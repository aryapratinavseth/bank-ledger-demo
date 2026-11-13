"""Fee schedule. Rules come from the bank's fee configuration, one per line:

    <transaction type>: <expression in `amount`>
    e.g.  neft: 2.50
          imps: max(5, amount * 0.001)

Policy (docs/policy.md §5): rules are simple arithmetic in `amount` — numbers,
`+ - * /`, `min`, `max`. Configuration is data, not code, so expressions are
parsed and evaluated with a restricted AST walker rather than `eval`.
"""
from __future__ import annotations

import ast
from decimal import Decimal


class InvalidFeeRule(ValueError):
    """A fee rule expression is not simple arithmetic in `amount`."""


def _eval_node(node: ast.AST, amount: float) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, amount)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        raise InvalidFeeRule("only numeric constants are allowed")
    if isinstance(node, ast.Name):
        if node.id == "amount":
            return amount
        raise InvalidFeeRule(f"unknown name {node.id!r}")
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        left = _eval_node(node.left, amount)
        right = _eval_node(node.right, amount)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if right == 0:
            raise InvalidFeeRule("division by zero in fee rule")
        return left / right
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_node(node.operand, amount)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in ("min", "max") or node.keywords:
            raise InvalidFeeRule("only min(...) and max(...) calls are allowed")
        values = [_eval_node(arg, amount) for arg in node.args]
        return (min if node.func.id == "min" else max)(values)
    raise InvalidFeeRule(f"disallowed expression element: {type(node).__name__}")


class FeeSchedule:
    def __init__(self, rules_text: str) -> None:
        self.rules: dict[str, str] = {}
        for line in rules_text.strip().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            kind, expr = line.split(":", 1)
            self._validate(expr)
            self.rules[kind.strip()] = expr.strip()

    @staticmethod
    def _validate(expr: str) -> None:
        try:
            tree = ast.parse(expr.strip(), mode="eval")
        except SyntaxError as e:
            raise InvalidFeeRule(f"invalid fee rule expression: {expr!r}") from e
        _eval_node(tree, 0.0)  # parse-check: rejects any disallowed element

    def fee(self, kind: str, amount: Decimal) -> Decimal:
        expr = self.rules.get(kind)
        if expr is None:
            return Decimal("0.00")
        value = _eval_node(ast.parse(expr, mode="eval"), float(amount))
        return Decimal(str(value)).quantize(Decimal("0.01"))
