from enum import StrEnum, auto
import pandas as pd
from stk_pred.entities.options import Options, OptionsEnum
from stk_pred.ml.data.preprocess import Preprocess


class OptionsPreprocessEnum(StrEnum):
    PUT_CALL_VOLUME_RATIO = auto()
    PUT_CALL_OI_RATIO = auto()
    AVG_IV_CALLS = auto()
    AVG_IV_PUTS = auto()
    VWAP_STRIKE_CALLS = auto()
    VWAP_STRIKE_PUTS = auto()
    SPOT = auto()


class OptionPreprocessor(Preprocess):
    options: Options

    def options_to_features(self, spot: float) -> pd.DataFrame:
        features = {
            OptionsPreprocessEnum.PUT_CALL_VOLUME_RATIO: self.options.puts[
                OptionsEnum.VOLUME
            ].sum()
            / max(self.options.calls[OptionsEnum.VOLUME].sum(), 1),
            OptionsPreprocessEnum.PUT_CALL_OI_RATIO: self.options.puts[
                OptionsEnum.OPENINTEREST
            ].sum()
            / max(self.options.calls[OptionsEnum.OPENINTEREST].sum(), 1),
            OptionsPreprocessEnum.AVG_IV_CALLS: self.options.calls[
                OptionsEnum.IMPLIEDVOLATILITY
            ].mean(),
            OptionsPreprocessEnum.AVG_IV_PUTS: self.options.puts[
                OptionsEnum.IMPLIEDVOLATILITY
            ].mean(),
            OptionsPreprocessEnum.VWAP_STRIKE_CALLS: (
                self.options.calls[OptionsEnum.STRIKE]
                * self.options.calls[OptionsEnum.VOLUME]
            ).sum()
            / max(self.options.calls[OptionsEnum.VOLUME].sum(), 1),
            OptionsPreprocessEnum.VWAP_STRIKE_PUTS: (
                self.options.puts[OptionsEnum.STRIKE]
                * self.options.puts[OptionsEnum.VOLUME]
            ).sum()
            / max(self.options.puts[OptionsEnum.VOLUME].sum(), 1),
            OptionsPreprocessEnum.SPOT: spot,
        }
        return features
