import pytest
from pandas import DataFrame
from stk_pred.entities.stock import Stock
from stk_pred.ml.data.options_preprocess import OptionPreprocessor


def test_stock_populate_and_preprocess():
    stock = Stock(symbol="AAPL", company="Apple Inc.")
    stock.populate(days_back=5, interval="1d", max_options=10)
    preprocessor = OptionPreprocessor(options=stock.options)
    print(stock.options.calls)
    print(preprocessor.options_to_features(spot=150.0))
