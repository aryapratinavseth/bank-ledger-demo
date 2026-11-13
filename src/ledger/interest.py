"""Interest on savings balances.

Policy (docs/policy.md): simple daily interest on the closing balance, actual/365,
rounded to the cent, half up.
"""
from __future__ import annotations

from decimal import Decimal


def monthly_interest(balance: Decimal, annual_rate_pct: float, days: int) -> Decimal:
    """Interest for `days` days at `annual_rate_pct` percent a year on `balance`."""
    interest = float(balance) * annual_rate_pct / 100 * days / 365
    return Decimal(str(round(interest, 2)))
