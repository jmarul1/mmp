from attrs import define, field
from foundation.encoding.encoder import Encoder
from foundation.entities.prediction import Prediction
from foundation.entities.stock import Stock

from ..ml.models.model import Model


@define
class Context:
    stock: Stock = field(default=None)
    preprocessor: Encoder = field(default=None)
    model: Model = field(default=None)
    prediction: Prediction = field(default=None)
