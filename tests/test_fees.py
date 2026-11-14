from decimal import Decimal

from ledger import FeeSchedule
from ledger.money import Money

RULES = """
# type: expression in amount
neft: 2.50
imps: max(5, amount * 0.001)
"""


def test_flat_fee():
    assert FeeSchedule(RULES).fee("neft", Money(Decimal("100"), "INR")) == Money(Decimal("2.50"), "INR")


def test_percentage_fee_with_floor():
    fs = FeeSchedule(RULES)
    assert fs.fee("imps", Money(Decimal("1000"), "INR")) == Money(Decimal("5.00"), "INR")
    assert fs.fee("imps", Money(Decimal("20000"), "INR")) == Money(Decimal("20.00"), "INR")


def test_unknown_kind_is_free():
    assert FeeSchedule(RULES).fee("rtgs", Money(Decimal("5"), "INR")) == Money(Decimal("0.00"), "INR")


def test_fee_keeps_the_amount_currency():
    assert FeeSchedule(RULES).fee("neft", Money(Decimal("100"), "USD")).currency == "USD"
