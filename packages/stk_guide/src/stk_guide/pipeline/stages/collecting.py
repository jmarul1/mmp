from typing import Any

from attrs import define, field
from click import MissingParameter

from ..context import Context
from ..decorators import PrePostExecution
from .stage import Stage


@define
class Collector(Stage):
    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        raise NotImplementedError


@define
class PriceCollector(Collector):
    _days_back: int | float = field(init=False)
    _interval: str = field(init=False)

    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        context.stock.populate_prices(self._days_back, self._interval)

    def _init(self, **kwargs: Any) -> None:
        if "days_back" not in kwargs:
            raise MissingParameter("days_back")
        if "interval" in kwargs:
            self._interval = kwargs["interval"]
        self._days_back = kwargs["days_back"]
