from pathlib import Path
from typing import ClassVar

from alembic import command
from alembic.config import Config


class Migrator:
    SCRIPTS: ClassVar[Path] = Path(__file__).parent / "migrations"
    HEAD: ClassVar[str] = "head"

    @classmethod
    def upgrade(cls, url: str, revision: str = HEAD) -> None:
        config = Config()
        config.set_main_option("script_location", str(cls.SCRIPTS))
        config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
        command.upgrade(config, revision)
