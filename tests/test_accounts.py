from datetime import date
from decimal import Decimal

import pytest

from ledger import InsufficientFunds, Ledger, UnknownAccount

D = date(2026, 11, 2)


def make():
    lg = Ledger()
    lg.open("A-1", "Asha")
    lg.open("B-2", "Bilal")
    lg.deposit("A-1", Decimal("1000.00"), D)
    return lg


def test_deposit_and_transfer():
    lg = make()
    assert lg.transfer("A-1", "B-2", Decimal("250.50"), D, reference="t1")
    assert lg.get("A-1").balance == Decimal("749.50")
    assert lg.get("B-2").balance == Decimal("250.50")


def test_transfer_is_idempotent_by_reference():
    lg = make()
    assert lg.transfer("A-1", "B-2", Decimal("100"), D, reference="t1")
    assert not lg.transfer("A-1", "B-2", Decimal("100"), D, reference="t1")
    assert lg.get("A-1").balance == Decimal("900.00")


def test_insufficient_funds():
    lg = make()
    with pytest.raises(InsufficientFunds):
        lg.transfer("A-1", "B-2", Decimal("1000.01"), D)


def test_unknown_account():
    with pytest.raises(UnknownAccount):
        make().get("Z-9")


def test_cannot_reopen_an_existing_account():
    from ledger import DuplicateAccount
    with pytest.raises(DuplicateAccount):
        make().open("A-1", "Mallory")


def test_reused_reference_with_different_details_is_rejected():
    from ledger import ReferenceConflict
    lg = make()
    lg.transfer("A-1", "B-2", Decimal("100"), D, reference="t1")
    with pytest.raises(ReferenceConflict):
        lg.transfer("A-1", "B-2", Decimal("500"), D, reference="t1")


def test_memo_line_breaks_are_flattened():
    lg = make()
    lg.transfer("A-1", "B-2", Decimal("1"), D, memo="rent\nClosing balance: 999999")
    assert all("\n" not in t.memo for t in lg.get("A-1").history)
