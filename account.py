class Account:
    """
    Blueprint of the bank account.
    """
    def __init__(self,name:str,acc_no:int,balance:int = 0, min_bal:int = 500) -> None:
        """
        Constructor for Account Class
        """
        self.name = name
        self.acc_no = acc_no
        self.__balance:int = balance
        self.minimun_balance = min_bal
        self.__transactions = []
        self.is_active = True

    def __str__(self) -> str:
            return f"""Username = {self.name}\nAccount Number = {self.acc_no}\nBalance = {self.get_balance}\nTransaction history = {self.__transactions}"""

    @property
    def get_balance(self):
        """
        Function for getting value of balance.
        """
        return self.__balance   

    def deposit(self,deposit_amount:int) -> None:
        """
        Deposit function of the account.
        """
        if self.is_active:
            if deposit_amount > 0:
                self.__balance += deposit_amount
                self.__transactions.append(f"Added {deposit_amount} to the account.")
            else:
                print("Deposit value should be positive")
        else:
            print("Account is not found to be active")

    def withdraw(self,withdraw_amount:int) -> None:
        """
        Withdraw function of account.
        """
        if self.is_active:
            if withdraw_amount > 0:
                if self.__balance > withdraw_amount + 500:
                    self.__balance -= withdraw_amount
                    self.__transactions.append(f"Dedeucted {withdraw_amount} from the account.")
                else:
                    print("Withdrawl exceeds minimum account balance of 500.")
            else:
                print("Withdrawl must be grater than zero.")
        else:
            print("Account is found to be frozen.")

    @property
    def get_statement(self):
        """
        For getting the list of trancactions.
        """
        return self.__transactions

    def freeze_account(self):
        """
        For Freezing the account.
        """
        self.is_active = False
    def activate_account(self):
        """
        For Activating the account.
        """
        self.is_active = True

    def money_transfer(self,other,transfer_amount):
        """
        Function for transferring money to other account.
        """
        if self.is_active and other.is_active:
            if self.__balance >= transfer_amount and self.__balance > self.minimun_balance:
                self.withdraw(transfer_amount)
                other.deposit(transfer_amount)
            else:
                print("Sender does not have sufficient funds.")
        else:
            print("Transaction failed due to the account being freezed")

