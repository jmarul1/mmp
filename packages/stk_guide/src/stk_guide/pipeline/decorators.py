from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from foundation.market.stocks import Stocks

if TYPE_CHECKING:
    from .stages.stage import Stage


class PrePostExecution:
    @staticmethod
    def stage(func: Callable) -> Callable:
        @wraps(func)
        def func_wrapper(stage: Stage, context: Stocks, **kwargs: Any) -> None:
            stage._init(**kwargs)  # pylint: disable=protected-access
            func(stage, context, **kwargs)

        return func_wrapper
