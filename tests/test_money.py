from decimal import Decimal

import pytest

from ledger.money import CurrencyMismatch, Money, as_money


def test_holds_two_decimal_places():
    m = Money(Decimal("10"), "INR")
    assert m.amount == Decimal("10.00")
    assert m.currency == "INR"


def test_rounds_half_up_to_the_cent():
    assert Money(Decimal("1.005"), "INR").amount == Decimal("1.01")
    assert Money(Decimal("1.004"), "INR").amount == Decimal("1.00")


def test_from_decimal_accepts_decimal_int_and_str():
    assert Money.from_decimal(Decimal("10.5"), "USD") == Money(Decimal("10.50"), "USD")
    assert Money.from_decimal(10, "USD") == Money(Decimal("10.00"), "USD")
    assert Money.from_decimal("10.25", "USD") == Money(Decimal("10.25"), "USD")


def test_addition_and_subtraction_in_same_currency():
    a = Money(Decimal("10.00"), "INR")
    b = Money(Decimal("2.50"), "INR")
    assert a + b == Money(Decimal("12.50"), "INR")
    assert a - b == Money(Decimal("7.50"), "INR")


def test_cross_currency_combination_is_rejected():
    a = Money(Decimal("10.00"), "INR")
    b = Money(Decimal("10.00"), "USD")
    with pytest.raises(CurrencyMismatch):
        a + b
    with pytest.raises(CurrencyMismatch):
        a - b
    with pytest.raises(CurrencyMismatch):
        a < b


def test_negation_and_zero():
    a = Money(Decimal("10.00"), "INR")
    assert -a == Money(Decimal("-10.00"), "INR")
    assert a + (-a) == Money(Decimal("0.00"), "INR")


def test_comparisons_in_same_currency():
    assert Money(Decimal("1.00"), "INR") < Money(Decimal("2.00"), "INR")
    assert Money(Decimal("2.00"), "INR") > Money(Decimal("1.00"), "INR")
    assert Money(Decimal("2.00"), "INR") >= Money(Decimal("2.00"), "INR")
    assert Money(Decimal("2.00"), "INR") <= Money(Decimal("2.00"), "INR")


def test_equality_requires_same_currency():
    assert Money(Decimal("10.00"), "INR") != Money(Decimal("10.00"), "USD")
    assert Money(Decimal("10.00"), "INR") == Money(Decimal("10.00"), "INR")


def test_is_hashable_and_immutable():
    a = Money(Decimal("10.00"), "INR")
    b = Money(Decimal("10.00"), "INR")
    assert hash(a) == hash(b)
    assert len({a, b}) == 1
    with pytest.raises(AttributeError):
        a.amount = Decimal("1.00")  # type: ignore[misc]


def test_str_is_the_amount():
    assert str(Money(Decimal("10.00"), "INR")) == "10.00"


def test_as_money_coerces_plain_values():
    assert as_money(Decimal("10.00"), "INR") == Money(Decimal("10.00"), "INR")
    assert as_money(Money(Decimal("10.00"), "USD"), "INR") == Money(Decimal("10.00"), "USD")
    assert as_money("10.00", "INR") == Money(Decimal("10.00"), "INR")
    assert as_money(10, "INR") == Money(Decimal("10.00"), "INR")
