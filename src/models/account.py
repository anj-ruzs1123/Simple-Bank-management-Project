from decimal import Decimal

from src.models.transaction import TransactionType,Transaction
from src.models.money import MoneyInput, to_money, to_rate

class Account:
    """
    Blueprint of the bank account.
    """
    def __init__(
        self,
        name: str,
        acc_no: str,
        balance: MoneyInput = Decimal("0.00"),
        min_bal: MoneyInput = Decimal("500.00"),
    ) -> None:
        """
        Constructor for Account Class
        """
        self.name = name
        self.acc_no = acc_no
        minimum_balance = to_money(min_bal)
        opening_balance = to_money(balance)
        if minimum_balance < 0:
            raise ValueError("Minimum balance must be non-negative.")
        if opening_balance < 0:
            raise ValueError("Opening balance must be non-negative.")

        self.minimum_balance = minimum_balance
        self._balance = opening_balance

        self._transactions = [] #private attribute
        if self._balance > 0:
            self._transactions.append(Transaction(TransactionType.DEPOSIT,self._balance,self._balance))
        
        self.is_active = True
        self.is_closed = False
        

    def __str__(self) -> str:
        return f"""Username = {self.name.title()}\nAccount Number = {self.acc_no}\nBalance = {self.balance}\nTransaction history = {self._transactions}"""

    @property
    def balance(self) -> Decimal:
        """
        Function for getting value of balance.
        """
        return self._balance   

    @property
    def _balance_floor(self) -> Decimal:
        return self.minimum_balance

    def set_balance(self, new_amount: MoneyInput) -> None:
        """Set a valid balance; normal transactions should use deposit or withdraw."""
        balance = to_money(new_amount)
        if balance < self._balance_floor:
            raise ValueError(f"Balance cannot be lower than {self._balance_floor}.")
        self._balance = balance

    def deposit(
        self,
        deposit_amount: MoneyInput,
        txn_type: TransactionType = TransactionType.DEPOSIT,
        description: str = "Deposit in account",
    ) -> bool:
        """
        Deposit function of the account.
        """
        if self.is_active and not self.is_closed:
            try:
                amount = to_money(deposit_amount)
                new_balance = to_money(self.balance + amount)
            except (ValueError, ArithmeticError):
                print("Deposit amount must be a finite monetary value.")
                return False
            if amount > 0:
                try:
                    self.set_balance(new_balance)
                except ValueError:
                    print("Deposit would exceed the maximum supported balance.")
                    return False
                self._transactions.append(
                    Transaction(txn_type, amount, self._balance, description=description)
                )
                return True
            else:
                print("Deposit value should be positive")
        else:
            print("Account is not active")
        return False

    def withdraw(
        self,
        withdraw_amount: MoneyInput,
        txn_type: TransactionType = TransactionType.WITHDRAWAL,
        description: str = "Withdrawal from account",
    ) -> bool:
        """
        Withdraw function of account.
        """
        if self.is_active and not self.is_closed:
            try:
                amount = to_money(withdraw_amount)
            except ValueError:
                print("Withdrawal amount must be a finite monetary value.")
                return False
            if amount > 0:
                if self.balance >= amount + self.minimum_balance:
                    self.set_balance(self.balance - amount)
                    self._transactions.append(
                        Transaction(txn_type, amount, self._balance, description=description)
                    )
                    return True
                else:
                    print(f"Withdrawal exceeds minimum account balance of {self.minimum_balance}.")
            else:
                print("Withdrawal must be greater than zero.")
        else:
            print("Account is frozen.")
        return False

    @property
    def statement(self) -> tuple[Transaction, ...]:
        """
        For getting the list of tranactions.
        """
        return tuple(self._transactions)

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

    def money_transfer(self, other: "Account", transfer_amount: MoneyInput) -> bool:
        """
        Function for transferring money to other account.
        """
        if not isinstance(other, Account):
            raise TypeError("Recipient must be an Account.")
        if self.acc_no == other.acc_no:
            print("Cannot self transfer.")
            return False
        
        if not self.is_active or not other.is_active or self.is_closed or other.is_closed:
            print("Transaction can't be completed because of frozen account.")
            return False

        try:
            amount = to_money(transfer_amount)
        except ValueError:
            print("Transfer amount must be a finite monetary value.")
            return False
        if amount <= 0:
            print("Transfer amount must be greater than zero.")
            return False

        if not self.withdraw(
            amount,
            txn_type=TransactionType.TRANSFER_OUT,
            description=f"Transfer to account {other.acc_no}",
        ):
            return False
        if not other.deposit(
            amount,
            txn_type=TransactionType.TRANSFER_IN,
            description=f"Transfer from account {self.acc_no}",
        ):
            self.deposit(
                transfer_amount,
                description=f"Reversal of failed transfer to account {other.acc_no}",
            )
            return False
        return True

