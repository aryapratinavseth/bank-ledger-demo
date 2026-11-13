from decimal import Decimal

import pytest

from ledger import FeeSchedule
from ledger.fees import InvalidFeeRule

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


def test_arithmetic_and_min_max_still_supported():
    fs = FeeSchedule("a: amount * 0.01 + 1\nb: min(amount * 0.02, 100)\nc: -amount + 2\n")
    assert fs.fee("a", Decimal("100")) == Decimal("2.00")
    assert fs.fee("b", Decimal("1000")) == Decimal("20.00")
    assert fs.fee("b", Decimal("100000")) == Decimal("100.00")
    assert fs.fee("c", Decimal("1")) == Decimal("1.00")


MALICIOUS_RULES = [
    # sandbox escape: eval's restricted globals are bypassed via dunders
    pytest.param("__import__('os').system('id')", id="dunder-import"),
    pytest.param("(1).__class__.__mro__", id="attribute-chain"),
    pytest.param("open('/etc/passwd').read()", id="builtin-open"),
    pytest.param("exec('import os')", id="exec"),
    pytest.param("eval('1+1')", id="nested-eval"),
    pytest.param("min.__globals__", id="builtin-globals"),
    pytest.param("lambda: 1", id="lambda"),
    pytest.param("[x for x in (1,)]", id="list-comp"),
    pytest.param("amount if amount else 0", id="conditional"),
    pytest.param("f'{amount}'", id="f-string"),
    pytest.param("'a' + 'b'", id="string-constant"),
    pytest.param("amount ** 2", id="power"),
    pytest.param("amount % 2", id="modulo"),
    pytest.param("min(amount, 5, key=abs)", id="keyword-args"),
    pytest.param("amount + 1/0", id="division-by-zero"),
]


@pytest.mark.parametrize("expr", MALICIOUS_RULES)
def test_malicious_rule_is_rejected(expr):
    with pytest.raises(InvalidFeeRule):
        FeeSchedule(f"evil: {expr}")


def test_sandbox_escape_cannot_run_code(tmp_path):
    # If the rule were executed, this file would exist.
    marker = tmp_path / "pwned"
    with pytest.raises(InvalidFeeRule):
        FeeSchedule(f"evil: __import__('os').system('touch {marker}')")
    assert not marker.exists()
