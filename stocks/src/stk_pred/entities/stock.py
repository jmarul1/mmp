from pydantic import BaseModel
from ..download.downloader import (
    PriceHistory,
    StockInfo,
    StockOptions,
    RobinhoodRatings,
    FinhubRating,
)
from ..download.download_enum import StockInfoEnum
from .price import Price
from .options import Options
from .ratings import Ratings


class Stock(BaseModel):
    symbol: str
    company: str
    prices: list[Price] = None
    options: Options = None
    pe_ratio: float = None
    revenue_growth: float = None
    market_cap: float = None
    ratings: Ratings = None

    def populate(self, days_back: int, interval: str, max_options: int) -> None:
        self.populate_prices(days_back=days_back, interval=interval)
        self.populate_options(max_number=max_options)
        self.populate_ratings()
        self.populate_info()

    def populate_prices(self, days_back: int, interval: str) -> None:
        prices = PriceHistory(
            symbol=self.symbol, days_back=days_back, interval=interval
        ).download()
        self.prices = Price.from_frame(prices)

    def populate_options(self, max_number: int = None) -> None:
        options = StockOptions(symbol=self.symbol, max_number=max_number).download()
        self.options = Options(calls=options[0], puts=options[1])

    def populate_ratings(self) -> None:
        robinhood = RobinhoodRatings(symbol=self.symbol).download()
        finhub = FinhubRating(symbol=self.symbol).download()
        self.ratings = Ratings()
        for rating in robinhood + finhub:
            self.ratings.add(rating[0], rating[1], rating[2], rating[3], rating[4])

    def populate_info(self) -> None:
        info = StockInfo(symbol=self.symbol).download()
        self.pe_ratio = info.get(StockInfoEnum.PE_RATIO)
        self.revenue_growth = info.get(StockInfoEnum.REVENUE_GROWTH)
        self.market_cap = info.get(StockInfoEnum.MARKET_CAP)

    def __hash__(self) -> int:
        return hash(self.symbol)

    def __str__(self) -> str:
        return self.symbol
