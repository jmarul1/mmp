from abc import ABC, abstractmethod
from numbers import Number
from os import environ
from typing import Any
from datetime import datetime, timedelta, date
from dateutil.tz import gettz
from pydantic import BaseModel, PrivateAttr
from pandas import DataFrame, concat
from yfinance import Ticker
from robin_stocks.robinhood import get_ratings
from finnhub import Client
from .download_enum import FinhubEnum, RobinhoodEnum, TimeZone, OptionsEnum
from ..settings import FinhubSettings

settings = FinhubSettings()
RatingEntry = tuple[date, Number, Number, Number, str]


class Downloader(BaseModel):
    symbol: str

    def download(self) -> DataFrame | tuple[DataFrame, DataFrame] | list[RatingEntry]:
        raise NotImplementedError


class StockInfo(Downloader):
    def download(self) -> dict[str, Any]:
        return Ticker(self.symbol).info


class PriceHistory(Downloader):
    days_back: int | float
    interval: str

    def download(self) -> DataFrame:
        tz = gettz(TimeZone.DEFAULT.value)
        start = datetime.now(tz) - timedelta(days=int(self.days_back))
        tic = Ticker(self.symbol)
        df = tic.history(start=start, interval=self.interval)
        return df


class StockOptions(Downloader):
    max_number: int = -1

    def download(self) -> tuple[DataFrame, DataFrame]:
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
        return (concat(calls), concat(puts))


class RobinhoodRatings(Downloader):
    def download(self) -> list[RatingEntry]:
        dt = get_ratings(self.symbol)
        return [self.robinhood_transform(dt)]

    def robinhood_transform(self, entry: dict) -> RatingEntry:
        date_str = entry[RobinhoodEnum.PUBLISHED]
        _date = (
            datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").date()
            if date_str is not None
            else date.today()
        )
        for name, value in entry[RobinhoodEnum.SUMMARY].items():
            match name:
                case RobinhoodEnum.BUY:
                    buy = value
                case RobinhoodEnum.SELL:
                    sell = value
                case RobinhoodEnum.HOLD:
                    hold = value
                case _:
                    pass
        return (_date, buy, hold, sell, "robinhood")


class FinhubRating(Downloader):
    _client: Client = PrivateAttr()

    def model_post_init(self, __context) -> None:
        self._client = Client(api_key=settings.api_key)

    def download(self) -> list[RatingEntry]:
        lst = self._client.recommendation_trends(self.symbol)
        return [self.finhub_transform(dt) for dt in lst]

    def finhub_transform(self, entry: dict) -> RatingEntry:
        date_str = entry[FinhubEnum.PUBLISHED]
        _date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str is not None
            else date.today()
        )
        buy = sell = 0
        for name, value in entry.items():
            match name:
                case FinhubEnum.STRONG_BUY:
                    buy += value * 1.25
                case FinhubEnum.STRONG_SELL:
                    sell += value * 1.25
                case FinhubEnum.BUY:
                    buy += value
                case FinhubEnum.SELL:
                    sell += value
                case FinhubEnum.HOLD:
                    hold = value
                case _:
                    pass
        return (_date, buy, hold, sell, "finhub")
