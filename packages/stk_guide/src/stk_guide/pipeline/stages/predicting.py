from typing import Any

from click import MissingParameter
from foundation.entities.prices import PriceBar
from pandas import DataFrame

from ..context import Context
from ..decorators import PrePostExecution
from ..prediction import Prediction
from .stage import Stage


class Predictor(Stage):
    _future_space: DataFrame

    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        raise NotImplementedError

    def _init(self, **kwargs: Any) -> None:
        if "future_space" not in kwargs:
            raise MissingParameter("future_space")
        self._future_space = kwargs["future_space"]


class PricePredictor(Predictor):
    @PrePostExecution.stage
    def __call__(self, context: Context, **kwargs: Any) -> None:
        prediction = Prediction(context.stock)
        price_preds = context.model.predict(self._future_space)
        for future_date, price_pred in zip(
            self._future_space.iloc[:, 0], price_preds, strict=False
        ):
            prediction.prices.bars.append(PriceBar(ts=future_date, close=price_pred))
        context.prediction = prediction
