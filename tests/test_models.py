"""Tests for sortchange data models."""

import pytest

from sortchange.models import Currency, Denomination, ChangeResult, DENOMINATIONS


class TestDenomination:
    def test_valid_denomination(self):
        d = Denomination(value=100, currency=Currency.JPY, label="100円")
        assert d.value == 100
        assert d.currency == Currency.JPY
        assert d.label == "100円"

    def test_invalid_value_zero(self):
        with pytest.raises(ValueError, match="positive"):
            Denomination(value=0, currency=Currency.JPY, label="0円")

    def test_invalid_value_negative(self):
        with pytest.raises(ValueError, match="positive"):
            Denomination(value=-1, currency=Currency.JPY, label="-1円")

    def test_ordering(self):
        d1 = Denomination(value=10, currency=Currency.JPY, label="10円")
        d2 = Denomination(value=100, currency=Currency.JPY, label="100円")
        assert d1 < d2
        assert d2 > d1
        assert d1 <= d1
        assert d2 >= d2

    def test_frozen(self):
        d = Denomination(value=50, currency=Currency.JPY, label="50円")
        with pytest.raises(Exception):
            d.value = 100  # type: ignore[misc]


class TestChangeResult:
    def test_coins_used(self):
        result = ChangeResult(
            total=160,
            currency=Currency.JPY,
            breakdown={100: 1, 50: 1, 10: 1},
        )
        assert result.coins_used == 3

    def test_coins_used_empty(self):
        result = ChangeResult(total=0, currency=Currency.JPY, breakdown={})
        assert result.coins_used == 0

    def test_to_dict(self):
        result = ChangeResult(
            total=100,
            currency=Currency.JPY,
            breakdown={100: 1},
        )
        d = result.to_dict()
        assert d["total"] == 100
        assert d["currency"] == "JPY"
        assert d["breakdown"] == {100: 1}
        assert d["coins_used"] == 1

    def test_repr_contains_total(self):
        result = ChangeResult(total=100, currency=Currency.JPY, breakdown={100: 1})
        assert "100" in repr(result)


class TestDenominationsConstant:
    def test_jpy_denominations_positive(self):
        for v in DENOMINATIONS[Currency.JPY]:
            assert v > 0

    def test_usd_denominations_positive(self):
        for v in DENOMINATIONS[Currency.USD]:
            assert v > 0

    def test_eur_denominations_positive(self):
        for v in DENOMINATIONS[Currency.EUR]:
            assert v > 0
