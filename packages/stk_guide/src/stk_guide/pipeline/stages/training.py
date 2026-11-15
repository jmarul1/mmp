from typing import Any

from ...ml.models.model import Model
from ..context import Context
from ..decorators import PrePostExecution
from .stage import Stage


class Trainer(Stage):
    def __init__(self, model: Model) -> None:
        self.model = model

    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        raise NotImplementedError

    def _init(self, **kwargs: Any) -> None:
        pass


class ClosePriceTrainer(Trainer):
    @PrePostExecution.stage
    def __call__(self, context: Context) -> None:
        prices = context.stock.prices
        self.model.preprocessor = context.preprocessor
        self.model.train(prices.features(), prices.to_frame().Close)
        context.model = self.model


class ClosePriceOptionsTrainer(ClosePriceTrainer):
    pass
