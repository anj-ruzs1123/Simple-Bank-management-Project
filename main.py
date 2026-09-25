import math

from src.models import Account, SavingsAccount
from src.services.bank_service import BankService


def _read_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")
            continue
        if not math.isfinite(value):
            print("Please enter a finite number.")
            continue
        return value


def _read_account(bank: BankService, prompt: str) -> Account | None:
    account_number = input(prompt).strip()
    if not account_number:
        print("Account number cannot be empty.")
        return None
    return bank.get_account(account_number)


def _open_account(bank: BankService) -> None:
    account_type = input("Account type (standard/savings/current): ").strip().lower()
    name = input("Account holder name: ").strip()
    initial_deposit = _read_float("Initial deposit (enter 0 for no opening deposit): Rs.")
    options: dict[str, float] = {}

    if account_type == "savings":
        options["interest_rate"] = _read_float(
            "Annual interest rate (e.g. 0.04 for 4%): "
        )
    elif account_type == "current":
        options["overdraft_limit"] = _read_float("Overdraft limit: Rs.")

    try:
        account_number = bank.open_account(
            account_type,
            name,
            initial_deposit=initial_deposit,
            **options,
        )
    except ValueError as error:
        print(f"Could not open account: {error}")
        return
    print(f"Your account number is {account_number}.")


def _deposit(bank: BankService) -> None:
    account = _read_account(bank, "Account number: ")
    if account is None:
        return
    amount = _read_float("Deposit amount: Rs.")
    if account.deposit(amount):
        print(f"Deposit successful. New balance: Rs.{account.balance:.2f}")


def _withdraw(bank: BankService) -> None:
    account = _read_account(bank, "Account number: ")
    if account is None:
        return
    amount = _read_float("Withdrawal amount: Rs.")
    if account.withdraw(amount):
        print(f"Withdrawal successful. New balance: Rs.{account.balance:.2f}")


def _transfer(bank: BankService) -> None:
    sender_number = input("From account number: ").strip()
    recipient_number = input("To account number: ").strip()
    amount = _read_float("Transfer amount: Rs.")
    if bank.transfer(sender_number, recipient_number, amount):
        print("Transfer successful.")
    else:
        print("Transfer failed.")


def _show_account(bank: BankService) -> None:
    account = _read_account(bank, "Account number: ")
    if account is None:
        return
    print(f"\n{account}\n")
    print("Transaction statement:")
    if not account.statement:
        print("No transactions recorded.")
        return
    for transaction in account.statement:
        print("-" * 40)
        print(transaction)


def _apply_interest(bank: BankService) -> None:
    account = _read_account(bank, "Savings account number: ")
    if account is None:
        return
    if not isinstance(account, SavingsAccount):
        print("Interest can only be applied to a savings account.")
        return
    interest = account.apply_interest()
    if interest > 0:
        print(f"Interest credited: Rs.{interest:.2f}")


def _toggle_account_status(bank: BankService) -> None:
    account = _read_account(bank, "Account number: ")
    if account is None:
        return
    if account.is_active:
        account.freeze_account()
        print("Account frozen.")
    else:
        account.activate_account()
        print("Account activated.")


def _show_bank_summary(bank: BankService) -> None:
    print(f"Total bank reserves: Rs.{bank.get_total_reserves():.2f}")
    accounts = bank.list_all_accounts()
    for account in accounts:
        print("-" * 40)
        print(account)


def main() -> None:
    bank = BankService("Python National Bank")
    actions = {
        "1": lambda: _open_account(bank),
        "2": lambda: _deposit(bank),
        "3": lambda: _withdraw(bank),
        "4": lambda: _transfer(bank),
        "5": lambda: _show_account(bank),
        "6": lambda: _apply_interest(bank),
        "7": lambda: _toggle_account_status(bank),
        "8": lambda: _show_bank_summary(bank),
    }

    while True:
        print(f"\n=== {bank.bank_name} ===")
        print(
            "1. Open account\n"
            "2. Deposit\n"
            "3. Withdraw\n"
            "4. Transfer\n"
            "5. View balance and statement\n"
            "6. Apply savings interest\n"
            "7. Freeze/reactivate account\n"
            "8. Bank summary\n"
            "9. Exit"
        )
        try:
            choice = input("Select an option: ").strip()
            if choice == "9":
                print("Goodbye.")
                return
            action = actions.get(choice)
            if action is None:
                print("Choose an option from 1 to 9.")
                continue
            action()
        except EOFError:
            print("\nInput ended. Goodbye.")
            return


if __name__ == "__main__":
    main()
