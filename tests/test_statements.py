from datetime import date
from decimal import Decimal

from ledger import Ledger, statement_lines
from ledger.money import Money


def test_statement_has_closing_balance():
    lg = Ledger()
    lg.open("A-1", "Asha")
    lg.deposit("A-1", Decimal("10"), date(2026, 11, 1))
    lines = statement_lines(lg.get("A-1"), date(2026, 11, 1), date(2026, 11, 30))
    assert lines[-1] == "Closing balance: 10.00"
    assert "deposit" in lines[1]


def test_statement_renders_money_amounts_right_aligned():
    lg = Ledger()
    lg.open("A-1", "Asha")
    lg.deposit("A-1", Money(Decimal("1234.50"), "INR"), date(2026, 11, 1))
    lines = statement_lines(lg.get("A-1"), date(2026, 11, 1), date(2026, 11, 30))
    assert lines[1] == f"{date(2026, 11, 1)}  {'1234.50':>12}  deposit"
    assert lines[-1] == "Closing balance: 1234.50"
