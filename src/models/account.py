import math

from src.models.transaction import TransactionType,Transaction

class Account:
    """
    Blueprint of the bank account.
    """
    def __init__(self,name:str,acc_no:str,balance:float = 0, min_bal:float = 500) -> None:
        """
        Constructor for Account Class
        """
        self.name = name
        self.acc_no = acc_no
        if not math.isfinite(min_bal) or min_bal < 0:
            raise ValueError("Minimum balance must be a finite, non-negative amount.")
        if not math.isfinite(balance) or balance < 0:
            raise ValueError("Opening balance must be a finite, non-negative amount.")

        self.minimum_balance = min_bal
        self._balance = balance

        self._transactions = [] #private attribute
        if self._balance > 0:
            self._transactions.append(Transaction(TransactionType.DEPOSIT,self._balance,self._balance))
        
        self.is_active = True
        

    def __str__(self) -> str:
        return f"""Username = {self.name.title()}\nAccount Number = {self.acc_no}\nBalance = {self.balance}\nTransaction history = {self._transactions}"""

    @property
    def balance(self) -> float:
        """
        Function for getting value of balance.
        """
        return self._balance   

    @property
    def _balance_floor(self) -> float:
        return self.minimum_balance

    def set_balance(self, new_amount: float) -> None:
        """Set a valid balance; normal transactions should use deposit or withdraw."""
        if not math.isfinite(new_amount):
            raise ValueError("Balance must be a finite amount.")
        if new_amount < self._balance_floor:
            raise ValueError(f"Balance cannot be lower than {self._balance_floor}.")
        self._balance = new_amount

    def deposit(self,deposit_amount:float,txn_type:TransactionType = TransactionType.DEPOSIT,description:str = "Deposit in account") -> bool:
        """
        Deposit function of the account.
        """
        if self.is_active:
            if math.isfinite(deposit_amount) and deposit_amount > 0:
                new_balance = self.balance + deposit_amount
                if not math.isfinite(new_balance):
                    print("Deposit would exceed the maximum supported balance.")
                    return False
                self.set_balance(new_balance)
                self._transactions.append(Transaction(txn_type,deposit_amount,self._balance,description=description))
                return True
            else:
                print("Deposit value should be positive")
        else:
            print("Account is not active")
        return False

    def withdraw(self,withdraw_amount:float,txn_type:TransactionType = TransactionType.WITHDRAWAL,description:str = "Withdrawal from account") -> bool:
        """
        Withdraw function of account.
        """
        if self.is_active:
            if math.isfinite(withdraw_amount) and withdraw_amount > 0:
                if self.balance >= withdraw_amount + self.minimum_balance:
                    self.set_balance(self.balance - withdraw_amount)
                    self._transactions.append(Transaction(txn_type,withdraw_amount,self._balance,description=description))
                    return True
                else:
                    print(f"Withdrawal exceeds minimum account balance of {self.minimum_balance}.")
            else:
                print("Withdrawal must be greater than zero.")
        else:
            print("Account is frozen.")
        return False

    @property
    def statement(self) -> tuple[Transaction, ...]:
        """
        For getting the list of tranactions.
        """
        return tuple(self._transactions)

    def freeze_account(self) -> None:
        """
        For Freezing the account.
        """
        self.is_active = False

    def activate_account(self)-> None:
        """
        For Activating the account.
        """
        self.is_active = True

    def money_transfer(self, other: "Account", transfer_amount: float) -> bool:
        """
        Function for transferring money to other account.
        """
        if not isinstance(other, Account):
            raise TypeError("Recipient must be an Account.")
        if self.acc_no == other.acc_no:
            print("Cannot self transfer.")
            return False
        
        if not self.is_active or not other.is_active:
            print("Transaction can't be completed because of frozen account.")
            return False

        if not math.isfinite(transfer_amount) or transfer_amount <= 0:
            print("Transfer amount must be greater than zero.")
            return False

        if not math.isfinite(other.balance + transfer_amount):
            print("Transfer would exceed the recipient's maximum supported balance.")
            return False

        if not self.withdraw(
            transfer_amount,
            txn_type=TransactionType.TRANSFER_OUT,
            description=f"Transfer to account {other.acc_no}",
        ):
            return False
        if not other.deposit(
            transfer_amount,
            txn_type=TransactionType.TRANSFER_IN,
            description=f"Transfer from account {self.acc_no}",
        ):
            self.deposit(
                transfer_amount,
                description=f"Reversal of failed transfer to account {other.acc_no}",
            )
            return False
        return True

