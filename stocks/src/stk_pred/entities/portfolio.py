from pydantic import BaseModel, PrivateAttr
from .stock import Stock


class Portfolio(BaseModel):
    _stocks: dict[str, Stock] = PrivateAttr(default_factory=dict)

    def __setitem__(self, symbol: str, stock: Stock) -> None:
        self._stocks[symbol] = stock

    def __getitem__(self, symbol: str) -> Stock:
        return self._stocks[symbol]

    def __delitem__(self, symbol: str) -> None:
        del self._stocks[symbol]
