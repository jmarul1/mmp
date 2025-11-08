from enum import StrEnum, auto
from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, field_validator


class OptionsEnum(StrEnum):
    EXPIRATION = auto()
    BID = auto()
    ASK = auto()
    IMPLIEDVOLATILITY = "impliedVolatility"
    OPENINTEREST = "openInterest"
    PERCENTCHANGE = "percentChange"
    VOLUME = auto()
    PROJECTED_PRICE_v0 = auto()
    PROJECTED_PRICE_v1 = auto()
    STRIKE = auto()
    SCORES = auto()


class Options(BaseModel):
    calls: DataFrame
    puts: DataFrame
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("calls", "puts", mode="before")
    def check_dataframe(cls, v: DataFrame) -> DataFrame:
        if not isinstance(v, DataFrame):
            raise ValueError("Must be a pandas DataFrame")
        return v
