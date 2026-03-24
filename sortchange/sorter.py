"""Sorting utilities for denominations and change breakdowns."""

from typing import Dict, List

from .models import Denomination


def sort_denominations(denominations: List[Denomination], descending: bool = True) -> List[Denomination]:
    """Sort a list of denominations by value.

    Args:
        denominations: The list of denominations to sort.
        descending: When True (default), sort largest first (useful for greedy
            change algorithms). When False, sort smallest first.

    Returns:
        A new sorted list of denominations.
    """
    return sorted(denominations, reverse=descending)


def group_by_denomination(coins: List[int]) -> Dict[int, int]:
    """Count occurrences of each denomination value in a flat list of coins.

    Args:
        coins: A list of integer coin/bill values (e.g. [100, 50, 10, 10]).

    Returns:
        A mapping from denomination value to count, sorted by value descending.

    Raises:
        ValueError: If any coin value is not positive.
    """
    if any(c <= 0 for c in coins):
        raise ValueError("All coin values must be positive integers.")

    counts: Dict[int, int] = {}
    for coin in coins:
        counts[coin] = counts.get(coin, 0) + 1
    # Return sorted descending so the most valuable coins appear first.
    return dict(sorted(counts.items(), reverse=True))


def filter_usable_denominations(denominations: List[Denomination], amount: int) -> List[Denomination]:
    """Return only denominations whose value does not exceed *amount*.

    Args:
        denominations: Candidate denominations.
        amount: The target change amount in smallest currency units.

    Returns:
        Filtered list, still sorted descending by value.
    """
    return [d for d in sort_denominations(denominations) if d.value <= amount]
