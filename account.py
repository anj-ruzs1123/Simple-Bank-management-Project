class Account:
    """
    Blueprint of the bank account.
    """
    def __init__(self,name:str,acc_no:int) -> None:
        """
        Constructor for Account Class
        """
        self.name = name
        self.acc_no = acc_no
        self.__balance:int = 0

    def get_balance(self):
        """
        Function for getting value of balance.
        """
        return self.__balance   

    def deposit(self,deposit_amount:int) -> None:
        """
        Deposit function of the account.
        """
        if deposit_amount > 0:
            self.__balance += deposit_amount
        else:
            print("Deposit value should be positive")

    def withdraw(self,withdraw_amount:int) -> None:
        """
        Withdraw function of account.
        """
        if withdraw_amount > 0:
            if self.__balance > withdraw_amount + 500:
                self.__balance -= withdraw_amount
        else:
            print("Withdrawl cannot be positive")

