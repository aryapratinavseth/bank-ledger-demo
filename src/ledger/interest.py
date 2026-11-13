"""Interest on savings balances.

Policy (docs/policy.md): simple daily interest on the closing balance, actual/365,
rounded to the cent, half up.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def monthly_interest(balance: Decimal, annual_rate_pct: Decimal, days: int) -> Decimal:
    """Interest for `days` days at `annual_rate_pct` percent a year on `balance`."""
    rate = annual_rate_pct / Decimal(100)
    interest = balance * rate * Decimal(days) / Decimal(365)
    return interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