class SavingsAccount(Account):
    """
    Specialized Account that provides interest on it's balance.
    """
    def __init__(self, name: str, acc_no: str, balance: float = 0, min_bal: float = 500,interest_rate:float = 0.04) -> None:
        """
        Constructor for SavingsAccount.
        Calls the parent constructor using super() and initialized interest_rate.
        """
        super().__init__(name, acc_no, balance, min_bal)
        if not math.isfinite(interest_rate) or interest_rate < 0:
            raise ValueError("Interest rate must be a finite, non-negative value.")
        self.interest_rate = interest_rate

    def apply_interest(self):
        """
        Calculates interest earned on current blance and deposits it into the account.
        Returns the interest amount added.
        """
        if not self.is_active:
            print("Cannot apply interest: Account is frozen.")
            return 0.0
        if self.balance <= 0:
            print("Cannot apply interest: Balance must be positive.")
            return 0.0
        # Calculate interest
        interest = round(self.balance * self.interest_rate,2)

        if interest > 0:
            if not self.deposit(
                interest,
                txn_type=TransactionType.INTEREST,
                description=f"Interest credited @{self.interest_rate * 100}%."
            ):
                return 0.0
            print(f"Applied interest of {interest} at rate of {self.interest_rate * 100}%.")
            return interest
        return 0.0

    def __str__(self) -> str:
        """
        Overrides the parent __str__ to append the interest rate.
        """
        base_info = super().__str__()
        return f"{base_info}\nAccount Type : Savings\nInterest Rate : {self.interest_rate * 100}%"

class CurrentAccount(Account):
    def __init__(
            self,
            name: str, 
            acc_no: str, 
            balance: float = 0.0, 
            min_bal: float = 0.0,
            overdraft_limit:float = 1000.0
        )-> None:
        if not math.isfinite(overdraft_limit) or overdraft_limit < 0:
            raise ValueError("Overdraft limit must be a finite, non-negative amount.")
        super().__init__(name, acc_no, balance, min_bal)
        self.overdraft_limit = overdraft_limit

    @property
    def _balance_floor(self) -> float:
        return -self.overdraft_limit

    def withdraw(
        self,
        withdraw_amount: float,
        txn_type: TransactionType = TransactionType.WITHDRAWAL,
        description: str = "Withdrawal successful.",
    ) -> bool:
        if not self.is_active:
            print("Account is frozen.")
            return False
        if math.isfinite(withdraw_amount) and withdraw_amount > 0:
            if self.balance - withdraw_amount >= (-self.overdraft_limit):
                self.set_balance(self.balance - withdraw_amount)
                self._transactions.append(
                    Transaction(
                        txn_type,
                        amount=withdraw_amount,
                        balance_after=self.balance,
                        description=description,
                    )
                )
                return True
            else:
                print("Withdrawal amount exceeds overdraft limit.")
        else:
            print("Withdrawal amount must be greater than 0.")
        return False

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base}\nAccount Type: Current\nOverdraft Limit : Rs.{self.overdraft_limit}."
        

if __name__ == "__main__": 
    ca = CurrentAccount("Anuj Corp", "8888", balance=500.0, overdraft_limit=1000.0)
    print(ca)
    print("\n--- Withdrawing 1200 (Overdraft) ---")
    ca.withdraw(1200)
    print(f"Current Balance: {ca.balance}")  # Should be -700.0!
    print("\n--- Withdrawing another 400 (Should fail: limit exceeded) ---")
    ca.withdraw(400)