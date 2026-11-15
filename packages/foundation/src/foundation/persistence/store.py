from collections.abc import Iterable
from datetime import UTC, date, datetime
from os import environ
from pathlib import Path
from typing import Any, ClassVar, Self, cast

from pandas import DataFrame, Timestamp, notna, read_sql_query, to_datetime
from sqlalchemy import Engine, Table, create_engine, event, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Session

from ..entities.options import Options
from ..entities.prices import Prices
from ..entities.rating import Rating
from .migrate import Migrator
from .models import OptionRow, PriceRow, RatingRow


class Store:
    ENV_VAR: ClassVar[str] = "MMP_DB"
    DATA_DIR: ClassVar[str] = "data"
    FILENAME: ClassVar[str] = "mmp.db"

    def __init__(
        self, path: str | Path | None = None, *, migrate_db: bool = True
    ) -> None:
        self.path = Path(path) if path is not None else self.default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine: Engine = create_engine(f"sqlite:///{self.path}")
        event.listen(self.engine, "connect", self._on_connect)
        if migrate_db:
            Migrator.upgrade(self.engine.url.render_as_string(hide_password=False))

    @classmethod
    def default_path(cls) -> Path:
        """Return the database path from the environment variable when set, otherwise the data folder of the nearest parent workspace that has a pyproject.toml and a data directory, falling back to the current directory."""
        if cls.ENV_VAR in environ:
            return Path(environ[cls.ENV_VAR])
        for folder in (Path.cwd(), *Path.cwd().parents):
            if (folder / "pyproject.toml").is_file() and (
                folder / cls.DATA_DIR
            ).is_dir():
                return folder / cls.DATA_DIR / cls.FILENAME
        return Path.cwd() / cls.DATA_DIR / cls.FILENAME

    @staticmethod
    def clean(value: Any) -> Any:
        """Convert a value for SQLite storage: NaN and NaT become None, timezone-aware datetimes become naive UTC, and numpy scalars become plain Python values, so SQLAlchemy can bind them directly."""
        if value is None or not notna(value):
            return None
        if isinstance(value, Timestamp):
            value = value.to_pydatetime()
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                value = value.astimezone(UTC).replace(tzinfo=None)
            return value
        if hasattr(value, "item"):
            return value.item()
        return value

    @staticmethod
    def _on_connect(dbapi_conn: Any, _record: Any) -> None:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    def session(self) -> Session:
        return Session(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _upsert(self, model: type[DeclarativeBase], rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        table = cast(Table, model.__table__)
        keys = [column.name for column in table.primary_key]
        stmt = insert(table)
        stmt = stmt.on_conflict_do_update(
            index_elements=keys,
            set_={
                column.name: stmt.excluded[column.name]
                for column in table.columns
                if column.name not in keys
            },
        )
        with self.engine.begin() as conn:
            conn.execute(stmt, rows)
        return len(rows)

    def save_prices(self, symbol: str, prices: Prices) -> int:
        rows = [
            {
                "symbol": symbol,
                **{k: self.clean(v) for k, v in bar.model_dump().items()},
            }
            for bar in prices.bars
        ]
        return self._upsert(PriceRow, rows)

    def load_prices(self, symbol: str) -> DataFrame:
        stmt = select(PriceRow).where(PriceRow.symbol == symbol).order_by(PriceRow.ts)
        df = read_sql_query(stmt, self.engine)
        df["ts"] = to_datetime(df["ts"], utc=True)
        return df.set_index("ts").drop(columns="symbol")

    def save_options(
        self, symbol: str, options: Options, snapshot: date | None = None
    ) -> int:
        rows = [
            {
                "snapshot_date": snapshot or date.today(),
                "symbol": symbol,
                **{k: self.clean(v) for k, v in contract.model_dump().items()},
            }
            for contract in options.contracts
        ]
        return self._upsert(OptionRow, rows)

    def load_options(
        self, symbol: str, snapshot: date | None = None, side: str | None = None
    ) -> DataFrame:
        stmt = select(OptionRow).where(OptionRow.symbol == symbol)
        if snapshot is not None:
            stmt = stmt.where(OptionRow.snapshot_date == snapshot)
        if side is not None:
            stmt = stmt.where(OptionRow.side == side)
        stmt = stmt.order_by(
            OptionRow.snapshot_date, OptionRow.expiration, OptionRow.strike
        )
        return read_sql_query(stmt, self.engine)

    def save_ratings(
        self,
        symbol: str,
        source: str,
        ratings: Iterable[Rating],
        snapshot: date | None = None,
    ) -> int:
        snapshot = snapshot or date.today()
        rows = [
            {
                "snapshot_date": snapshot,
                "symbol": symbol,
                "source": source,
                "published": rating.date,
                "buy": rating.buy,
                "hold": rating.hold,
                "sell": rating.sell,
            }
            for rating in ratings
        ]
        return self._upsert(RatingRow, rows)

    def load_ratings(self, symbol: str, source: str | None = None) -> DataFrame:
        stmt = select(RatingRow).where(RatingRow.symbol == symbol)
        if source is not None:
            stmt = stmt.where(RatingRow.source == source)
        stmt = stmt.order_by(RatingRow.snapshot_date, RatingRow.published)
        return read_sql_query(stmt, self.engine)
