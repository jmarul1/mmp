from collections.abc import Sequence
from datetime import datetime
from functools import singledispatchmethod
from numbers import Number
from typing import Any, overload

from pandas import DataFrame, Series

NativeDataType = datetime | str | bool | Number
# the class of a native value, e.g. `str`, as returned by `DataType.get_type`
NativeKind = type[NativeDataType]
# a column of values, as passed around between coders and encoders
ColumnData = Sequence[Any] | Series


class DataType:
    @overload
    @staticmethod
    def get_type(test: list | tuple | DataFrame | Series) -> list[NativeKind]: ...

    @overload
    @staticmethod
    def get_type(test: NativeDataType) -> NativeKind: ...

    @staticmethod
    def get_type(
        test: NativeDataType | list | tuple | DataFrame | Series,
    ) -> NativeKind | list[NativeKind]:
        return DataType()._get_type(test)  # pylint: disable = protected-access

    def _findout(self, test: NativeDataType) -> NativeKind:
        for check in [Number, str, bool, datetime]:
            if isinstance(test, check):
                return check
        raise ValueError(f"Unknown data type: {test}")

    @singledispatchmethod
    def _get_type(
        self, test: NativeDataType | list | tuple | DataFrame | Series
    ) -> NativeKind | list[NativeKind]:
        raise NotImplementedError

    @_get_type.register
    def _(self, test: NativeDataType) -> NativeKind:
        return self._findout(test)

    @_get_type.register
    def _(self, test: DataFrame) -> list[NativeKind]:
        return [self._findout(itest) for itest in test.iloc[0, :]]

    @_get_type.register
    def _(self, test: list | tuple | Series) -> list[NativeKind]:
        return [self._findout(itest) for itest in test]
