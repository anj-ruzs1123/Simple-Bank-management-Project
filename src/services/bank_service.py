import math
from typing  import Optional
from src.models import Account,SavingsAccount,CurrentAccount
from uuid import uuid4

class BankService:
    """
    Central banking service that manages customer accounts and transactions.
    """
    def __init__(self,bank_name:str) -> None:
        """
        Constructor for BankService Object.
        """
        self.bank_name = bank_name
        self.accounts:dict[str,Account] = {}

    @staticmethod
    def generate_acc_no() -> str:
        """
        Method for generating a randomized account number.
        """
        # Get 128-bit integer from UUID4 and convert to 10-digit number string
        raw_int = uuid4().int
        # Ensure first digit isn't 0 by forcing range 1000000000-9999999999
        bounded_id = (raw_int % (9 * 10**9)) + (10**9)
        return str(bounded_id)
        

    def open_account(self,account_type:str,name:str,initial_deposit:float = 0.0,**kwargs) -> str:
        """
        Method for opening a bank account.
        """
        acc_type = account_type.strip().lower()
        name = name.strip()
        if not name:
            raise ValueError("Account holder name cannot be empty.")
        acc_no = self.generate_acc_no()
        while acc_no in self.accounts:
            acc_no = self.generate_acc_no()

        interest_rate = kwargs.get("interest_rate",0.04)
        overdraft_limit = kwargs.get("overdraft_limit",1000)

        if acc_type == "savings":
            new_acc = SavingsAccount(name=name, acc_no=acc_no,balance=initial_deposit,interest_rate=interest_rate)
        elif acc_type == "current":
            new_acc = CurrentAccount(name=name, acc_no=acc_no,balance=initial_deposit,overdraft_limit=overdraft_limit)
        elif acc_type == "standard":
            new_acc = Account(name=name,acc_no=acc_no,balance=initial_deposit)
        else:
            raise ValueError("Account type must be 'standard', 'savings', or 'current'.")

        self.accounts[acc_no] = new_acc
        print(f"A new {acc_type.title()} account #{acc_no} is created.")
        return acc_no


    def get_account(self,acc_no:str) -> Optional[Account]:
        """
        Method for getting the account.
        """
        acc = self.accounts.get(acc_no)
        if not acc:
            print(f"Account #{acc_no} doesn't exist.")
        return acc

    def transfer(self,from_acc:str,to_acc:str,amount:float) -> bool:
        """
        Method for transferring the money from sender account to recipient account.
        """
        sender = self.get_account(from_acc)
        recipient = self.get_account(to_acc)

        if sender is None or recipient is None:
            return False
        if not sender.is_active or not recipient.is_active:
            return False
        if sender == recipient:
            return False
        if not math.isfinite(amount) or amount <= 0:
            return False
        return sender.money_transfer(recipient,amount)

    def close_account(self,acc_no:str) -> bool:
        """
        Removes the account from the account list.
        """
        acc = self.accounts.get(acc_no)
        if not acc: # checking if account exists or not
            return False
        # implementation of account closure
        if acc.balance > 0:
            print(f"Cannot close account: Please withdraw remaining balance of Rs.{acc.balance}.")
            return False
        elif acc.balance < 0:
            print(f"Cannot close account: Resolve the overdraft debt of Rs{acc.balance}.")
            return False
        else:
            del self.accounts[acc_no]
            print(f"Account #{acc_no} is closed.")
            return True

    def get_total_reserves(self) -> float:
        """
        Returns the total reserves of bank.
        """
        # Iterate to whole account list and add balance of each account
        # Then return it as a float value
        return sum((i.balance for i in self.accounts.values()))
        

    def list_all_accounts(self) -> list[Account]:
        """
        Lists all the available accounts in the bank.
        """
        if not self.accounts:
            print("No account in the list.")
            return []
        return list(self.accounts.values())

if __name__ == "__main__":
    bank = BankService("Python National Bank")
    print("\n--- 1. Opening Accounts ---")
    acc1 = bank.open_account("savings", "Anuj Jain", initial_deposit=10000, interest_rate=0.05)
    acc2 = bank.open_account("current", "Tech Corp", initial_deposit=5000, overdraft_limit=2000)
    print("\n--- 2. Total Reserves ---")
    print(f"Total Bank Reserves: Rs.{bank.get_total_reserves()}")
    print("\n--- 3. Transferring Money ---")
    bank.transfer(acc1, acc2, 2500)
    print("\n--- 4. Listing All Accounts ---")
    bank.list_all_accounts()
    print("\n--- 5. Attempting to Close Account with Balance ---")
    bank.close_account(acc1)