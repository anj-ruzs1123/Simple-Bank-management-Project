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
        self.__balance = balance
        self.minimum_balance = min_bal
        self.__transactions = [f"Initial balance = {self.__balance}"]
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
                self.__transactions.append(f"Added {deposit_amount} to the account.")
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
                    self.__transactions.append(f"Deducted {withdraw_amount} from the account.")
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

        self.withdraw(transfer_amount)
        other.deposit(transfer_amount)
        