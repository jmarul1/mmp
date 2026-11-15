from dataclasses import dataclass

from ..pipeline.stages.collecting import Collector
from ..pipeline.stages.predicting import Predictor
from ..pipeline.stages.preprocessing import Preprocessor
from ..pipeline.stages.training import Trainer


@dataclass(kw_only=True)
class PipelineStages:
    collector: Collector | None = None
    preprocessor: Preprocessor | None = None
    trainer: Trainer | None = None
    predictor: Predictor | None = None
