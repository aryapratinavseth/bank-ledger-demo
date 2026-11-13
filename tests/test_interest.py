from decimal import Decimal

from ledger import monthly_interest


def test_thirty_days():
    assert monthly_interest(Decimal("1000.00"), 3.65, 30) == Decimal("3.00")


def test_zero_balance():
    assert monthly_interest(Decimal("0.00"), 7.0, 31) == Decimal("0.0")


def test_rounds_half_up_not_half_even():
    # Issue #1: 2675.00 at 3.65% for 10 days is exactly 2.675, which
    # must round half up to 2.68 (docs/policy.md §2), not 2.67.
    assert monthly_interest(Decimal("2675.00"), 3.65, 10) == Decimal("2.68")
