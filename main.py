"""Entry point for the sortchange CLI demo."""

from sortchange import ChangeCalculator, Currency


def demo() -> None:
    """Run a short demonstration of the sortchange service."""
    examples = [
        (Currency.JPY, 1234),
        (Currency.JPY, 0),
        (Currency.USD, 175),
        (Currency.EUR, 299),
    ]

    for currency, amount in examples:
        calc = ChangeCalculator(currency=currency)
        result = calc.calculate(amount)
        print(result)
        print()


if __name__ == "__main__":
    demo()
