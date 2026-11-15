from attrs import define, field

from .prices import Prices
from .stock import Stock


@define
class Prediction:
    stock: Stock = field(default=None)
    recommendation: str = field(default=None)
    prices: Prices = field(factory=Prices)
