"""Tests for the ChangeCalculator."""

import pytest

from sortchange.models import Currency, Denomination
from sortchange.change_calculator import ChangeCalculator


class TestChangeCalculatorJPY:
    """Tests using Japanese Yen (canonical denomination set)."""

    def setup_method(self):
        self.calc = ChangeCalculator(currency=Currency.JPY)

    def test_zero_amount(self):
        result = self.calc.calculate(0)
        assert result.total == 0
        assert result.coins_used == 0
        assert result.breakdown == {}

    def test_single_denomination(self):
        result = self.calc.calculate(1000)
        assert result.breakdown.get(1000) == 1
        assert result.coins_used == 1

    def test_multiple_denominations(self):
        # 1234円: 1000 + 100*2 + 10*3 + 1*4
        result = self.calc.calculate(1234)
        assert result.total == 1234
        assert result.breakdown.get(1000) == 1
        assert result.breakdown.get(100) == 2
        assert result.breakdown.get(10) == 3
        assert result.breakdown.get(1) == 4

    def test_minimum_coins_greedy(self):
        # 60円: one 50 + one 10 = 2 coins (not six 10-yen)
        result = self.calc.calculate(60)
        assert result.coins_used == 2
        assert result.breakdown.get(50) == 1
        assert result.breakdown.get(10) == 1

    def test_exact_amount(self):
        result = self.calc.calculate(10000)
        assert result.breakdown.get(10000) == 1
        assert result.coins_used == 1

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            self.calc.calculate(-1)


class TestCalculateDifference:
    def setup_method(self):
        self.calc = ChangeCalculator(currency=Currency.JPY)

    def test_exact_payment(self):
        result = self.calc.calculate_difference(paid=1000, price=1000)
        assert result.total == 0

    def test_normal_change(self):
        result = self.calc.calculate_difference(paid=1000, price=780)
        assert result.total == 220
        assert result.breakdown.get(100) == 2
        assert result.breakdown.get(10) == 2

    def test_underpayment_raises(self):
        with pytest.raises(ValueError, match="greater than or equal"):
            self.calc.calculate_difference(paid=500, price=1000)

    def test_negative_paid_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            self.calc.calculate_difference(paid=-1, price=100)

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            self.calc.calculate_difference(paid=100, price=-1)


class TestMinimumCoins:
    def setup_method(self):
        self.calc = ChangeCalculator(currency=Currency.JPY)

    def test_zero(self):
        assert self.calc.minimum_coins(0) == 0

    def test_single_coin(self):
        assert self.calc.minimum_coins(500) == 1

    def test_multiple_coins(self):
        # 999 = 500+100*4+50+10*4+5+1*4 = 1+4+1+4+1+4 = 15
        assert self.calc.minimum_coins(999) == 15


class TestCustomDenominations:
    def test_custom_denominations(self):
        denoms = [
            Denomination(value=1, currency=Currency.JPY, label="1"),
            Denomination(value=3, currency=Currency.JPY, label="3"),
            Denomination(value=9, currency=Currency.JPY, label="9"),
        ]
        calc = ChangeCalculator(currency=Currency.JPY, denominations=denoms)
        result = calc.calculate(9)
        assert result.breakdown.get(9) == 1
        assert result.coins_used == 1

    def test_insufficient_denominations_raises(self):
        denoms = [
            Denomination(value=5, currency=Currency.JPY, label="5"),
            Denomination(value=10, currency=Currency.JPY, label="10"),
        ]
        calc = ChangeCalculator(currency=Currency.JPY, denominations=denoms)
        with pytest.raises(ValueError, match="Cannot represent"):
            calc.calculate(3)


class TestMultipleCurrencies:
    def test_usd(self):
        calc = ChangeCalculator(currency=Currency.USD)
        # 175 cents = $1.75 = 100 + 50 + 25 = 3 coins
        result = calc.calculate(175)
        assert result.total == 175
        assert result.coins_used == 3

    def test_eur(self):
        calc = ChangeCalculator(currency=Currency.EUR)
        # 299 euro-cents = 200 + 50 + 20 + 20 + 5 + 2 + 2 = 7
        result = calc.calculate(299)
        assert result.total == 299
        assert result.coins_used == 7
