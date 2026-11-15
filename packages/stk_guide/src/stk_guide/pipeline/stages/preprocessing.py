from typing import Any

from foundation.encoding.encoder import Encoder

from ..context import Context
from ..decorators import PrePostExecution
from .stage import Stage


class Preprocessor(Stage):
    def __init__(self, encoder: Encoder | None = None) -> None:
        self.encoder = encoder or Encoder()

    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        raise NotImplementedError

    def _init(self, **kwargs: Any) -> None:
        pass


class PricePreprocessor(Preprocessor):
    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        context.preprocessor = self.encoder.fit(context.stock.prices.features())
