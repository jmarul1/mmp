from dataclasses import dataclass

from foundation.encoding.encoder import Encoder
from foundation.entities.prediction import Prediction
from foundation.entities.stock import Stock

from ..ml.models.model import Model


@dataclass
class Context:
    stock: Stock | None = None
    preprocessor: Encoder | None = None
    model: Model | None = None
    prediction: Prediction | None = None
