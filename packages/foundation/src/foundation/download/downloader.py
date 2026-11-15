from abc import ABC, abstractmethod
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


class Downloader[T](ABC):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @abstractmethod
    def download(self) -> T:
        raise NotImplementedError


class StockInfo(Downloader[dict[str, Any]]):
    def download(self) -> dict[str, Any]:
        return Ticker(self.symbol).info


class PriceHistory(Downloader[Prices]):
    def __init__(
        self, symbol: str, days_back: int | float, interval: str = "1d"
    ) -> None:
        super().__init__(symbol)
        self.days_back = days_back
        self.interval = interval

    def download(self) -> Prices:
        tz = gettz(TimeZone.DEFAULT.value)
        start = datetime.now(tz) - timedelta(days=int(self.days_back))
        tic = Ticker(self.symbol)
        df = tic.history(start=start, interval=self.interval)
        return Prices(df.to_dict("index"))


class StockOptions(Downloader[Options]):
    def __init__(self, symbol: str, max_number: int | None = None) -> None:
        super().__init__(symbol)
        self.max_number = -1 if max_number is None else max_number

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


class FinhubRating(Downloader[list[Rating]]):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
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
