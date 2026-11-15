from typing import Any, Self

from numpy import array
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder

from ..cloning import ResetClone
from ..datatypes import ColumnData

EncoderApi = MinMaxScaler | OneHotEncoder | OrdinalEncoder


class CoderType:
    api: EncoderApi

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        self.options = options or {}

    def fit(self, data: ColumnData) -> Self:
        _data = array(data).reshape(-1, 1)
        self.api.fit(_data)
        return self

    def code(self, data: ColumnData) -> ColumnData:
        _data = array(data).reshape(-1, 1)
        edata = self.api.transform(_data)
        return edata.squeeze().tolist()

    def fit_code(self, data: ColumnData) -> ColumnData:
        self.fit(data)
        return self.code(data)

    def clone_reset(self) -> Self:
        return ResetClone().clone_reset(self)


class OrdinalCoder(CoderType):
    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.api = OrdinalEncoder(**self.options)


class MinMaxCoder(CoderType):
    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.api = MinMaxScaler(**self.options)


class IdentityCoder(CoderType):
    def fit(self, data: ColumnData) -> Self:
        return self

    def code(self, data: ColumnData) -> ColumnData:
        return data


class DatetimeCoder(CoderType):
    def fit(self, data: ColumnData) -> Self:
        return self

    def code(self, data: ColumnData) -> ColumnData:
        return [idata.timestamp() for idata in data]


class OneHotCoder(CoderType):
    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.api = OneHotEncoder(**self.options)

    def code(self, data: ColumnData) -> ColumnData:
        _data = array(data).reshape(-1, 1)
        edata = self.api.transform(_data)
        return edata.toarray().tolist()
