from decimal import Decimal

from ledger import monthly_interest


def test_thirty_days():
    assert monthly_interest(Decimal("1000.00"), 3.65, 30) == Decimal("3.00")


def test_zero_balance():
    assert monthly_interest(Decimal("0.00"), 7.0, 31) == Decimal("0.0")
