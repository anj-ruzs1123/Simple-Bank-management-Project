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

    def deposit(self,deposit_amount:float) -> None:
        """
        Deposit function of the account.
        """
        if self.is_active:
            if deposit_amount > 0:
                self.__balance += deposit_amount
                self.__transactions.append(Transaction(TransactionType.DEPOSIT,deposit_amount,self.__balance,description="Deposit in account"))
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


a = Account("anuj",4554,42000)
b = Account("banuj",7879,45000)
print(a.balance,"\n",b.balance)
a.money_transfer(b,415)
print(a.balance,"\n",b.balance)
print(a)