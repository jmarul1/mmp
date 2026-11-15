from collections.abc import Iterator
from math import ceil
from typing import ClassVar

from foundation.analysis.options import OptionsAnalyzer
from foundation.market.stock import Stock
from matplotlib.axes import Axes
from matplotlib.pyplot import subplots
from pandas import DataFrame, concat


class Watchlist:
    EXPIRATIONS: ClassVar[int] = 10

    def __init__(self, symbols: list[str]) -> None:
        self.stocks = [Stock(symbol) for symbol in dict.fromkeys(symbols)]

    def load(self, expirations: int = EXPIRATIONS) -> None:
        for stock in self.stocks:
            stock.populate_options(max_number=expirations)
            stock.populate_ratings()

    def calls(self, weights: dict[str, int] | None = None) -> dict[str, DataFrame]:
        return {
            stock.symbol: OptionsAnalyzer.summarize(stock.options.calls, weights)
            for stock in self.stocks
        }

    def ratings(self) -> DataFrame:
        return concat(
            stock.ratings_frame().assign(stock=stock.symbol) for stock in self.stocks
        ).reset_index(drop=True)


class Charts:
    COLUMNS: ClassVar[int] = 6
    PANEL: ClassVar[tuple[float, float]] = (3.4, 3.0)

    @classmethod
    def panels(cls, stocks: list[Stock]) -> Iterator[tuple[Axes, Stock]]:
        rows = ceil(len(stocks) / cls.COLUMNS)
        size = (cls.COLUMNS * cls.PANEL[0], rows * cls.PANEL[1])
        _, axes = subplots(rows, cls.COLUMNS, figsize=size, squeeze=False)
        for ax in axes.flat[len(stocks) :]:
            ax.set_visible(False)
        for ax, stock in zip(axes.flat, stocks, strict=False):
            ax.set_title(
                f"{stock.symbol} ({stock.info.get('currentPrice')}) "
                f"{stock.info.get('recommendationKey')}",
                fontsize=9,
            )
            yield ax, stock
