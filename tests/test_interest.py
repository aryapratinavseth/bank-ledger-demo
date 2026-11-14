from decimal import Decimal

from ledger import monthly_interest
from ledger.money import Money


def test_thirty_days():
    assert monthly_interest(Money(Decimal("1000.00"), "INR"), 3.65, 30) == Money(Decimal("3.00"), "INR")


def test_zero_balance():
    assert monthly_interest(Money(Decimal("0.00"), "INR"), 7.0, 31) == Money(Decimal("0.00"), "INR")


def test_policy_example_rounds_half_up():
    # docs/policy.md: 2,675.00 at 3.65% for 10 days is 2.675, which rounds to 2.68.
    assert monthly_interest(Money(Decimal("2675.00"), "INR"), 3.65, 10) == Money(Decimal("2.68"), "INR")


def test_keeps_the_balance_currency():
    assert monthly_interest(Money(Decimal("1000.00"), "USD"), 3.65, 30).currency == "USD"
