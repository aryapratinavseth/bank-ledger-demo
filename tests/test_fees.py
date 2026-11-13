from decimal import Decimal

from ledger import FeeSchedule

RULES = """
# type: expression in amount
neft: 2.50
imps: max(5, amount * 0.001)
"""


def test_flat_fee():
    assert FeeSchedule(RULES).fee("neft", Decimal("100")) == Decimal("2.50")


def test_percentage_fee_with_floor():
    fs = FeeSchedule(RULES)
    assert fs.fee("imps", Decimal("1000")) == Decimal("5.00")
    assert fs.fee("imps", Decimal("20000")) == Decimal("20.00")


def test_unknown_kind_is_free():
    assert FeeSchedule(RULES).fee("rtgs", Decimal("5")) == Decimal("0.00")
