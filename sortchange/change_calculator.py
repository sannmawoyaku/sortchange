"""Core change-calculation logic for the sortchange service."""

from typing import Dict, List, Optional

from .models import ChangeResult, Currency, Denomination, DENOMINATIONS
from .sorter import sort_denominations


def _build_default_denominations(currency: Currency) -> List[Denomination]:
    """Build a list of Denomination objects for the given currency."""
    values = DENOMINATIONS[currency]
    labels = {
        Currency.JPY: lambda v: f"{v}円",
        Currency.USD: lambda v: f"${v // 100}.{v % 100:02d}" if v >= 100 else f"{v}¢",
        Currency.EUR: lambda v: f"€{v // 100}.{v % 100:02d}" if v >= 100 else f"{v}ct",
    }
    label_fn = labels[currency]
    return [Denomination(value=v, currency=currency, label=label_fn(v)) for v in values]


class ChangeCalculator:
    """Calculate the optimal change breakdown for a given amount.

    The calculator uses a greedy algorithm (largest denomination first), which
    produces the minimum number of coins/bills for canonical currency systems
    (JPY, USD, EUR).

    Attributes:
        currency: The currency to operate in.
        denominations: The available denominations, sorted descending.
    """

    def __init__(
        self,
        currency: Currency = Currency.JPY,
        denominations: Optional[List[Denomination]] = None,
    ) -> None:
        if denominations is not None:
            self.denominations = sort_denominations(denominations)
        else:
            self.denominations = sort_denominations(_build_default_denominations(currency))
        self.currency = currency

    def calculate(self, amount: int) -> ChangeResult:
        """Calculate the change breakdown for *amount*.

        Args:
            amount: The change amount in the smallest currency unit (e.g. yen,
                cents). Must be non-negative.

        Returns:
            A :class:`ChangeResult` describing how many of each denomination to
            use.

        Raises:
            ValueError: If *amount* is negative.
        """
        if amount < 0:
            raise ValueError(f"Amount must be non-negative, got {amount}")

        breakdown: Dict[int, int] = {}
        remaining = amount

        for denom in self.denominations:
            if remaining == 0:
                break
            if denom.value <= remaining:
                count = remaining // denom.value
                breakdown[denom.value] = count
                remaining -= denom.value * count

        if remaining != 0:
            raise ValueError(
                f"Cannot represent {amount} with the available denominations. "
                f"Remaining: {remaining}"
            )

        return ChangeResult(total=amount, currency=self.currency, breakdown=breakdown)

    def calculate_difference(self, paid: int, price: int) -> ChangeResult:
        """Calculate change to return when a customer pays *paid* for *price*.

        Args:
            paid: Amount the customer paid (smallest currency unit).
            price: Price of the goods/service (smallest currency unit).

        Returns:
            A :class:`ChangeResult` for the difference ``paid - price``.

        Raises:
            ValueError: If *paid* is less than *price*, or either value is
                negative.
        """
        if paid < 0 or price < 0:
            raise ValueError("paid and price must be non-negative.")
        if paid < price:
            raise ValueError(
                f"paid ({paid}) must be greater than or equal to price ({price})."
            )
        return self.calculate(paid - price)

    def minimum_coins(self, amount: int) -> int:
        """Return the minimum number of coins/bills required for *amount*.

        This is a convenience wrapper around :meth:`calculate`.

        Args:
            amount: The change amount in the smallest currency unit.

        Returns:
            Total number of coins/bills.
        """
        return self.calculate(amount).coins_used
