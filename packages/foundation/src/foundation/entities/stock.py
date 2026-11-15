from typing import Any

from ..download.downloader import (
    FinhubRating,
    PriceHistory,
    RobinhoodRatings,
    StockInfo,
    StockOptions,
)
from .options import Options
from .prices import Prices
from .rating import Rating


class Stock:
    def __init__(self, symbol: str, company: str | None = None) -> None:
        self.symbol = symbol
        self.company = company or symbol
        self.prices: Prices | None = None
        self.options: Options | None = None
        self.info: dict[str, Any] = StockInfo(symbol).download()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            raise ValueError("Cannot compare to non Stock objects")
        return self.symbol == value.symbol

    @property
    def robinhood_ratings(self) -> list[Rating]:
        return RobinhoodRatings(self.symbol).download()

    @property
    def finhub_ratings(self) -> list[Rating]:
        return FinhubRating(self.symbol).download()

    def populate_prices(
        self, days_back: int | float = 5, interval: str | None = None
    ) -> None:
        self.prices = PriceHistory(self.symbol, days_back, interval).download()

    def populate_options(self, max_number: int | None = None) -> None:
        self.options = StockOptions(self.symbol, max_number).download()

    def __hash__(self) -> int:
        return hash(self.symbol)

    def __str__(self) -> str:
        return self.symbol
