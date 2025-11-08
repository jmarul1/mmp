from datetime import datetime
from numbers import Number
from pandas import DataFrame
from stk_pred.entities.options import Options
from stk_pred.entities.price import Price
from stk_pred.entities.ratings import Ratings, RatingsEnum
from stk_pred.entities.stock import Stock


def test_stock(mock_downloads):
    stock = Stock(symbol="AAPL", company="Apple")
    assert stock.symbol == "AAPL"
    stock.populate(days_back=1, interval="1d", max_options=5)
    assert isinstance(stock.prices, list)
    assert len(stock.prices) == 2
    assert all(isinstance(price, Price) for price in stock.prices)
    assert isinstance(stock.options, Options)
    assert len(stock.options.calls) == 2
    assert len(stock.options.puts) == 2
    assert isinstance(stock.ratings, Ratings)
    assert stock.ratings.to_frame().shape == (2, 5)


def test_price():
    date = datetime.now()
    price = Price(date=date, close=10, open=11, volume=100)
    assert price.date == date
    assert price.close == 10 and price.open == 11 and price.volume == 100


def test_ratings():
    date = datetime.now()
    ratings = Ratings()
    ratings.add(date, 6, 2, 0, "robinhood")
    df = ratings.to_frame()
    assert isinstance(df, DataFrame)
    assert len(df) == 1
