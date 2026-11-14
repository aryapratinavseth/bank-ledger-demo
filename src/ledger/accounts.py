"""Accounts and transfers. Money is held as Money (Decimal, two places) in the account's currency."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from .money import CurrencyMismatch, Money, as_money


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
    amount: Money          # positive = credit, negative = debit
    memo: str
    reference: str | None = None


@dataclass
class Account:
    number: str
    owner: str
    currency: str = "INR"
    balance: Money = field(default_factory=lambda: Money(Decimal("0.00"), "INR"))
    history: list[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        # A fresh account always starts at zero in its own currency.
        self.balance = Money(Decimal("0.00"), self.currency)

    def post(self, day: date, amount: Money, memo: str, reference: str | None = None) -> None:
        if amount.currency != self.currency:
            raise CurrencyMismatch(f"cannot post {amount.currency} to a {self.currency} account")
        memo = " ".join(memo.split())  # no line breaks or control whitespace in statements
        self.balance += amount
        self.history.append(Transaction(day, amount, memo, reference))


class Ledger:
    def __init__(self) -> None:
        self.accounts: dict[str, Account] = {}
        self._seen_references: dict[str, tuple[str, str, Money]] = {}

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

    def deposit(self, number: str, amount: Money | Decimal, day: date, memo: str = "deposit") -> None:
        acct = self.get(number)
        money = as_money(amount, acct.currency)
        if money <= Money(Decimal("0.00"), acct.currency):
            raise ValueError("deposit must be positive")
        acct.post(day, money, memo)

    def transfer(self, src: str, dst: str, amount: Money | Decimal, day: date,
                 reference: str | None = None, memo: str = "transfer") -> bool:
        """Move money between two accounts in the same currency.

        A retry with a reference that was already processed for the same source, destination and
        amount is ignored and returns False (idempotent retries); the same reference with different
        details raises ReferenceConflict. Returns True when money moved.
        """
        a, b = self.get(src), self.get(dst)
        if a.currency != b.currency:
            raise ValueError("cross-currency transfers are not supported")
        money = as_money(amount, a.currency)
        if money <= Money(Decimal("0.00"), a.currency):
            raise ValueError("transfer must be positive")
        if reference is not None and reference in self._seen_references:
            if self._seen_references[reference] != (src, dst, money):
                raise ReferenceConflict(reference)
            return False
        if a.balance < money:
            raise InsufficientFunds(f"{src} has {a.balance}, needs {money}")
        a.post(day, -money, f"{memo} to {dst}", reference)
        b.post(day, money, f"{memo} from {src}", reference)
        if reference is not None:
            self._seen_references[reference] = (src, dst, money)
        return True