class SavingsAccount(Account):
    """
    Specialized Account that provides interest on it's balance.
    """
    def __init__(
        self,
        name: str,
        acc_no: str,
        balance: MoneyInput = Decimal("0.00"),
        min_bal: MoneyInput = Decimal("500.00"),
        interest_rate: MoneyInput = Decimal("0.04"),
    ) -> None:
        """
        Constructor for SavingsAccount.
        Calls the parent constructor using super() and initialized interest_rate.
        """
        super().__init__(name, acc_no, balance, min_bal)
        self.interest_rate = to_rate(interest_rate)
        if self.interest_rate < 0:
            raise ValueError("Interest rate must be non-negative.")

    def apply_interest(self):
        """
        Calculates interest earned on current blance and deposits it into the account.
        Returns the interest amount added.
        """
        if not self.is_active:
            print("Cannot apply interest: Account is frozen.")
            return Decimal("0.00")
        if self.balance <= 0:
            print("Cannot apply interest: Balance must be positive.")
            return Decimal("0.00")
        interest = to_money(self.balance * self.interest_rate)

        if interest > 0:
            if not self.deposit(
                interest,
                txn_type=TransactionType.INTEREST,
                description=f"Interest credited @{self.interest_rate * 100}%."
            ):
                return Decimal("0.00")
            print(f"Applied interest of {interest} at rate of {self.interest_rate * 100}%.")
            return interest
        return Decimal("0.00")

    def __str__(self) -> str:
        """
        Overrides the parent __str__ to append the interest rate.
        """
        base_info = super().__str__()
        return f"{base_info}\nAccount Type : Savings\nInterest Rate : {self.interest_rate * 100}%"

class CurrentAccount(Account):
    def __init__(
            self,
            name: str, 
            acc_no: str, 
            balance: MoneyInput = Decimal("0.00"),
            min_bal: MoneyInput = Decimal("0.00"),
            overdraft_limit: MoneyInput = Decimal("1000.00")
        )-> None:
        overdraft = to_money(overdraft_limit)
        if overdraft < 0:
            raise ValueError("Overdraft limit must be non-negative.")
        super().__init__(name, acc_no, balance, min_bal)
        self.overdraft_limit = overdraft

    @property
    def _balance_floor(self) -> Decimal:
        return -self.overdraft_limit

    def withdraw(
        self,
        withdraw_amount: MoneyInput,
        txn_type: TransactionType = TransactionType.WITHDRAWAL,
        description: str = "Withdrawal successful.",
    ) -> bool:
        if not self.is_active:
            print("Account is frozen.")
            return False
        try:
            amount = to_money(withdraw_amount)
        except ValueError:
            print("Withdrawal amount must be a finite monetary value.")
            return False
        if amount > 0:
            if self.balance - amount >= (-self.overdraft_limit):
                self.set_balance(self.balance - amount)
                self._transactions.append(
                    Transaction(
                        txn_type,
                        amount=amount,
                        balance_after=self.balance,
                        description=description,
                    )
                )
                return True
            else:
                print("Withdrawal amount exceeds overdraft limit.")
        else:
            print("Withdrawal amount must be greater than 0.")
        return False

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base}\nAccount Type: Current\nOverdraft Limit : Rs.{self.overdraft_limit}."
        

if __name__ == "__main__": 
    ca = CurrentAccount("Anuj Corp", "8888", balance=500.0, overdraft_limit=1000.0)
    print(ca)
    print("\n--- Withdrawing 1200 (Overdraft) ---")
    ca.withdraw(1200)
    print(f"Current Balance: {ca.balance}")  # Should be -700.0!
    print("\n--- Withdrawing another 400 (Should fail: limit exceeded) ---")
    ca.withdraw(400)