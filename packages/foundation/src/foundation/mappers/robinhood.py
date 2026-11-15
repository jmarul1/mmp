from datetime import date, datetime
from typing import Any

from ..download.download_enum import RobinhoodEnum
from ..entities.rating import Rating
from .mapper import Mapper


class RobinhoodRatingMapper(Mapper[dict[str, Any], Rating]):
    @classmethod
    def map(cls, raw: dict[str, Any]) -> Rating:
        published = raw.get(RobinhoodEnum.PUBLISHED)
        summary = raw[RobinhoodEnum.SUMMARY]
        return Rating(
            date=datetime.fromisoformat(published).date()
            if published
            else date.today(),
            buy=summary[RobinhoodEnum.BUY],
            hold=summary[RobinhoodEnum.HOLD],
            sell=summary[RobinhoodEnum.SELL],
        )
