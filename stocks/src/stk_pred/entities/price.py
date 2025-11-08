from datetime import datetime
from typing import Self
from pandas import DataFrame
from pydantic import BaseModel


class Price(BaseModel):
    date: datetime
    close: float
    open: float
    volume: float

    @staticmethod
    def from_frame(df: DataFrame) -> list[Self]:
        return [
            Price(date=item.Index, close=item.Close, open=item.Open, volume=item.Volume)
            for item in df.itertuples()
        ]
