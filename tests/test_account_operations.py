import unittest
from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from main import main
from src.models import Account, CurrentAccount, SavingsAccount, TransactionType
from src.services.bank_service import BankService


class InMemoryBankRepository:
    def __init__(self) -> None:
        self.accounts: dict[str, Account] = {}

    def create_account(self, account: Account) -> None:
        self.accounts[account.acc_no] = account

    def get_account(self, account_number: str) -> Account | None:
        return self.accounts.get(account_number)

    def list_accounts(self) -> list[Account]:
        return list(self.accounts.values())

    def deposit(self, account_number: str, amount: Decimal) -> bool:
        return self.accounts[account_number].deposit(amount)

    def withdraw(self, account_number: str, amount: Decimal) -> bool:
        return self.accounts[account_number].withdraw(amount)

    def transfer(self, sender_number: str, recipient_number: str, amount: Decimal) -> bool:
        return self.accounts[sender_number].money_transfer(
            self.accounts[recipient_number],
            amount,
        )

    def apply_interest(self, account_number: str) -> Decimal:
        account = self.accounts[account_number]
        if isinstance(account, SavingsAccount):
            return account.apply_interest()
        return Decimal("0.00")

    def set_account_active(self, account_number: str, is_active: bool) -> bool:
        account = self.accounts.get(account_number)
        if account is None:
            return False
        account.is_active = is_active
        return True

    def close_account(self, account_number: str) -> bool:
        account = self.accounts.get(account_number)
        if account is None or account.balance != 0:
            return False
        account.is_active = False
        account.is_closed = True
        return True

    def get_total_reserves(self) -> Decimal:
        return sum(
            (account.balance for account in self.accounts.values() if not account.is_closed),
            Decimal("0.00"),
        )


class AccountOperationTests(unittest.TestCase):
    def test_zero_balance_account_construction_does_not_prompt(self) -> None:
        with patch("builtins.input", side_effect=AssertionError("unexpected input")):
            account = Account("Test User", "1001")

        self.assertEqual(account.balance, 0)

    def test_standard_transfer_records_one_transaction_per_account(self) -> None:
        sender = Account("Sender", "1001", balance=1000)
        recipient = Account("Recipient", "1002", balance=500)

        result = sender.money_transfer(recipient, 100)

        self.assertTrue(result)
        self.assertEqual(sender.balance, 900)
        self.assertEqual(recipient.balance, 600)
        self.assertEqual(len(sender.statement), 2)
        self.assertEqual(len(recipient.statement), 2)
        self.assertEqual(sender.statement[-1].transactiontype, TransactionType.TRANSFER_OUT)
        self.assertEqual(recipient.statement[-1].transactiontype, TransactionType.TRANSFER_IN)

    def test_current_account_transfer_obeys_overdraft_limit(self) -> None:
        sender = CurrentAccount(
            "Sender",
            "1001",
            balance=100,
            overdraft_limit=200,
        )
        recipient = Account("Recipient", "1002", balance=500)

        result = sender.money_transfer(recipient, 250)

        self.assertTrue(result)
        self.assertEqual(sender.balance, -150)
        self.assertEqual(recipient.balance, 750)
        self.assertEqual(len(sender.statement), 2)
        self.assertEqual(sender.statement[-1].transactiontype, TransactionType.TRANSFER_OUT)

    def test_current_withdraw_reports_success_and_failure(self) -> None:
        account = CurrentAccount("Company", "2001", balance=100, overdraft_limit=50)

        self.assertTrue(account.withdraw(125))
        self.assertEqual(account.balance, -25)
        self.assertFalse(account.withdraw(30))
        self.assertEqual(account.balance, -25)

    def test_failed_transfer_does_not_change_either_balance(self) -> None:
        sender = Account("Sender", "1001", balance=600)
        recipient = Account("Recipient", "1002", balance=500)

        self.assertFalse(sender.money_transfer(recipient, 200))
        self.assertEqual(sender.balance, 600)
        self.assertEqual(recipient.balance, 500)

    def test_non_finite_amounts_are_rejected(self) -> None:
        account = Account("Test User", "1001", balance=600)
        self.assertFalse(account.deposit(float("nan")))
        self.assertFalse(account.withdraw(float("inf")))
        with self.assertRaises(ValueError):
            account.set_balance(float("nan"))

    def test_set_balance_respects_account_floor(self) -> None:
        standard = Account("Test User", "1001", balance=600, min_bal=500)
        current = CurrentAccount("Company", "2001", balance=0, overdraft_limit=100)

        with self.assertRaises(ValueError):
            standard.set_balance(499)
        with self.assertRaises(ValueError):
            current.set_balance(-101)

    def test_interest_credits_once(self) -> None:
        account = SavingsAccount(
            "Saver",
            "3001",
            balance=1000,
            interest_rate=0.05,
        )

        self.assertEqual(account.apply_interest(), 50)
        self.assertEqual(account.balance, 1050)
        self.assertEqual(len(account.statement), 2)
        self.assertEqual(account.statement[-1].transactiontype, TransactionType.INTEREST)

    def test_cli_opens_zero_balance_account_and_exits(self) -> None:
        inputs = iter(["1", "standard", "CLI User", "0", "9"])
        output = StringIO()
        repository = InMemoryBankRepository()

        with (
            patch("builtins.input", side_effect=lambda _: next(inputs)),
            patch(
                "main.BankService",
                side_effect=lambda bank_name: BankService(bank_name, repository),
            ),
            patch.object(BankService, "generate_acc_no", return_value="1001"),
            redirect_stdout(output),
        ):
            main()

        self.assertIn("Your account number is 1001.", output.getvalue())
        self.assertIn("Goodbye.", output.getvalue())


if __name__ == "__main__":
    unittest.main()