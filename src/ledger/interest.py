"""Interest on savings balances.

Policy (docs/policy.md): simple daily interest on the closing balance, actual/365,
rounded to the cent, half up.
"""
from __future__ import annotations

from decimal import Decimal

from .money import Money


def monthly_interest(balance: Money, annual_rate_pct: float, days: int) -> Money:
    """Interest for `days` days at `annual_rate_pct` percent a year on `balance`."""
    interest = balance.amount * Decimal(str(annual_rate_pct)) / Decimal(100) * days / Decimal(365)
    return Money(interest, balance.currency)
