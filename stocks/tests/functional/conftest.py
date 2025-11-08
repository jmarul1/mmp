from datetime import datetime
from pandas import DataFrame
import pytest


@pytest.fixture
def mock_downloads(monkeypatch):
    from stk_pred.download.downloader import PriceHistory
    from stk_pred.download.downloader import StockOptions
    from stk_pred.download.downloader import RobinhoodRatings, FinhubRating

    def mock_price_download(self):
        return DataFrame(
            {
                "date": [datetime.now(), datetime.now()],
                "Close": [100, 101],
                "Open": [110, 111],
                "Volume": [1000, 1001],
            }
        )

    def mock_options_download(self):
        calls = DataFrame(
            {
                "strike": [150, 155],
                "bid": [2.5, 2.0],
                "ask": [3.0, 2.5],
                "volume": [100, 150],
                "openInterest": [200, 250],
                "impliedVolatility": [0.25, 0.30],
                "percentChange": [1.5, -0.5],
                "expiration": [datetime.now(), datetime.now()],
            }
        )
        puts = DataFrame(
            {
                "strike": [145, 140],
                "bid": [2.0, 1.5],
                "ask": [2.5, 2.0],
                "volume": [120, 130],
                "openInterest": [220, 230],
                "impliedVolatility": [0.28, 0.32],
                "percentChange": [-1.0, 0.5],
                "expiration": [datetime.now(), datetime.now()],
            }
        )
        return calls, puts

    monkeypatch.setattr(
        RobinhoodRatings,
        "download",
        lambda *args, **kwargs: [(datetime.now(), 1, 0, 0, "robinhood")],
    )
    monkeypatch.setattr(
        FinhubRating,
        "download",
        lambda *args, **kwargs: [(datetime.now(), 1, 0, 0, "finhub")],
    )
    monkeypatch.setattr(StockOptions, "download", mock_options_download)
    monkeypatch.setattr(PriceHistory, "download", mock_price_download)
