"""Accounts and transfers. Money is held as Decimal, two places, in the account's currency."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

CENT = Decimal("0.01")


class UnknownAccount(KeyError):
    pass


class InsufficientFunds(ValueError):
    pass


class DuplicateAccount(ValueError):
    pass


class ReferenceConflict(ValueError):
    """A transfer reference was reused with different details."""


@dataclass
class Transaction:
    day: date
    amount: Decimal          # positive = credit, negative = debit
    memo: str
    reference: str | None = None


@dataclass
class Account:
    number: str
    owner: str
    currency: str = "INR"
    balance: Decimal = Decimal("0.00")
    history: list[Transaction] = field(default_factory=list)

    def post(self, day: date, amount: Decimal, memo: str, reference: str | None = None) -> None:
        amount = Decimal(amount).quantize(CENT)
        memo = " ".join(memo.split())  # no line breaks or control whitespace in statements
        self.balance += amount
        self.history.append(Transaction(day, amount, memo, reference))


class Ledger:
    def __init__(self) -> None:
        self.accounts: dict[str, Account] = {}
        self._seen_references: dict[str, tuple[str, str, Decimal]] = {}

    def open(self, number: str, owner: str, currency: str = "INR") -> Account:
        number, owner, currency = (" ".join(str(s).split()) for s in (number, owner, currency))
        if number in self.accounts:
            raise DuplicateAccount(number)
        acct = Account(number, owner, currency)
        self.accounts[number] = acct
        return acct

    def get(self, number: str) -> Account:
        try:
            return self.accounts[number]
        except KeyError:
            raise UnknownAccount(number) from None

    def deposit(self, number: str, amount: Decimal, day: date, memo: str = "deposit") -> None:
        if Decimal(amount) <= 0:
            raise ValueError("deposit must be positive")
        self.get(number).post(day, Decimal(amount), memo)

    def transfer(self, src: str, dst: str, amount: Decimal, day: date,
                 reference: str | None = None, memo: str = "transfer") -> bool:
        """Move money between two accounts in the same currency.

        A retry with a reference that was already processed for the same source, destination and
        amount is ignored and returns False (idempotent retries); the same reference with different
        details raises ReferenceConflict. Returns True when money moved.
        """
        amount = Decimal(amount).quantize(CENT)
        if amount <= 0:
            raise ValueError("transfer must be positive")
        if reference is not None and reference in self._seen_references:
            if self._seen_references[reference] != (src, dst, amount):
                raise ReferenceConflict(reference)
            return False
        a, b = self.get(src), self.get(dst)
        if a.currency != b.currency:
            raise ValueError("cross-currency transfers are not supported")
        if a.balance < amount:
            raise InsufficientFunds(f"{src} has {a.balance}, needs {amount}")
        a.post(day, -amount, f"{memo} to {dst}", reference)
        b.post(day, amount, f"{memo} from {src}", reference)
        if reference is not None:
            self._seen_references[reference] = (src, dst, amount)
        return True
