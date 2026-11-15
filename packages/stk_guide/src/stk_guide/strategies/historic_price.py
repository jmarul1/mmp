from datetime import datetime, timedelta

from dateutil.tz import gettz
from foundation.download.download_enum import TimeZone
from foundation.download.downloader import PriceHistory
from foundation.encoding.algorithms import MinMaxCoder
from foundation.encoding.encoder import Encoder
from foundation.entities.prices import PricesEnum
from foundation.market.stock import Stock
from pandas import DataFrame, concat

from ..pipeline.pipeline import Pipeline
from ..pipeline.pipeline_stages import PipelineStages
from ..pipeline.prediction import Prediction
from ..pipeline.stages.collecting import PriceCollector
from .strategy import Strategy


class HistoricPrice(Strategy):
    pipeline: Pipeline

    def __init__(self, pipeline_stages: PipelineStages) -> None:
        self.pipeline_stages = pipeline_stages

    def __call__(
        self,
        stock: Stock,
        days_back: int,
        days_fwd: int,
        interval: str = PriceHistory.INTERVAL,
    ) -> Prediction:
        stock.populate_prices(days_back=days_back, interval=interval)
        history = stock.prices.features()
        tz = gettz(TimeZone.DEFAULT.value)
        projection = DataFrame(
            {
                PricesEnum.DATETIME.value: [
                    datetime.now(tz) + timedelta(hours=ihr)
                    for ihr in range(days_fwd * 24)
                ]
            }
        )
        self.pipeline = Pipeline()
        self.pipeline.context.stock = stock
        self.pipeline.context.preprocessor = self.setup_preprocessor(
            history, projection
        )
        self.pipeline.add(PriceCollector(), days_back=days_back, interval=interval)
        self.pipeline.add(self.pipeline_stages.trainer)
        self.pipeline.add(self.pipeline_stages.predictor, future_space=projection)
        self.pipeline.execute()
        return self.pipeline.context

    def setup_preprocessor(self, history: DataFrame, projection: DataFrame) -> Encoder:
        preprocessor = Encoder(
            feature_scalers={PricesEnum.DATETIME.value: MinMaxCoder()}
        )
        data = concat([history, projection])
        return preprocessor.fit(data)
