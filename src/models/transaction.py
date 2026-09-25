from enum import Enum
import uuid
from datetime import datetime
from dataclasses import dataclass,field

class TransactionType(str,Enum):
    """
    Enumeration of possible transaction categories
    """
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    INTEREST = "INTEREST"

@dataclass(frozen=True)
class Transaction:
    """Represents a single immutable financial transaction record."""

    transactiontype: TransactionType
    amount: float
    balance_after: float
    description: str = ""

    # We keep init=False so Python knows they aren't arguments in the type hints,
    # but we will assign them manually inside our custom __init__.
    transaction_id: str = field(init=False)
    timestamp: str = field(init=False)

    def __init__(self, transactiontype: TransactionType, amount: float, balance_after: float, description: str = "") -> None:
        """Custom constructor for frozen dataclass."""
        # Standard assignments will fail, so we must use object.__setattr__
        object.__setattr__(self, 'transactiontype', transactiontype)
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'balance_after', balance_after)
        object.__setattr__(self, 'description', description)

        # Generate the dynamic values and assign them safely
        object.__setattr__(self, 'transaction_id', uuid.uuid4().hex[:12])
        object.__setattr__(self, 'timestamp', datetime.now().strftime("%d/%m/%y %H:%M:%S"))

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (
            f"Timestamp : {self.timestamp}\n"
            f"Transaction_ID : {self.transaction_id}\n"
            f"Type : {self.transactiontype.value}\n"
            f"Amount : {self.amount}\n"
            f"Balance : {self.balance_after}\n"
            f"Description : {self.description}"
        )

    def __repr__(self) -> str:
        """
        Used for returning list of strings
        """
        return self.__str__()
