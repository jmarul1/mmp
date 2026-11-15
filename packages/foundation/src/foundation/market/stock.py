from typing import Any, ClassVar

from pandas import DataFrame, concat

from ..download.downloader import (
    FinhubRating,
    PriceHistory,
    RobinhoodRatings,
    StockInfo,
    StockOptions,
)
from ..entities.options import Options
from ..entities.prices import Prices
from ..entities.rating import Rating
from ..mappers.finnhub import FinnhubRatingMapper
from ..mappers.robinhood import RobinhoodRatingMapper
from ..mappers.yahoo import YahooOptionsMapper, YahooPricesMapper


class Stock:
    DAYS_BACK: ClassVar[int] = 5

    def __init__(self, symbol: str, company: str | None = None) -> None:
        self.symbol = symbol
        self.company = company or symbol
        self.prices: Prices | None = None
        self.options: Options | None = None
        self.ratings: dict[str, list[Rating]] = {}
        self.info: dict[str, Any] = StockInfo(symbol).download()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            raise ValueError("Cannot compare to non Stock objects")
        return self.symbol == value.symbol

    def __hash__(self) -> int:
        return hash(self.symbol)

    def __str__(self) -> str:
        return self.symbol

    @property
    def robinhood_ratings(self) -> list[Rating]:
        return [RobinhoodRatingMapper.map(RobinhoodRatings(self.symbol).download())]

    @property
    def finhub_ratings(self) -> list[Rating]:
        return [
            FinnhubRatingMapper.map(r) for r in FinhubRating(self.symbol).download()
        ]

    def populate_prices(
        self, days_back: int | float = DAYS_BACK, interval: str = PriceHistory.INTERVAL
    ) -> None:
        raw = PriceHistory(self.symbol, days_back, interval).download()
        self.prices = YahooPricesMapper.map(raw)

    def populate_options(self, max_number: int = StockOptions.DEFAULT_MAX) -> None:
        raw = StockOptions(self.symbol, max_number).download()
        self.options = YahooOptionsMapper.map(raw)

    def populate_ratings(self) -> None:
        self.ratings = {
            "robinhood": self.robinhood_ratings,
            "finnhub": self.finhub_ratings,
        }

    def ratings_frame(self) -> DataFrame:
        return concat(
            r.to_frame().assign(source=source)
            for source, ratings in self.ratings.items()
            for r in ratings
        ).reset_index(drop=True)
