from collections.abc import Iterable  # pylint: disable = import-error

from .stock import Stock


class Stocks(list):
    """Contains list[Stock]"""

    def __init__(self, iterable: Iterable[Stock] | None = None) -> None:
        if iterable is None:
            iterable = []
        for item in iterable:
            self.append(item)

    def append(self, item: Stock) -> None:
        self._validate(item)
        if item not in self:
            super().append(item)

    def _validate(self, item: Stock) -> None:
        if not isinstance(item, Stock):
            raise ValueError(f"Must belong to class Stock: {item}")

    def __contains__(self, stock: object) -> bool:
        return any(item == stock for item in self)
