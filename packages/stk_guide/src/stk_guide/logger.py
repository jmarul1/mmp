import logging
import sys
from pathlib import Path
from typing import Self

import daiquiri

type LoggerObject = logging.LoggerAdapter


class Logger:
    _instance: Self | None = None
    _initialized: bool = False

    def __new__(
        cls,
        verbose_level: int = logging.INFO,
        logfile: Path | None = None,
        stdout: bool = True,
    ) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        verbose_level: int = logging.INFO,
        logfile: Path | None = None,
        stdout: bool = True,
    ) -> None:
        if not self._initialized:
            self.verbose_level = verbose_level
            self.logfile = logfile
            outputs: list[daiquiri.output.Output] = []
            if stdout:
                outputs += [
                    daiquiri.output.Stream(sys.stdout),
                    daiquiri.output.Stream(sys.stderr, level=logging.ERROR),
                ]
            if self.logfile:
                outputs.append(daiquiri.output.File(str(self.logfile)))
            daiquiri.setup(level=self.verbose_level, outputs=outputs)
            self._initialized = True

    def __call__(self, name: str) -> LoggerObject:
        return daiquiri.getLogger(name)
