from typing import Any

from click import MissingParameter
from foundation.download.downloader import PriceHistory

from ..context import Context
from ..decorators import PrePostExecution
from .stage import Stage


class Collector(Stage):
    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        raise NotImplementedError


class PriceCollector(Collector):
    _days_back: int | float
    _interval: str

    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        context.stock.populate_prices(self._days_back, self._interval)

    def _init(self, **kwargs: Any) -> None:
        if "days_back" not in kwargs:
            raise MissingParameter("days_back")
        self._interval = kwargs.get("interval", PriceHistory.INTERVAL)
        self._days_back = kwargs["days_back"]
