from typing import Any, Self

from ..logger import Logger, LoggerObject
from .context import Context
from .stages.stage import Stage


class Pipeline(list):
    def __init__(self, context: Context | None = None) -> None:
        super().__init__()
        self.context = context if context is not None else Context()
        self._logger: LoggerObject = Logger()(__name__)

    def execute(self) -> None:
        for idx, (stage, kwargs) in enumerate(self, start=1):
            self._logger.debug(f"Running {stage} {idx}/{len(self)}")
            stage(context=self.context, **kwargs)

    def add(self, stage: Stage, **kwargs: Any) -> None:
        self.append((stage, kwargs))

    def append(self, stage_pkg: tuple[Stage, dict]) -> None:
        self._validate(stage_pkg)
        super().append(stage_pkg)

    def _validate(self, stage_pkg: tuple[Stage, dict]) -> None:
        if (
            len(stage_pkg) != 2
            or not isinstance(stage_pkg[0], Stage)
            or not isinstance(stage_pkg[1], dict)
        ):
            raise ValueError(f"Arguments passed are of the wrong type: {stage_pkg}")

    def insert(self, index: int, stage: Stage) -> None:
        self._validate(stage)
        super().insert(index, stage)

    def __setitem__(self, index: int, stage: Stage) -> None:
        self._validate(stage)
        super().__setitem__(index, stage)

    def __iadd__(self, stage: Stage) -> Self:
        self.append(stage)
        return self

    def __add__(self, iterable: Self) -> Self:
        new_pipeline = Pipeline(self)
        for stage in iterable:
            new_pipeline += stage
        return new_pipeline
