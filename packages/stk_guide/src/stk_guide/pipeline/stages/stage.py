from abc import abstractmethod
from typing import Any

from foundation.market.stocks import Stocks

from ..decorators import PrePostExecution


class Stage:
    @abstractmethod
    @PrePostExecution.stage
    def __call__(self, context: Stocks, **kwargs: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def _init(self, **kwargs: Any) -> None:
        raise NotImplementedError
