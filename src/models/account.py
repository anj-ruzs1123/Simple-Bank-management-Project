from transaction import TransactionType,Transaction

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
        self.__balance = balance #Private attribute
        self.minimum_balance = min_bal
        self.__transactions = [] #private attribute
        if self.__balance > 0:
            self.__transactions.append(Transaction(TransactionType.DEPOSIT,self.__balance,self.__balance))
        
        self.is_active = True
        

    def __str__(self) -> str:
        return f"""Username = {self.name}\nAccount Number = {self.acc_no}\nBalance = {self.balance}\nTransaction history = {self.__transactions}"""

    @property
    def balance(self) -> float:
        """
        Function for getting value of balance.
        """
        return self.__balance   

    def deposit(self,deposit_amount:float,txn_type:TransactionType = TransactionType.DEPOSIT,description:str = "Deposit in account") -> None:
        """
        Deposit function of the account.
        """
        if self.is_active:
            if deposit_amount > 0:
                self.__balance += deposit_amount
                self.__transactions.append(Transaction(txn_type,deposit_amount,self.__balance,description=description))
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
                    self.__transactions.append(Transaction(TransactionType.WITHDRAWAL,withdraw_amount,self.__balance,description="Withdrawal from account"))
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
        return self.__transactions

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
        self.__balance -= transfer_amount
        other.__balance += transfer_amount
        self.__transactions.append(
            Transaction(
                TransactionType.TRANSFER_OUT,
                amount=transfer_amount,
                balance_after=self.__balance,
                description=f"Transfer to account {other.acc_no}",
            )
        )
        other.__transactions.append(
            Transaction(
                TransactionType.TRANSFER_IN,
                amount=transfer_amount,
                balance_after=other.__balance,
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


if __name__ == "__main__": 
    # a = Account("anuj",4554,42000)
    # b = Account("banuj",7879,45000)
    # print(a.balance,"\n",b.balance)
    # a.money_transfer(b,415)
    # print(a.balance,"\n",b.balance)
    # print(a)
    sa = SavingsAccount("Anuj", 9999, balance=10000, interest_rate=0.05)
    sa.apply_interest()
    print(sa)