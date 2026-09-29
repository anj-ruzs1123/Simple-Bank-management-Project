import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from src.models import Account, CurrentAccount, SavingsAccount, Transaction, TransactionType
from src.repositories.postgres_bank_repository import PostgresBankRepository


class PostgresRepositoryMappingTests(unittest.TestCase):
    def test_database_row_maps_to_standard_account_without_synthetic_ledger(self) -> None:
        row = {
            "account_number": "1001",
            "holder_name": "Standard User",
            "account_type": "standard",
            "balance": Decimal("125.75"),
            "minimum_balance": Decimal("50.00"),
            "is_active": True,
            "is_closed": False,
            "interest_rate": None,
            "overdraft_limit": None,
        }

        account = PostgresBankRepository._account_from_row(row)

        self.assertIs(type(account), Account)
        self.assertEqual(account.balance, Decimal("125.75"))
        self.assertEqual(account.minimum_balance, Decimal("50.00"))
        self.assertEqual(account.statement, ())

    def test_database_row_maps_to_savings_account_settings(self) -> None:
        row = {
            "account_number": "2001",
            "holder_name": "Saver",
            "account_type": "savings",
            "balance": Decimal("900.00"),
            "minimum_balance": Decimal("500.00"),
            "is_active": False,
            "is_closed": False,
            "interest_rate": Decimal("0.045000"),
            "overdraft_limit": None,
        }

        account = PostgresBankRepository._account_from_row(row)

        self.assertIsInstance(account, SavingsAccount)
        assert isinstance(account,SavingsAccount)
        self.assertEqual(account.interest_rate, Decimal("0.045000"))
        self.assertFalse(account.is_active)

    def test_database_row_maps_current_account_with_negative_balance(self) -> None:
        row = {
            "account_number": "3001",
            "holder_name": "Business",
            "account_type": "current",
            "balance": Decimal("-25.00"),
            "minimum_balance": Decimal("0.00"),
            "is_active": True,
            "is_closed": False,
            "interest_rate": None,
            "overdraft_limit": Decimal("100.00"),
        }

        account = PostgresBankRepository._account_from_row(row)

        self.assertIsInstance(account, CurrentAccount)
        assert isinstance(account,CurrentAccount)
        self.assertEqual(account.balance, Decimal("-25.00"))
        self.assertEqual(account.overdraft_limit, Decimal("100.00"))

    def test_database_row_restores_original_transaction_id_and_timestamp(self) -> None:
        occurred_at = datetime(2026, 9, 28, 10, 30, tzinfo=timezone.utc)
        row = {
            "transaction_id": "test-transaction-id",
            "occurred_at": occurred_at,
            "transaction_type": "DEPOSIT",
            "amount": Decimal("10.25"),
            "balance_after": Decimal("20.50"),
            "description": "Test deposit",
        }

        transaction = PostgresBankRepository._transaction_from_row(row)

        self.assertEqual(transaction.transaction_id, "test-transaction-id")
        self.assertEqual(transaction.timestamp, occurred_at)
        self.assertEqual(transaction.amount, Decimal("10.25"))
        self.assertEqual(transaction.transactiontype, TransactionType.DEPOSIT)

    def test_schema_file_is_present(self) -> None:
        schema_path = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
        self.assertTrue(schema_path.is_file())


if __name__ == "__main__":
    unittest.main()
