from datetime import date
from typing import Any, ClassVar

from ..download.download_enum import FinhubEnum
from ..entities.rating import Rating
from .mapper import Mapper


class FinnhubRatingMapper(Mapper[dict[str, Any], Rating]):
    STRONG_WEIGHT: ClassVar[float] = 1.25

    @classmethod
    def map(cls, raw: dict[str, Any]) -> Rating:
        published = raw.get(FinhubEnum.PUBLISHED)
        return Rating(
            date=date.fromisoformat(published) if published else date.today(),
            buy=raw.get(FinhubEnum.BUY, 0)
            + cls.STRONG_WEIGHT * raw.get(FinhubEnum.STRONG_BUY, 0),
            hold=raw[FinhubEnum.HOLD],
            sell=raw.get(FinhubEnum.SELL, 0)
            + cls.STRONG_WEIGHT * raw.get(FinhubEnum.STRONG_SELL, 0),
        )
