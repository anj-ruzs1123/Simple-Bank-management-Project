from decimal import Decimal
from typing import Optional
from uuid import uuid4

from src.models import Account, CurrentAccount, SavingsAccount
from src.models.money import MoneyInput, to_money
from src.repositories import PostgresBankRepository


class BankService:
    """Coordinates banking operations through a persistent repository."""

    def __init__(
        self,
        bank_name: str,
        repository: PostgresBankRepository | None = None,
    ) -> None:
        self.bank_name = bank_name
        self.repository = repository or PostgresBankRepository()

    @staticmethod
    def generate_acc_no() -> str:
        """Generate a 10-digit account number."""
        raw_int = uuid4().int
        bounded_id = (raw_int % (9 * 10**9)) + (10**9)
        return str(bounded_id)

    def open_account(
        self,
        account_type: str,
        name: str,
        initial_deposit: MoneyInput = Decimal("0.00"),
        **kwargs: MoneyInput,
    ) -> str:
        account_type = account_type.strip().lower()
        name = name.strip()
        if not name:
            raise ValueError("Account holder name cannot be empty.")

        if account_type not in {"standard", "savings", "current"}:
            raise ValueError("Account type must be 'standard', 'savings', or 'current'.")

        account_number = self.generate_acc_no()
        while self.repository.get_account(account_number) is not None:
            account_number = self.generate_acc_no()

        if account_type == "savings":
            account: Account = SavingsAccount(
                name=name,
                acc_no=account_number,
                balance=initial_deposit,
                interest_rate=kwargs.get("interest_rate", Decimal("0.04")),
            )
        elif account_type == "current":
            account = CurrentAccount(
                name=name,
                acc_no=account_number,
                balance=initial_deposit,
                overdraft_limit=kwargs.get("overdraft_limit", Decimal("1000.00")),
            )
        else:
            account = Account(
                name=name,
                acc_no=account_number,
                balance=initial_deposit,
            )

        self.repository.create_account(account)
        print(f"A new {account_type.title()} account #{account_number} is created.")
        return account_number

    def get_account(self, account_number: str) -> Optional[Account]:
        account = self.repository.get_account(account_number)
        if account is None:
            print(f"Account #{account_number} doesn't exist.")
        return account

    def deposit(self, account_number: str, amount: MoneyInput) -> bool:
        return self._valid_money(amount) and self.repository.deposit(
            account_number,
            to_money(amount),
        )

    def withdraw(self, account_number: str, amount: MoneyInput) -> bool:
        return self._valid_money(amount) and self.repository.withdraw(
            account_number,
            to_money(amount),
        )

    def transfer(
        self,
        from_account_number: str,
        to_account_number: str,
        amount: MoneyInput,
    ) -> bool:
        if not self._valid_money(amount):
            return False
        return self.repository.transfer(
            from_account_number,
            to_account_number,
            to_money(amount),
        )

    def apply_interest(self, account_number: str) -> Decimal:
        return self.repository.apply_interest(account_number)

    def set_account_active(self, account_number: str, is_active: bool) -> bool:
        return self.repository.set_account_active(account_number, is_active)

    def close_account(self, account_number: str) -> bool:
        account = self.get_account(account_number)
        if account is None:
            return False
        if account.balance != Decimal("0.00"):
            print("Cannot close account: balance must be zero.")
            return False
        return self.repository.close_account(account_number)

    def get_total_reserves(self) -> Decimal:
        return self.repository.get_total_reserves()

    def list_all_accounts(self) -> list[Account]:
        return self.repository.list_accounts()

    @staticmethod
    def _valid_money(amount: MoneyInput) -> bool:
        try:
            return to_money(amount) > 0
        except ValueError:
            return False


if __name__ == "__main__":
    bank = BankService("Python National Bank")
    print("\n--- 1. Opening Accounts ---")
    account_one = bank.open_account("savings", "Anuj Jain", initial_deposit=10000)
    account_two = bank.open_account("current", "Tech Corp", initial_deposit=5000)
    print("\n--- 2. Total Reserves ---")
    print(f"Total Bank Reserves: Rs.{bank.get_total_reserves()}")
    print("\n--- 3. Transferring Money ---")
    bank.transfer(account_one, account_two, 2500)
    print("\n--- 4. Listing All Accounts ---")
    for account in bank.list_all_accounts():
        print(account)
