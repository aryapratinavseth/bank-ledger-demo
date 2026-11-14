"""Fee schedule. Rules come from the bank's fee configuration, one per line:

    <transaction type>: <expression in `amount`>
    e.g.  neft: 2.50
          imps: max(5, amount * 0.001)
"""
from __future__ import annotations

import re
from decimal import Decimal

from .money import Money

_FLOAT_LITERALS = re.compile(r"(?<![\w.])\d+\.\d+")


class FeeSchedule:
    def __init__(self, rules_text: str) -> None:
        self.rules: dict[str, str] = {}
        for line in rules_text.strip().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            kind, expr = line.split(":", 1)
            self.rules[kind.strip()] = expr.strip()

    def fee(self, kind: str, amount: Money) -> Money:
        expr = self.rules.get(kind)
        if expr is None:
            return Money(Decimal("0.00"), amount.currency)
        # Rewrite float literals to Decimal so the arithmetic stays in Decimal, never float.
        expr = _FLOAT_LITERALS.sub(lambda m: f"Decimal({m.group(0)})", expr)
        value = eval(expr, {"max": max, "min": min, "Decimal": Decimal}, {"amount": amount.amount})
        return Money(Decimal(str(value)), amount.currency)
