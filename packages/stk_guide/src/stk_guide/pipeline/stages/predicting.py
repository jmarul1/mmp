from typing import Any

from attrs import define, field
from click import MissingParameter
from foundation.entities.prediction import Prediction
from pandas import DataFrame

from ..context import Context
from ..decorators import PrePostExecution
from .stage import Stage


@define
class Predictor(Stage):
    _future_space: DataFrame = field(init=False)

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
            prediction.prices[future_date] = {"Close": price_pred}
        context.prediction = prediction
