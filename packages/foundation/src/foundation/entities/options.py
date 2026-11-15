from enum import StrEnum, auto
from numbers import Number
from typing import Any

from numpy import mean
from pandas import DataFrame

from ..encoding.algorithms import MinMaxCoder
from ..encoding.encoder import Encoder


class OptionsEnum(StrEnum):
    EXPIRATION = auto()
    BID = auto()
    ASK = auto()
    IMPLIEDVOLATILITY = "impliedVolatility"
    OPENINTEREST = "openInterest"
    PERCENTCHANGE = "percentChange"
    VOLUME = auto()
    PROJECTED_PRICE_v0 = auto()
    PROJECTED_PRICE_v1 = auto()
    STRIKE = auto()
    SCORES = auto()


class Options:
    def __init__(self, calls: DataFrame, puts: DataFrame) -> None:
        self.calls = calls
        self.puts = puts

    def sumarize_calls(self, weights: int | dict[str, int] = 1) -> DataFrame:
        return self._summarize(self.calls, weights)

    def sumarize_puts(self, weights: int | dict[str, int] = 1) -> DataFrame:
        return self._summarize(self.puts, weights)

    def _summarize(self, chain: DataFrame, weights: int | dict[str, int]) -> DataFrame:
        keys_weights = self._keys_weights(weights)
        return DataFrame(
            self.summarize_data(group, keys_weights)
            for _, group in chain.groupby(OptionsEnum.EXPIRATION.value)
        )

    @staticmethod
    def summarize_data(
        options_data: DataFrame, keys_weights: dict[str, int]
    ) -> dict[str, Number | str]:
        _data: dict[Any, Any] = {}
        _options_data = options_data.dropna()
        keys, weights = list(keys_weights), list(keys_weights.values())
        iscores = Encoder(
            feature_scalers={name: MinMaxCoder() for name in keys}
        ).fit_transform(_options_data.loc[:, keys])
        if OptionsEnum.IMPLIEDVOLATILITY in iscores:
            iscores[OptionsEnum.IMPLIEDVOLATILITY.value] = (
                1 - iscores[OptionsEnum.IMPLIEDVOLATILITY.value]
            )
        scores = (iscores * weights).sum(axis=1)
        for name, values in _options_data.items():
            if isinstance(values.iloc[0], Number):
                _data[name] = mean(values)
            else:
                _data[name] = values.iloc[0]
        projected = (
            _options_data[OptionsEnum.STRIKE.value]
            + _options_data[OptionsEnum.ASK.value]
        )
        total = scores.sum()
        _data[OptionsEnum.PROJECTED_PRICE_v0.value] = (
            (projected * scores).sum() / total if total > 0 else 0
        )
        ranked = DataFrame({"projected": projected, "scores": scores}).sort_values(
            "scores", ascending=False
        )
        _data[OptionsEnum.PROJECTED_PRICE_v1.value] = ranked["projected"].iloc[0]
        return _data

    def _keys_weights(self, weights: int | dict[str, int]) -> dict[str, int]:
        keys = [
            OptionsEnum.BID.value,
            OptionsEnum.ASK.value,
            OptionsEnum.OPENINTEREST.value,
            OptionsEnum.VOLUME.value,
            OptionsEnum.IMPLIEDVOLATILITY.value,
            OptionsEnum.PERCENTCHANGE.value,
        ]
        if isinstance(weights, dict):
            for key in weights:
                if key not in keys:
                    raise ValueError(f"Provided weights are wrong: {weights}")
        return {
            key: (weights[key] if isinstance(weights, dict) and key in weights else 1)
            for key in keys
        }
