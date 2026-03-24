# Implementation

## Overview

`sortchange` is a Python library that calculates and sorts coin/bill change for a given amount. It supports Japanese Yen (JPY), US Dollars (USD), and Euros (EUR) out of the box, and can be extended with custom denomination sets.

## Project Structure

```
sortchange/
├── sortchange/
│   ├── __init__.py          # Public API re-exports
│   ├── models.py            # Data structures: Currency, Denomination, ChangeResult
│   ├── sorter.py            # Sorting and grouping utilities
│   └── change_calculator.py # Core ChangeCalculator class
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_sorter.py
│   └── test_change_calculator.py
├── main.py                  # CLI demonstration entry point
├── requirements.txt
└── README.md
```

## Algorithm

The change calculator uses a **greedy algorithm** (largest denomination first). This produces the minimum number of coins/bills for canonical currency systems (JPY, USD, EUR) where the denomination set satisfies the greedy-choice property.

### Steps

1. Sort denominations in descending order of value.
2. For each denomination `d`:
   - Compute `count = remaining // d.value`.
   - Subtract `count * d.value` from `remaining`.
   - Store `{d.value: count}` in the breakdown if `count > 0`.
3. If `remaining > 0` after all denominations are exhausted, raise `ValueError`.

### Complexity

- **Time**: O(k) where k is the number of denomination types.
- **Space**: O(k) for the breakdown dictionary.

## Usage Examples

```python
from sortchange import ChangeCalculator, Currency

# Japanese Yen — calculate change for 1234円
calc = ChangeCalculator(currency=Currency.JPY)
result = calc.calculate(1234)
print(result)
# ChangeResult(total=1234, currency=JPY)
#     1000 x 1
#      100 x 2
#       10 x 3
#        1 x 4

# Calculate change when a customer pays 1000円 for an 780円 item
result = calc.calculate_difference(paid=1000, price=780)
print(result.total)   # 220
print(result.coins_used)  # 4

# Custom denominations
from sortchange import Denomination
custom = [
    Denomination(value=1, currency=Currency.JPY, label="1"),
    Denomination(value=3, currency=Currency.JPY, label="3"),
    Denomination(value=9, currency=Currency.JPY, label="9"),
]
calc2 = ChangeCalculator(currency=Currency.JPY, denominations=custom)
result2 = calc2.calculate(9)
print(result2.coins_used)  # 1
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Extending the Service

To add a new currency:

1. Add it to the `Currency` enum in `models.py`.
2. Add its denomination list (in smallest unit) to `DENOMINATIONS` in `models.py`.
3. Add a label lambda in `_build_default_denominations()` in `change_calculator.py`.
4. Write tests in `tests/test_change_calculator.py`.
