from abc import abstractmethod

from foundation.entities.stocks import Stocks
from pandas import DataFrame


class Strategy:
    @abstractmethod
    def __call__(self, stocks: Stocks) -> DataFrame:
        raise NotImplementedError
