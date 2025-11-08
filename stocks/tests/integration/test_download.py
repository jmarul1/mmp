from datetime import date
from numbers import Number
from pandas import DataFrame
from stk_pred.download.downloader import (
    PriceHistory,
    StockOptions,
    StockInfo,
    FinhubRating,
    RobinhoodRatings,
)


def test_price() -> None:
    test = PriceHistory(symbol="INTC", days_back=5, interval="1d").download()
    assert isinstance(test, DataFrame)
    assert not test.empty


def test_info() -> None:
    data = StockInfo(symbol="INTC").download()
    assert isinstance(data, dict)


def test_options() -> None:
    data = StockOptions(symbol="INTC").download()
    assert isinstance(data, tuple)
    assert isinstance(data[0], DataFrame)
    assert isinstance(data[1], DataFrame)
    assert not data[0].empty
    assert not data[1].empty


def test_ratings() -> None:
    datas = [
        RobinhoodRatings(symbol="AAPL").download(),
        FinhubRating(symbol="AAPL").download(),
    ]
    for data in datas:
        assert isinstance(data, list), data.symbol
        assert isinstance(data[0], tuple), data.symbol
        assert isinstance(data[0][0], date), data.symbol
        assert all(isinstance(val, Number) for val in data[0][1:-1]), data.symbol
