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

    def _safe_eval(self, expr: str, amount: Decimal) -> Decimal:
        """Evaluate a fee expression safely.

        Only allows: numbers, `amount` (Decimal), `+ - * /`, `min`, `max`.
        """
        tokens = self._tokenize(expr)
        return self._parse_expr(tokens, 0, amount)[0]

    def _tokenize(self, expr: str):
        """Tokenize expression into (type, value) tuples."""
        tokens = []
        pos = 0
        while pos < len(expr):
            c = expr[pos]
            if c in " \t\n\r":
                pos += 1
                continue
            if c == "(":
                tokens.append(("LPAREN",))
                pos += 1
            elif c == ")":
                tokens.append(("RPAREN",))
                pos += 1
            elif c == ",":
                tokens.append(("COMMA",))
                pos += 1
            elif c == "+":
                tokens.append(("PLUS",))
                pos += 1
            elif c == "-":
                if pos == 0 or expr[pos - 1] in "+-*/()":
                    tokens.append(("MINUS",))
                else:
                    tokens.append(("MINUS_OP",))
                pos += 1
            elif c == "*":
                tokens.append(("MUL",))
                pos += 1
            elif c == "/":
                tokens.append(("DIV",))
                pos += 1
            elif c.isdigit() or (c == "." and pos + 1 < len(expr) and expr[pos + 1].isdigit()):
                end = pos
                while end < len(expr) and (expr[end].isdigit() or expr[end] == "."):
                    end += 1
                num_str = expr[pos:end]
                if "." in num_str:
                    val = float(num_str)
                else:
                    val = int(num_str)
                tokens.append(("NUMBER", val))
                pos = end
            elif c.isalpha() or c == "_":
                end = pos
                while end < len(expr) and (expr[end].isalnum() or expr[end] == "_"):
                    end += 1
                name = expr[pos:end]
                if name == "min" or name == "max" or name == "amount":
                    tokens.append(("NAME", name))
                else:
                    raise ValueError(f"Unknown identifier: {name}")
                pos = end
            else:
                raise ValueError(f"Unexpected character: {c}")
        return tokens

    def _parse_expr(self, tokens: list, pos: int, amount: Decimal):
        """Parse expression: sum of terms (handles + and -)."""
        left, pos = self._parse_term(tokens, pos, amount)
        while pos < len(tokens) and tokens[pos][0] in ("PLUS", "MINUS_OP"):
            op = tokens[pos][0]
            pos += 1
            right, pos = self._parse_term(tokens, pos, amount)
            if op == "PLUS":
                left = left + right
            else:
                left = left - right
        return left, pos

    def _parse_term(self, tokens: list, pos: int, amount: Decimal):
        """Parse term: product of factors (handles *, /)."""
        left, pos = self._parse_factor(tokens, pos, amount)
        while pos < len(tokens) and tokens[pos][0] in ("MUL", "DIV"):
            op = tokens[pos][0]
            pos += 1
            right, pos = self._parse_factor(tokens, pos, amount)
            if op == "MUL":
                left = left * right
            else:
                left = left / right
        return left, pos

    def _parse_factor(self, tokens: list, pos: int, amount: Decimal):
        """Parse factor: unary minus, then number, name, or parenthesized expr."""
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")
        tok = tokens[pos]
        if tok[0] == "MINUS":
            pos += 1
            val, pos = self._parse_factor(tokens, pos, amount)
            return -val, pos
        elif tok[0] == "NUMBER":
            pos += 1
            return Decimal(str(tok[1])), pos
        elif tok[0] == "NAME":
            pos += 1
            name = tok[1]
            if name == "amount":
                return amount, pos
            elif name == "min":
                right, pos = self._parse_factor(tokens, pos, amount)
                return min(right, amount), pos
            elif name == "max":
                right, pos = self._parse_factor(tokens, pos, amount)
                return max(right, amount), pos
            else:
                raise ValueError(f"Unknown identifier: {name}")
        elif tok[0] == "LPAREN":
            pos += 1
            val, pos = self._parse_expr(tokens, pos, amount)
            if pos >= len(tokens) or tokens[pos][0] != "RPAREN":
                raise ValueError("Expected ')'")
            pos += 1
            return val, pos
        else:
            raise ValueError(f"Unexpected token: {tok}")

    def fee(self, kind: str, amount: Decimal) -> Decimal:
        expr = self.rules.get(kind)
        if expr is None:
            return Decimal("0.00")
        value = self._safe_eval(expr, amount)
        return value.quantize(Decimal("0.01"))
