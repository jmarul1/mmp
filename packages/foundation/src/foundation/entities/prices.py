from datetime import datetime
from enum import StrEnum, auto

from pandas import DataFrame
from pydantic import BaseModel


class PricesEnum(StrEnum):
    DATETIME = auto()


class PriceBar(BaseModel):
    ts: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    dividends: float | None = None
    stock_splits: float | None = None


class Prices(BaseModel):
    bars: list[PriceBar] = []

    def to_frame(self) -> DataFrame:
        rows = [bar.model_dump() for bar in self.bars]
        return DataFrame(rows, columns=list(PriceBar.model_fields)).set_index("ts")

    def features(self) -> DataFrame:
        return DataFrame({PricesEnum.DATETIME.value: [bar.ts for bar in self.bars]})
