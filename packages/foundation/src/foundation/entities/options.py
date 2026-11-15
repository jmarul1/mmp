from datetime import date, datetime
from enum import StrEnum, auto

from pandas import DataFrame
from pydantic import BaseModel


class OptionsEnum(StrEnum):
    EXPIRATION = auto()
    BID = auto()
    ASK = auto()
    IMPLIEDVOLATILITY = "implied_volatility"
    OPENINTEREST = "open_interest"
    PERCENTCHANGE = "percent_change"
    VOLUME = auto()
    PROJECTED_PRICE_v0 = auto()
    PROJECTED_PRICE_v1 = auto()
    STRIKE = auto()
    SCORES = auto()


class OptionContract(BaseModel):
    contract_symbol: str
    side: str
    expiration: date
    strike: float
    last_trade_date: datetime | None = None
    last_price: float | None = None
    bid: float | None = None
    ask: float | None = None
    change: float | None = None
    percent_change: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    implied_volatility: float | None = None
    in_the_money: bool | None = None


class Options(BaseModel):
    contracts: list[OptionContract] = []

    def to_frame(self, side: str | None = None) -> DataFrame:
        rows = [c.model_dump() for c in self.contracts if side in (None, c.side)]
        return DataFrame(rows, columns=list(OptionContract.model_fields))

    @property
    def calls(self) -> DataFrame:
        return self.to_frame("call")

    @property
    def puts(self) -> DataFrame:
        return self.to_frame("put")
