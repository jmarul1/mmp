from foundation.datatypes import DataType
from pandas import DataFrame, Series
from sklearn.ensemble import GradientBoostingRegressor

from .model import Model


class GbrModel(Model):
    _apimodel: GradientBoostingRegressor

    def train(self, features: DataFrame, labels: Series) -> None:
        self._features_types = DataType.get_type(features)
        _features = self.preprocessor(features)
        self._apimodel = GradientBoostingRegressor()
        self._apimodel.fit(_features, labels)

    def save(self, prefix_path: str) -> bool:
        pass
