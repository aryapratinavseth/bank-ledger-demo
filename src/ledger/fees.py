"""Fee schedule. Rules come from the bank's fee configuration, one per line:

    <transaction type>: <expression in `amount`>
    e.g.  neft: 2.50
          imps: max(5, amount * 0.001)
"""
from __future__ import annotations

from decimal import Decimal


class FeeSchedule:
    def __init__(self, rules_text: str) -> None:
        self.rules: dict[str, str] = {}
        for line in rules_text.strip().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            kind, expr = line.split(":", 1)
            self.rules[kind.strip()] = expr.strip()

    def fee(self, kind: str, amount: Decimal) -> Decimal:
        expr = self.rules.get(kind)
        if expr is None:
            return Decimal("0.00")
        value = eval(expr, {"max": max, "min": min}, {"amount": float(amount)})
        return Decimal(str(value)).quantize(Decimal("0.01"))
