from src.models.transaction import TransactionType,Transaction

class Account:
    """
    Blueprint of the bank account.
    """
    def __init__(self,name:str,acc_no:float,balance:float = 0, min_bal:float = 500) -> None:
        """
        Constructor for Account Class
        """
        self.name = name
        self.acc_no = acc_no
        self._balance = balance #Private attribute
        self.minimum_balance = min_bal
        self._transactions = [] #private attribute
        if self._balance > 0:
            self._transactions.append(Transaction(TransactionType.DEPOSIT,self._balance,self._balance))
        
        self.is_active = True
        

    def __str__(self) -> str:
        return f"""Username = {self.name}\nAccount Number = {self.acc_no}\nBalance = {self.balance}\nTransaction history = {self._transactions}"""

    @property
    def balance(self) -> float:
        """
        Function for getting value of balance.
        """
        return self._balance   

    def deposit(self,deposit_amount:float,txn_type:TransactionType = TransactionType.DEPOSIT,description:str = "Deposit in account") -> None:
        """
        Deposit function of the account.
        """
        if self.is_active:
            if deposit_amount > 0:
                self.__balance += deposit_amount
                self._transactions.append(Transaction(txn_type,deposit_amount,self._balance,description=description))
            else:
                print("Deposit value should be positive")
        else:
            print("Account is not found to be active")

    def withdraw(self,withdraw_amount:float) -> None:
        """
        Withdraw function of account.
        """
        if self.is_active:
            if withdraw_amount > 0:
                if self.__balance >= withdraw_amount + self.minimum_balance:
                    self.__balance -= withdraw_amount
                    self._transactions.append(Transaction(TransactionType.WITHDRAWAL,withdraw_amount,self._balance,description="Withdrawal from account"))
                else:
                    print("Withdrawl exceeds minimum account balance of 500.")
            else:
                print("Withdrawl must be greater than zero.")
        else:
            print("Account is found to be frozen.")

    @property
    def statement(self) -> list[str]:
        """
        For getting the list of tranactions.
        """
        return self._transactions

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

    def money_transfer(self,other,transfer_amount:float) -> None:
        """
        Function for transferring money to other account.
        """
        if self.acc_no == other.acc_no:
            print("Cannot self transfer.")
            return
        
        if not self.is_active or not other.is_active:
            print("Transaction can't be completed because of frozen account.")
            return

        if transfer_amount <= 0:
            print("Transfer amount must be greater than zero.")
            return

        if self.__balance < transfer_amount + self.minimum_balance:
            print("Transfer failed: Insufficient funds to maintain minimum balance.")
            return

        # Complete the transfer atomically and record both sides as transactions.
        self._balance -= transfer_amount
        other._balance += transfer_amount
        self._transactions.append(
            Transaction(
                TransactionType.TRANSFER_OUT,
                amount=transfer_amount,
                balance_after=self._balance,
                description=f"Transfer to account {other.acc_no}",
            )
        )
        other.__transactions.append(
            Transaction(
                TransactionType.TRANSFER_IN,
                amount=transfer_amount,
                balance_after=other._balance,
                description=f"Transfer from account {self.acc_no}",
            )
        )

class SavingsAccount(Account):
    """
    Specialized Account that provides interest on it's balance.
    """
    def __init__(self, name: str, acc_no: float, balance: float = 0, min_bal: float = 500,interest_rate:float = 0.04) -> None:
        """
        Constructor for SavingsAccount.
        Calls the parent constructor using super() and initialized interest_rate.
        """
        super().__init__(name, acc_no, balance, min_bal)
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
            self.deposit(
                interest,
                txn_type=TransactionType.INTEREST,
                description=f"Interest credited @{self.interest_rate * 100}%."
                )
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
            acc_no: float, 
            balance: float = 0.0, 
            min_bal: float = 0.0,
            overdraft_limit:float = 1000.0
        )-> None:
        super().__init__(name, acc_no, balance, min_bal)
        self.overdraft_limit = overdraft_limit

    def withdraw(self,withdraw_amount:float) -> None:
        if not self.is_active:
            print("Account is frozen.")
            return
        if withdraw_amount > 0:
            if self.balance - withdraw_amount >= (-self.overdraft_limit):
                self._balance -= withdraw_amount
                self._transactions.append(Transaction(TransactionType.WITHDRAWAL,amount=withdraw_amount,balance_after=self.balance,description="Withdrawal successful."))
            else:
                print("Withdrawal amount exceeds overdraft limit.")
        else:
            print("Withdrawal amount must be greater than 0.")

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base}\nAccount Type: Current\nOverdraft Limit : Rs.{self.overdraft_limit}."
        

if __name__ == "__main__": 
    ca = CurrentAccount("Anuj Corp", 8888, balance=500.0, overdraft_limit=1000.0)
    print(ca)
    print("\n--- Withdrawing 1200 (Overdraft) ---")
    ca.withdraw(1200)
    print(f"Current Balance: {ca.balance}")  # Should be -700.0!
    print("\n--- Withdrawing another 400 (Should fail: limit exceeded) ---")
    ca.withdraw(400)