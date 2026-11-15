from datetime import date
from typing import ClassVar

from pandas import DataFrame

from ..entities.options import OptionContract, Options
from ..entities.prices import PriceBar, Prices
from .mapper import Mapper

RawChain = tuple[str, DataFrame, DataFrame]


class YahooMapper[Raw, Entity](Mapper[Raw, Entity]):
    COLUMNS: ClassVar[dict[str, str]]

    @classmethod
    def records(cls, frame: DataFrame) -> list[dict]:
        frame = frame.reindex(columns=list(cls.COLUMNS)).rename(columns=cls.COLUMNS)
        return frame.astype(object).where(frame.notna(), None).to_dict("records")


class YahooPricesMapper(YahooMapper[DataFrame, Prices]):
    COLUMNS: ClassVar[dict[str, str]] = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Dividends": "dividends",
        "Stock Splits": "stock_splits",
    }

    @classmethod
    def map(cls, raw: DataFrame) -> Prices:
        rows = zip(raw.index, cls.records(raw), strict=True)
        return Prices(bars=[PriceBar(ts=ts, **row) for ts, row in rows])


class YahooOptionsMapper(YahooMapper[list[RawChain], Options]):
    COLUMNS: ClassVar[dict[str, str]] = {
        "contractSymbol": "contract_symbol",
        "strike": "strike",
        "lastTradeDate": "last_trade_date",
        "lastPrice": "last_price",
        "bid": "bid",
        "ask": "ask",
        "change": "change",
        "percentChange": "percent_change",
        "volume": "volume",
        "openInterest": "open_interest",
        "impliedVolatility": "implied_volatility",
        "inTheMoney": "in_the_money",
    }
    SIDES: ClassVar[tuple[str, str]] = ("call", "put")

    @classmethod
    def map(cls, raw: list[RawChain]) -> Options:
        return Options(
            contracts=[
                OptionContract(side=side, expiration=date.fromisoformat(exp), **row)
                for exp, *chains in raw
                for side, chain in zip(cls.SIDES, chains, strict=True)
                for row in cls.records(chain)
            ]
        )
