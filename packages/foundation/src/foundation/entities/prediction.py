from dataclasses import dataclass, field

from .prices import Prices
from .stock import Stock


@dataclass
class Prediction:
    stock: Stock | None = None
    recommendation: str | None = None
    prices: Prices = field(default_factory=Prices)
