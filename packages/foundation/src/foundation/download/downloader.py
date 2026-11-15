from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from os import environ
from typing import Any, ClassVar

from dateutil.tz import gettz
from finnhub import Client
from pandas import DataFrame
from robin_stocks.robinhood import get_ratings
from yfinance import Ticker

from .download_enum import TimeZone


class Downloader[Raw](ABC):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def download(self) -> Raw:
        raise NotImplementedError


class StockInfo(Downloader[dict[str, Any]]):
    def download(self) -> dict[str, Any]:
        return Ticker(self.symbol).info


class PriceHistory(Downloader[DataFrame]):
    INTERVAL: ClassVar[str] = "1d"

    def __init__(
        self, symbol: str, days_back: int | float, interval: str = INTERVAL
    ) -> None:
        super().__init__(symbol)
        self.days_back = days_back
        self.interval = interval

    def download(self) -> DataFrame:
        start = datetime.now(gettz(TimeZone.DEFAULT.value)) - timedelta(
            days=int(self.days_back)
        )
        return Ticker(self.symbol).history(start=start, interval=self.interval)


class StockOptions(Downloader[list[tuple[str, DataFrame, DataFrame]]]):
    DEFAULT_MAX: ClassVar[int] = -1

    def __init__(self, symbol: str, max_number: int = DEFAULT_MAX) -> None:
        super().__init__(symbol)
        self.max_number = max_number

    def download(self) -> list[tuple[str, DataFrame, DataFrame]]:
        tic = Ticker(self.symbol)
        chains = []
        for expiration in tic.options[: self.max_number]:
            chain = tic.option_chain(expiration)
            chains.append((expiration, chain.calls, chain.puts))
        return chains


class RobinhoodRatings(Downloader[dict[str, Any]]):
    def download(self) -> dict[str, Any]:
        return get_ratings(self.symbol)


class FinhubRating(Downloader[list[dict[str, Any]]]):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self._client = Client(api_key=environ["FINHUB_TOKEN"])

    def download(self) -> list[dict[str, Any]]:
        return self._client.recommendation_trends(self.symbol)
