from datetime import date as Date
from enum import StrEnum, auto

from pandas import DataFrame
from pydantic import BaseModel


class RatingEnum(StrEnum):
    BUY = auto()
    HOLD = auto()
    SELL = auto()


class Rating(BaseModel):
    date: Date
    buy: float
    hold: float
    sell: float

    def to_frame(self, index: list[str | int] | None = None) -> DataFrame:
        return DataFrame([self.model_dump()], index=index or [0])
