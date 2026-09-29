from __future__ import annotations
from dotenv import load_dotenv
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable,cast,LiteralString

import psycopg
from psycopg.rows import DictRow, dict_row
from psycopg import sql

from src.models import Account, CurrentAccount, SavingsAccount, Transaction, TransactionType

dict_row_factory = cast(Any, dict_row)

class PostgresBankRepository:
    """PostgreSQL storage for bank accounts and their transaction ledgers."""

    def __init__(self, connection_string: str | None = None) -> None:
        """Create the repository with an optional PostgreSQL connection string."""
        self._connection_string = connection_string

    def _connect(self) -> psycopg.Connection[DictRow]:
        """Open a PostgreSQL connection using the configured settings."""
        load_dotenv()
        if self._connection_string:
            return cast(
                psycopg.Connection[DictRow],
                psycopg.connect(self._connection_string, row_factory=dict_row_factory)
            )
            

        required = ("PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD")
        missing = [key for key in required if not os.environ.get(key)]
        if missing:
            raise RuntimeError(
                "PostgreSQL connection is not configured. Set "
                + ", ".join(missing)
                + " or pass a connection string."
            )

        return cast(
            psycopg.Connection[DictRow],
            psycopg.connect(
            host=os.environ["PGHOST"],
            port=os.environ.get("PGPORT", "5432"),
            dbname=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            row_factory=dict_row_factory,
        )
        )

    def check_connection(self) -> bool:
        """Return True if PostgreSQL is reachable."""
        with self._connect() as connection:
            row = connection.execute("SELECT 1 AS connected").fetchone()
        return row is not None and row["connected"] == 1

    def initialize_schema(self) -> None:
        """Apply the database schema from the project SQL file."""
        schema_path = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"
        schema_sql = schema_path.read_text(encoding="utf-8")
        with self._connect() as connection:
            connection.execute(sql.SQL(cast(LiteralString,schema_sql)),prepare=False)

    def create_account(self, account: Account) -> None:
        """Insert a new account and its current statement."""
        account_type, interest_rate, overdraft_limit = self._account_details(account)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO accounts (
                    account_number, holder_name, account_type, balance,
                    minimum_balance, is_active, is_closed, interest_rate, overdraft_limit
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    account.acc_no,
                    account.name,
                    account_type,
                    account.balance,
                    account.minimum_balance,
                    account.is_active,
                    account.is_closed,
                    interest_rate,
                    overdraft_limit,
                ),
            )
            self._insert_transactions(connection, account)

    def save_account(self, account: Account) -> None:
        """Update an existing account and save any new transactions."""
        account_type, interest_rate, overdraft_limit = self._account_details(account)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE accounts
                SET holder_name = %s,
                    account_type = %s,
                    balance = %s,
                    minimum_balance = %s,
                    is_active = %s,
                    is_closed = %s,
                    interest_rate = %s,
                    overdraft_limit = %s
                WHERE account_number = %s
                """,
                (
                    account.name,
                    account_type,
                    account.balance,
                    account.minimum_balance,
                    account.is_active,
                    account.is_closed,
                    interest_rate,
                    overdraft_limit,
                    account.acc_no,
                ),
            )
            if cursor.rowcount != 1:
                raise LookupError(f"Account {account.acc_no} does not exist.")
            self._insert_transactions(connection, account)

    def get_account(self, account_number: str) -> Account | None:
        """Return an account by number or None if it is missing."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE account_number = %s AND is_closed = FALSE",
                (account_number,),
            ).fetchone()
            if row is None:
                return None
            transaction_rows = connection.execute(
                """
                SELECT transaction_id, occurred_at, transaction_type,
                       amount, balance_after, description
                FROM transactions
                WHERE account_number = %s
                ORDER BY occurred_at, transaction_id
                """,
                (account_number,),
            ).fetchall()

        account = self._account_from_row(row)
        account._transactions = [self._transaction_from_row(tx) for tx in transaction_rows]
        return account

    def list_accounts(self) -> list[Account]:
        """Return all active accounts with their transactions."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM accounts
                WHERE is_closed = FALSE
                ORDER BY created_at, account_number
                """
            ).fetchall()
            account_numbers = [row["account_number"] for row in rows]
            transaction_rows = []
            if account_numbers:
                transaction_rows = connection.execute(
                    """
                    SELECT account_number, transaction_id, occurred_at,
                           transaction_type, amount, balance_after, description
                    FROM transactions
                    WHERE account_number = ANY(%s)
                    ORDER BY account_number, occurred_at, transaction_id
                    """,
                    (account_numbers,),
                ).fetchall()

        transactions_by_account: dict[str, list[Transaction]] = {}
        for row in transaction_rows:
            transactions_by_account.setdefault(row["account_number"], []).append(
                self._transaction_from_row(row)
            )

        accounts: list[Account] = []
        for row in rows:
            account = self._account_from_row(row)
            account._transactions = transactions_by_account.get(account.acc_no, [])
            accounts.append(account)
        return accounts

    def transfer(self, sender_number: str, recipient_number: str, amount: Decimal) -> bool:
        """Move money between two accounts if the transfer is valid."""
        if sender_number == recipient_number or not amount.is_finite() or amount <= 0:
            return False

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM accounts
                WHERE account_number = ANY(%s)
                ORDER BY account_number
                FOR UPDATE
                """,
                ([sender_number, recipient_number],),
            ).fetchall()
            accounts_by_number = {row["account_number"]: row for row in rows}
            sender_row = accounts_by_number.get(sender_number)
            recipient_row = accounts_by_number.get(recipient_number)
            if sender_row is None or recipient_row is None:
                return False

            sender = self._account_from_row(sender_row)
            recipient = self._account_from_row(recipient_row)
            sender._transactions = []
            recipient._transactions = []
            if not sender.money_transfer(recipient, amount):
                return False

            for account in (sender, recipient):
                connection.execute(
                    "UPDATE accounts SET balance = %s WHERE account_number = %s",
                    (account.balance, account.acc_no),
                )
                self._insert_transactions(connection, account)
        return True

    def deposit(self, account_number: str, amount: Decimal) -> bool:
        """Deposit money into an account."""
        return self._mutate_account(
            account_number,
            lambda account: account.deposit(amount),
        ) is True

    def withdraw(self, account_number: str, amount: Decimal) -> bool:
        """Withdraw money from an account."""
        return self._mutate_account(
            account_number,
            lambda account: account.withdraw(amount),
        ) is True

    def apply_interest(self, account_number: str) -> Decimal:
        """Apply interest to a savings account and return the earned amount."""
        result = self._mutate_account(
            account_number,
            lambda account: account.apply_interest()
            if isinstance(account, SavingsAccount)
            else Decimal("0.00"),
        )
        return result if isinstance(result, Decimal) else Decimal("0.00")

    def set_account_active(self, account_number: str, is_active: bool) -> bool:
        """Enable or disable an active account."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE accounts
                SET is_active = %s
                WHERE account_number = %s AND is_closed = FALSE
                """,
                (is_active, account_number),
            )
        return cursor.rowcount == 1

    def close_account(self, account_number: str) -> bool:
        """Close an account if it has a zero balance."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE accounts
                SET is_active = FALSE, is_closed = TRUE
                WHERE account_number = %s
                    AND balance = 0
                    AND is_closed = FALSE
                """,
                (account_number,),
            )
        return cursor.rowcount == 1

    def get_total_reserves(self) -> Decimal:
        """Return the total balance of all open accounts."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(SUM(balance), 0)::NUMERIC(18, 2) AS reserves
                FROM accounts
                WHERE is_closed = FALSE
                """
            ).fetchone()
        if row is None:
            raise RuntimeError("This reserves query has no result.")
        return Decimal(row["reserves"])

    def _mutate_account(
        self,
        account_number: str,
        operation: Callable[[Account], bool | Decimal],
    ) -> bool | Decimal:
        """Apply an account mutation and persist the updated balance."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM accounts
                WHERE account_number = %s AND is_closed = FALSE
                FOR UPDATE
                """,
                (account_number,),
            ).fetchone()
            if row is None:
                return False

            account = self._account_from_row(row)
            result = operation(account)
            succeeded = result if isinstance(result, bool) else result > 0
            if not succeeded:
                return result

            connection.execute(
                """
                UPDATE accounts
                SET balance = %s, is_active = %s
                WHERE account_number = %s
                """,
                (account.balance, account.is_active, account_number),
            )
            self._insert_transactions(connection, account)
            return result

    @staticmethod
    def _account_details(
        account: Account,
    ) -> tuple[str, Decimal | None, Decimal | None]:
        """Return the database column values for the account type."""
        if isinstance(account, SavingsAccount):
            return "savings", account.interest_rate, None
        if isinstance(account, CurrentAccount):
            return "current", None, account.overdraft_limit
        if type(account) is Account:
            return "standard", None, None
        raise TypeError(f"Unsupported account class: {type(account).__name__}")

    @staticmethod
    def _insert_transactions(connection: Any, account: Account) -> None:
        """Save all account transactions to the transaction ledger."""
        for transaction in account.statement:
            connection.execute(
                """
                INSERT INTO transactions (
                    transaction_id, account_number, occurred_at,
                    transaction_type, amount, balance_after, description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
                """,
                (
                    transaction.transaction_id,
                    account.acc_no,
                    transaction.timestamp,
                    transaction.transactiontype.value,
                    transaction.amount,
                    transaction.balance_after,
                    transaction.description,
                ),
            )

    @staticmethod
    def _account_from_row(row: dict[str, Any]) -> Account:
        """Build an Account object from a database row."""
        account_type = row["account_type"]
        common = {
            "name": row["holder_name"],
            "acc_no": row["account_number"],
            "balance": Decimal(row["balance"]),
            "min_bal": Decimal(row["minimum_balance"]),
        }
        stored_balance = common["balance"]
        if account_type == "savings":
            account = SavingsAccount(
                **common,
                interest_rate=Decimal(row["interest_rate"]),
            )
        elif account_type == "current":
            common["balance"] = max(stored_balance, Decimal("0.00"))
            account = CurrentAccount(
                **common,
                overdraft_limit=Decimal(row["overdraft_limit"]),
            )
            account._balance = stored_balance
        elif account_type == "standard":
            account = Account(**common)
        else:
            raise ValueError(f"Unsupported account type in database: {account_type}")

        account.is_active = row["is_active"]
        account.is_closed = row["is_closed"]
        account._transactions = []
        return account

    @staticmethod
    def _transaction_from_row(row: dict[str, Any]) -> Transaction:
        """Build a Transaction object from a database row."""
        occurred_at = row["occurred_at"]
        if not isinstance(occurred_at, datetime):
            raise TypeError("Database transaction timestamp must be a datetime.")
        return Transaction(
            transactiontype=TransactionType(row["transaction_type"]),
            amount=Decimal(row["amount"]),
            balance_after=Decimal(row["balance_after"]),
            description=row["description"],
            transaction_id=row["transaction_id"],
            timestamp=occurred_at,
        )
