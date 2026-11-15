from dataclasses import dataclass, field

from foundation.entities.prices import Prices
from foundation.market.stock import Stock


@dataclass
class Prediction:
    stock: Stock | None = None
    recommendation: str | None = None
    prices: Prices = field(default_factory=Prices)
