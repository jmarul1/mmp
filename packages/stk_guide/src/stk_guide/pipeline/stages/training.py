from typing import Any

from attrs import define
from foundation.entities.prices import PricesEnum
from pandas import DataFrame

from ...ml.models.model import Model
from ..context import Context
from ..decorators import PrePostExecution
from .stage import Stage


@define
class Trainer(Stage):
    model: Model

    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        raise NotImplementedError

    def _init(self, **kwargs: Any) -> None:
        pass


class ClosePriceTrainer(Trainer):
    @PrePostExecution.stage
    def __call__(self, context: Context) -> None:
        labels = DataFrame(context.stock.prices).transpose().Close
        _data = labels.reset_index().rename(
            {"index": PricesEnum.DATETIME.value}, axis=1
        )
        features = _data.datetime.to_frame()
        self.model.preprocessor = context.preprocessor
        self.model.train(features, labels)
        context.model = self.model


class ClosePriceOptionsTrainer(Trainer):
    @PrePostExecution.stage
    def __call__(self, context: Context) -> None:
        labels = DataFrame(context.stock.prices).transpose().Close
        _data = labels.reset_index().rename(
            {"index": PricesEnum.DATETIME.value}, axis=1
        )
        features = _data.datetime.to_frame()
        self.model.preprocessor = context.preprocessor
        self.model.train(features, labels)
        context.model = self.model
