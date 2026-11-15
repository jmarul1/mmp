from numbers import Number
from typing import Any, ClassVar

from numpy import mean
from pandas import DataFrame

from ..encoding.algorithms import MinMaxCoder
from ..encoding.encoder import Encoder
from ..entities.options import OptionsEnum


class OptionsAnalyzer:
    SCORED: ClassVar[list[str]] = [
        OptionsEnum.BID.value,
        OptionsEnum.ASK.value,
        OptionsEnum.OPENINTEREST.value,
        OptionsEnum.VOLUME.value,
        OptionsEnum.IMPLIEDVOLATILITY.value,
        OptionsEnum.PERCENTCHANGE.value,
    ]
    DEFAULT_WEIGHT: ClassVar[int] = 1

    @classmethod
    def summarize(
        cls, chain: DataFrame, weights: dict[str, int] | None = None
    ) -> DataFrame:
        weights = weights or {}
        if set(weights) - set(cls.SCORED):
            raise ValueError(f"Provided weights are wrong: {weights}")
        keys_weights = {key: weights.get(key, cls.DEFAULT_WEIGHT) for key in cls.SCORED}
        return DataFrame(
            cls.summarize_expiration(group, keys_weights)
            for _, group in chain.groupby(OptionsEnum.EXPIRATION.value)
        )

    @staticmethod
    def summarize_expiration(
        chain: DataFrame, keys_weights: dict[str, int]
    ) -> dict[Any, Any]:
        """Average one expiration's contracts and project two prices from strike plus ask: v0 is the score-weighted mean, v1 the top-scored contract, where scores are min-max scaled liquidity, inverted volatility and price change."""
        data = chain.dropna().reset_index(drop=True)
        keys, weights = list(keys_weights), list(keys_weights.values())
        iscores = Encoder(
            feature_scalers={k: MinMaxCoder() for k in keys}
        ).fit_transform(data.loc[:, keys])
        if OptionsEnum.IMPLIEDVOLATILITY in iscores:
            iscores[OptionsEnum.IMPLIEDVOLATILITY.value] = (
                1 - iscores[OptionsEnum.IMPLIEDVOLATILITY.value]
            )
        scores = (iscores * weights).sum(axis=1)
        summary = {
            name: mean(values) if isinstance(values.iloc[0], Number) else values.iloc[0]
            for name, values in data.items()
        }
        projected = data[OptionsEnum.STRIKE.value] + data[OptionsEnum.ASK.value]
        total = scores.sum()
        summary[OptionsEnum.PROJECTED_PRICE_v0.value] = (
            (projected * scores).sum() / total if total > 0 else 0
        )
        ranked = DataFrame({"projected": projected, "scores": scores}).sort_values(
            "scores", ascending=False
        )
        summary[OptionsEnum.PROJECTED_PRICE_v1.value] = ranked["projected"].iloc[0]
        return summary
