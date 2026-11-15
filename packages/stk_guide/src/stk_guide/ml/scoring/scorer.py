from abc import ABC, abstractmethod
from typing import ClassVar

from foundation.encoding.algorithms import MinMaxCoder
from foundation.encoding.encoder import Encoder
from foundation.entities.rating import RatingEnum
from pandas import DataFrame, Series


class Scorer(ABC):
    @abstractmethod
    def __call__(self, data: DataFrame) -> Series:
        pass


class RatingsScorer(Scorer):
    HOLD_WEIGHT: ClassVar[float] = 0.5

    def __init__(self, hold_weight: float = HOLD_WEIGHT) -> None:
        self.hold_weight = hold_weight

    def __call__(self, data: DataFrame) -> Series:
        _data = data.loc[:, [RatingEnum.BUY, RatingEnum.SELL, RatingEnum.HOLD]]
        df = Encoder(feature_scalers=MinMaxCoder()).fit_transform(_data)
        buy = 1 - df[RatingEnum.BUY]
        hold = df[RatingEnum.HOLD] * self.hold_weight
        scores = buy + hold + df[RatingEnum.SELL]
        nscores = (
            Encoder(feature_scalers=MinMaxCoder())
            .fit_transform(scores.to_frame())
            .iloc[:, 0]
        )
        nscores.name = "scores"
        return nscores
