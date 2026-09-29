from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


PAISE = Decimal("0.01")
MoneyInput = Decimal | float | int | str


def to_money(value: MoneyInput) -> Decimal:
    """Convert a monetary value to a finite Decimal rounded to paise."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("Money value must be a valid decimal number.") from error
    if not amount.is_finite():
        raise ValueError("Money value must be finite.")
    try:
        return amount.quantize(PAISE, rounding=ROUND_HALF_UP)
    except InvalidOperation as error:
        raise ValueError("Money value exceeds supported decimal precision.") from error


def to_rate(value: MoneyInput) -> Decimal:
    """Convert an interest rate to a finite Decimal without currency rounding."""
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("Interest rate must be a valid decimal number.") from error
    if not rate.is_finite():
        raise ValueError("Interest rate must be finite.")
    return rate
