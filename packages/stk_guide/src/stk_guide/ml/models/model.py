from abc import abstractmethod
from typing import Any, Self

from attrs import define, field
from foundation.cloning import ResetClone
from foundation.datatypes import DataType, NativeDataType, NativeKind
from foundation.encoding.encoder import Encoder
from pandas import DataFrame, Series


@define
class Model:
    preprocessor: Encoder = field(factory=Encoder, kw_only=True)
    _features_types: list[NativeKind] = field(init=False)
    _apimodel: Any = field(init=False)

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

    def data_type(self, test: NativeDataType) -> NativeKind:
        return DataType.get_type(test)

    def __str__(self) -> str:
        return str(self.__class__)

    def _check_features_types(self, features: DataFrame) -> bool:
        if len(self._features_types) != features.shape[1]:
            return False
        for orig, test in zip(
            self._features_types, DataType.get_type(features), strict=False
        ):
            if orig != test:
                return False
        return True

    @abstractmethod
    def train(self, features: DataFrame, labels: Series) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self, prefix_path: str) -> bool:
        raise NotImplementedError
