from abc import abstractmethod
from typing import Any, Self

from foundation.cloning import ResetClone
from foundation.datatypes import DataType, NativeKind
from foundation.encoding.encoder import Encoder
from pandas import DataFrame, Series


class Model:
    _features_types: list[NativeKind]
    _apimodel: Any

    def __init__(self, *, preprocessor: Encoder | None = None) -> None:
        self.preprocessor = preprocessor or Encoder()

    def predict(self, features: DataFrame) -> Series:
        if not self._check_features_types(features):
            raise ValueError(
                "Predicting features shape/types must match that of training"
            )
        _features = self.preprocessor(features)
        preds = self._apimodel.predict(_features)
        return Series(preds.squeeze().reshape(-1), name=str(self))

    def clone_reset(self) -> Self:
        return ResetClone().clone_reset(self)

    def __str__(self) -> str:
        return str(self.__class__)

    def _check_features_types(self, features: DataFrame) -> bool:
        if len(self._features_types) != features.shape[1]:
            return False
        return self._features_types == DataType.get_type(features)

    @abstractmethod
    def train(self, features: DataFrame, labels: Series) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self, prefix_path: str) -> bool:
        raise NotImplementedError
