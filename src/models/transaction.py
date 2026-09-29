from enum import Enum
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from decimal import Decimal

from src.models.money import MoneyInput, to_money

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
    amount: Decimal
    balance_after: Decimal
    description: str = ""

    transaction_id: str = field(init=False)
    timestamp: datetime = field(init=False)

    def __init__(
        self,
        transactiontype: TransactionType,
        amount: MoneyInput,
        balance_after: MoneyInput,
        description: str = "",
        *,
        transaction_id: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        object.__setattr__(self, 'transactiontype', transactiontype)
        object.__setattr__(self, 'amount', to_money(amount))
        object.__setattr__(self, 'balance_after', to_money(balance_after))
        object.__setattr__(self, 'description', description)
        object.__setattr__(self, 'transaction_id', transaction_id or uuid.uuid4().hex[:12])
        object.__setattr__(
            self,
            'timestamp',
            timestamp or datetime.now(timezone.utc),
        )

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (
            f"Timestamp : {self.timestamp.strftime('%d/%m/%y %H:%M:%S %Z')}\n"
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
