from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from os import environ
from typing import Any

from dateutil.tz import gettz
from finnhub import Client
from pandas import concat
from robin_stocks.robinhood import get_ratings
from yfinance import Ticker

from ..entities.options import Options, OptionsEnum
from ..entities.prices import Prices
from ..entities.rating import Rating
from .download_enum import FinhubEnum, RobinhoodEnum, TimeZone


def _parse_date(value: str | None) -> date:
    if value is None:
        return date.today()
    return datetime.strptime(value.split("T")[0], "%Y-%m-%d").date()


@dataclass
class Downloader[T](ABC):
    symbol: str

    @abstractmethod
    def download(self) -> T:
        raise NotImplementedError


@dataclass
class StockInfo(Downloader[dict[str, Any]]):
    def download(self) -> dict[str, Any]:
        return Ticker(self.symbol).info


@dataclass
class PriceHistory(Downloader[Prices]):
    days_back: int | float
    interval: str = "1d"

    def download(self) -> Prices:
        tz = gettz(TimeZone.DEFAULT.value)
        start = datetime.now(tz) - timedelta(days=int(self.days_back))
        tic = Ticker(self.symbol)
        df = tic.history(start=start, interval=self.interval)
        return Prices(df.to_dict("index"))


@dataclass
class StockOptions(Downloader[Options]):
    max_number: int | None = None

    def __post_init__(self) -> None:
        if self.max_number is None:
            self.max_number = -1

    def download(self) -> Options:
        tic = Ticker(self.symbol)
        calls, puts = [], []
        for option in tic.options[: self.max_number]:
            tic_options = tic.option_chain(option)
            _calls, _puts = tic_options.calls, tic_options.puts
            _calls[OptionsEnum.EXPIRATION] = datetime.strptime(
                option, "%Y-%m-%d"
            ).date()
            _puts[OptionsEnum.EXPIRATION] = datetime.strptime(option, "%Y-%m-%d").date()
            calls.append(tic_options.calls)
            puts.append(tic_options.puts)
        return Options(concat(calls), concat(puts))


@dataclass
class RobinhoodRatings(Downloader[list[Rating]]):
    def download(self) -> list[Rating]:
        dt = get_ratings(self.symbol)
        return [self.robinhood_transform(dt)]

    def robinhood_transform(self, entry: dict) -> Rating:
        summary = entry[RobinhoodEnum.SUMMARY]
        return Rating(
            date=_parse_date(entry[RobinhoodEnum.PUBLISHED]),
            buy=summary[RobinhoodEnum.BUY],
            hold=summary[RobinhoodEnum.HOLD],
            sell=summary[RobinhoodEnum.SELL],
        )


@dataclass
class FinhubRating(Downloader[list[Rating]]):
    _client: Client = field(init=False)

    def __post_init__(self) -> None:
        self._client = Client(api_key=environ["FINHUB_TOKEN"])

    def download(self) -> list[Rating]:
        lst = self._client.recommendation_trends(self.symbol)
        return [self.finhub_transform(dt) for dt in lst]

    def finhub_transform(self, entry: dict) -> Rating:
        return Rating(
            date=_parse_date(entry[FinhubEnum.PUBLISHED]),
            buy=entry.get(FinhubEnum.BUY, 0)
            + 1.25 * entry.get(FinhubEnum.STRONG_BUY, 0),
            hold=entry[FinhubEnum.HOLD],
            sell=entry.get(FinhubEnum.SELL, 0)
            + 1.25 * entry.get(FinhubEnum.STRONG_SELL, 0),
        )
