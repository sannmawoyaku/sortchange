"""Data models for the sortchange service."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Currency(Enum):
    """Supported currency types."""

    JPY = "JPY"
    USD = "USD"
    EUR = "EUR"


# Standard denomination values (in smallest unit) for each currency.
DENOMINATIONS: Dict[Currency, List[int]] = {
    Currency.JPY: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
    Currency.USD: [1, 5, 10, 25, 50, 100, 500, 1000, 2000, 5000, 10000],
    Currency.EUR: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000],
}


@dataclass(frozen=True)
class Denomination:
    """Represents a single coin or bill denomination.

    Attributes:
        value: The face value in the smallest currency unit (e.g. yen, cents).
        currency: The currency this denomination belongs to.
        label: Human-readable label (e.g. "100円", "$1").
    """

    value: int
    currency: Currency
    label: str

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"Denomination value must be positive, got {self.value}")

    def __lt__(self, other: "Denomination") -> bool:
        return self.value < other.value

    def __le__(self, other: "Denomination") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "Denomination") -> bool:
        return self.value > other.value

    def __ge__(self, other: "Denomination") -> bool:
        return self.value >= other.value


@dataclass
class ChangeResult:
    """The result of a change calculation.

    Attributes:
        total: The total amount of change (in smallest currency unit).
        currency: The currency used.
        breakdown: Mapping from denomination value to count of coins/bills used.
        coins_used: Total number of coins/bills used.
    """

    total: int
    currency: Currency
    breakdown: Dict[int, int] = field(default_factory=dict)

    @property
    def coins_used(self) -> int:
        """Return the total number of individual coins/bills."""
        return sum(self.breakdown.values())

    def to_dict(self) -> Dict:
        """Serialize to a plain dictionary."""
        return {
            "total": self.total,
            "currency": self.currency.value,
            "breakdown": self.breakdown,
            "coins_used": self.coins_used,
        }

    def __repr__(self) -> str:
        lines = [f"ChangeResult(total={self.total}, currency={self.currency.value})"]
        for denom in sorted(self.breakdown.keys(), reverse=True):
            count = self.breakdown[denom]
            lines.append(f"  {denom:>6} x {count}")
        return "\n".join(lines)
