"""Plain-text account statements."""
from __future__ import annotations

from datetime import date

from .accounts import Account


def statement_lines(acct: Account, start: date, end: date) -> list[str]:
    lines = [f"Statement for {acct.number} ({acct.owner}), {start} to {end}, {acct.currency}"]
    for t in acct.history:
        if start <= t.day <= end:
            lines.append(f"{t.day}  {t.amount:>12}  {t.memo}")
    lines.append(f"Closing balance: {acct.balance}")
    return lines
