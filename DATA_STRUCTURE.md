# Data Structures

## Currency (Enum)

Represents a supported currency.

| Value | Description |
|-------|-------------|
| `JPY` | Japanese Yen |
| `USD` | US Dollar |
| `EUR` | Euro |

## DENOMINATIONS (dict)

A constant mapping from `Currency` to a list of denomination values (in the smallest currency unit).

```python
DENOMINATIONS: Dict[Currency, List[int]] = {
    Currency.JPY: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
    Currency.USD: [1, 5, 10, 25, 50, 100, 500, 1000, 2000, 5000, 10000],
    Currency.EUR: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000],
}
```

## Denomination (dataclass, frozen)

Represents a single coin or bill denomination.

| Field | Type | Description |
|-------|------|-------------|
| `value` | `int` | Face value in the smallest currency unit (must be > 0) |
| `currency` | `Currency` | Currency this denomination belongs to |
| `label` | `str` | Human-readable label (e.g. `"100円"`, `"$1.00"`) |

Supports comparison operators (`<`, `<=`, `>`, `>=`) based on `value`.

## ChangeResult (dataclass)

Holds the result of a change-calculation operation.

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total change amount in the smallest currency unit |
| `currency` | `Currency` | The currency used |
| `breakdown` | `Dict[int, int]` | Maps denomination value → number of coins/bills used |

### Computed Properties

| Property | Type | Description |
|----------|------|-------------|
| `coins_used` | `int` | Total number of individual coins/bills |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | `Dict` | Serialises the result to a plain dictionary |
