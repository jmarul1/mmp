from dataclasses import dataclass

from foundation.encoding.encoder import Encoder
from foundation.market.stock import Stock

from ..ml.models.model import Model
from .prediction import Prediction


@dataclass
class Context:
    stock: Stock | None = None
    preprocessor: Encoder | None = None
    model: Model | None = None
    prediction: Prediction | None = None
