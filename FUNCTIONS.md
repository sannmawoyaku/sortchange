# Functions

## sorter module

### `sort_denominations(denominations, descending=True) -> List[Denomination]`

Sort a list of `Denomination` objects by value.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `denominations` | `List[Denomination]` | — | Denominations to sort |
| `descending` | `bool` | `True` | Largest first when `True`, smallest first when `False` |

Returns a new sorted list (does not mutate the input).

---

### `group_by_denomination(coins) -> Dict[int, int]`

Count how many of each denomination value appear in a flat list of coins.

| Parameter | Type | Description |
|-----------|------|-------------|
| `coins` | `List[int]` | Coin/bill values (all must be positive) |

Returns a `dict` mapping value → count, sorted descending. Raises `ValueError` for non-positive values.

---

### `filter_usable_denominations(denominations, amount) -> List[Denomination]`

Return only denominations whose value does not exceed `amount`, sorted descending.

| Parameter | Type | Description |
|-----------|------|-------------|
| `denominations` | `List[Denomination]` | Candidate denominations |
| `amount` | `int` | Upper bound (inclusive) |

---

## ChangeCalculator class

### `__init__(currency=Currency.JPY, denominations=None)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `currency` | `Currency` | `Currency.JPY` | Currency to operate in |
| `denominations` | `Optional[List[Denomination]]` | `None` | Custom denominations; built-in defaults are used when `None` |

---

### `calculate(amount) -> ChangeResult`

Calculate the minimum-coin breakdown for `amount` using the greedy algorithm.

| Parameter | Type | Description |
|-----------|------|-------------|
| `amount` | `int` | Change amount in smallest currency unit (must be ≥ 0) |

Raises `ValueError` for negative amounts or amounts that cannot be represented.

---

### `calculate_difference(paid, price) -> ChangeResult`

Calculate the change to return when a customer pays `paid` for goods costing `price`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `paid` | `int` | Amount paid (smallest currency unit, must be ≥ `price`) |
| `price` | `int` | Price of goods (smallest currency unit) |

Raises `ValueError` if `paid < price` or either value is negative.

---

### `minimum_coins(amount) -> int`

Convenience method returning the total number of coins/bills for `amount`.
