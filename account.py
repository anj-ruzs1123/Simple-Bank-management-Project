class Account:
    """Blueprint of the bank account."""
    def __init__(self,name:str,acc_no:int) -> None:
        """Constructor for Account Class"""
        self.name = name
        self.acc_no = acc_no
        self.__balance:int = 0

    def get_balance(self):
        """Function for getting value of balance."""
        return self.__balance   

    def set_balance(self,new_balance:int):
        """Function to set the value of balance"""
        self.__balance = new_balance

a = Account(name="Anuj",acc_no=48423)
a.set_balance(525)
print(a.get_balance())