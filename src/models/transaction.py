from enum import Enum
import uuid
from datetime import datetime

class TransactionType(str,Enum):
    """
    Enumeration of possible transaction categories
    """
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    INTEREST = "INTEREST"

class Transaction:
    """
    Represents a single immutable financial transaction record.
    """
    def __init__(self,transactiontype:TransactionType,amount:float,balance_after:float,description:str = "") -> None:
        """
        Constructor for Transaction class
        """
        self.trasanction_id = uuid.uuid4().hex[:12]
        self.timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        self.transactiontype = transactiontype
        self.amount = amount
        self.balance_after = balance_after
        self.description = description #Optional addition for different cases

    def __str__(self) ->str:
        """
        Return a string when we print Transaction object
        """
        s =  f"Timestamp : {self.timestamp}\nTransaction_ID : {self.trasanction_id}\n{self.transactiontype.value}\nAmount : {self.amount}\nBalance : {self.balance_after}\n{self.description}"
        return s

    def __repr__(self) -> str:
        """
        Used for returning list of strings
        """
        return self.__str__()
