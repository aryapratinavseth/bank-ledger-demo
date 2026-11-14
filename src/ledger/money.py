"""Money: an immutable amount in a currency, held to the cent.

Policy (docs/policy.md): amounts are held to two decimal places in the
account's currency; money is Decimal, never float.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
DEFAULT_CURRENCY = "INR"


class CurrencyMismatch(ValueError):
    """Two amounts in different currencies cannot be combined."""


def _to_decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    raise TypeError(f"cannot make a Money amount from {type(value).__name__}")


@dataclass(frozen=True)
class Money:
    """An immutable amount of money in a currency, rounded to the cent."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", _to_decimal(self.amount).quantize(CENT, rounding=ROUND_HALF_UP))
        object.__setattr__(self, "currency", " ".join(str(self.currency).split()))

    @classmethod
    def from_decimal(cls, value: Decimal | int | str, currency: str = DEFAULT_CURRENCY) -> "Money":
        return cls(_to_decimal(value), currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def _combine(self, other: object, op) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot combine {self.currency} with {other.currency}")
        return Money(op(self.amount, other.amount), self.currency)

    def __add__(self, other: object) -> "Money":
        return self._combine(other, lambda a, b: a + b)

    def __sub__(self, other: object) -> "Money":
        return self._combine(other, lambda a, b: a - b)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.currency == other.currency and self.amount == other.amount

    def __lt__(self, other: "Money") -> bool:
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot compare {self.currency} with {other.currency}")
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot compare {self.currency} with {other.currency}")
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot compare {self.currency} with {other.currency}")
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot compare {self.currency} with {other.currency}")
        return self.amount >= other.amount

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        return str(self.amount)

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"


def as_money(value: object, currency: str = DEFAULT_CURRENCY) -> Money:
    """Coerce a Money / Decimal / int / str into Money in `currency`."""
    if isinstance(value, Money):
        return value
    return Money.from_decimal(value, currency)
