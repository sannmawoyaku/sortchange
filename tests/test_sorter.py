"""Tests for sortchange sorting utilities."""

import pytest

from sortchange.models import Currency, Denomination
from sortchange.sorter import sort_denominations, group_by_denomination, filter_usable_denominations


def _make_denom(value: int) -> Denomination:
    return Denomination(value=value, currency=Currency.JPY, label=f"{value}円")


class TestSortDenominations:
    def test_sort_descending_default(self):
        denoms = [_make_denom(v) for v in [10, 500, 50, 1]]
        result = sort_denominations(denoms)
        assert [d.value for d in result] == [500, 50, 10, 1]

    def test_sort_ascending(self):
        denoms = [_make_denom(v) for v in [10, 500, 50, 1]]
        result = sort_denominations(denoms, descending=False)
        assert [d.value for d in result] == [1, 10, 50, 500]

    def test_already_sorted(self):
        denoms = [_make_denom(v) for v in [500, 100, 50, 10, 5, 1]]
        result = sort_denominations(denoms)
        assert [d.value for d in result] == [500, 100, 50, 10, 5, 1]

    def test_single_element(self):
        denoms = [_make_denom(100)]
        assert sort_denominations(denoms) == denoms

    def test_empty_list(self):
        assert sort_denominations([]) == []


class TestGroupByDenomination:
    def test_basic_grouping(self):
        coins = [100, 50, 10, 10, 5]
        result = group_by_denomination(coins)
        assert result[100] == 1
        assert result[50] == 1
        assert result[10] == 2
        assert result[5] == 1

    def test_sorted_descending(self):
        coins = [1, 100, 10]
        result = group_by_denomination(coins)
        assert list(result.keys()) == [100, 10, 1]

    def test_invalid_coin(self):
        with pytest.raises(ValueError):
            group_by_denomination([100, -1, 10])

    def test_zero_coin(self):
        with pytest.raises(ValueError):
            group_by_denomination([0, 10])

    def test_empty_list(self):
        assert group_by_denomination([]) == {}


class TestFilterUsableDenominations:
    def test_filters_large_denominations(self):
        denoms = [_make_denom(v) for v in [1000, 500, 100, 50, 10, 5, 1]]
        result = filter_usable_denominations(denoms, amount=150)
        assert all(d.value <= 150 for d in result)

    def test_result_sorted_descending(self):
        denoms = [_make_denom(v) for v in [1, 10, 100, 500]]
        result = filter_usable_denominations(denoms, amount=200)
        values = [d.value for d in result]
        assert values == sorted(values, reverse=True)

    def test_exact_match_included(self):
        denoms = [_make_denom(v) for v in [100, 50]]
        result = filter_usable_denominations(denoms, amount=100)
        assert any(d.value == 100 for d in result)
