from datetime import datetime, date as date_type
from enum import StrEnum, auto
from numbers import Number
from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, PrivateAttr, field_validator


class RatingsEnum(StrEnum):
    DATE = auto()
    BUY = auto()
    HOLD = auto()
    SELL = auto()
    SOURCE = auto()


class Ratings(BaseModel):
    _data: DataFrame = PrivateAttr(
        default={
            RatingsEnum.DATE: [],
            RatingsEnum.BUY: [],
            RatingsEnum.HOLD: [],
            RatingsEnum.SELL: [],
            RatingsEnum.SOURCE: [],
        }
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def add(
        self, date: datetime, buy: Number, hold: Number, sell: Number, source: str
    ) -> None:
        if not isinstance(date, date_type):
            raise ValueError("date must be a datetime object")
        if not all(isinstance(x, Number) for x in [buy, hold, sell]):
            raise ValueError("buy, hold, and sell must be numbers")
        self._data[RatingsEnum.DATE].append(date)
        self._data[RatingsEnum.BUY].append(buy)
        self._data[RatingsEnum.HOLD].append(hold)
        self._data[RatingsEnum.SELL].append(sell)
        self._data[RatingsEnum.SOURCE].append(source)

    def to_frame(self) -> DataFrame:
        return DataFrame(self._data)

    def itertuples(self) -> DataFrame.itertuples:
        return self.to_frame().itertuples()

    def __setitem__(
        self, key: RatingsEnum, value: list[datetime | Number | str]
    ) -> None:
        raise NotImplementedError("Direct assignment not allowed. Use the add method.")

    def __getitem__(self, key: RatingsEnum) -> list[datetime | Number | str]:
        raise NotImplementedError(
            "Direct access not allowed. Use the to_frame or itertuples method."
        )
