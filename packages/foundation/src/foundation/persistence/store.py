from collections.abc import Iterable
from datetime import UTC, date, datetime
from os import environ
from pathlib import Path
from typing import Any, Self, cast

from pandas import DataFrame, Timestamp, notna, read_sql_query, to_datetime
from sqlalchemy import Engine, Table, create_engine, event, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Session

from ..entities.options import Options
from ..entities.prices import Prices
from ..entities.rating import Rating
from .migrate import migrate
from .models import OptionRow, PriceRow, RatingRow

OPTION_COLUMNS = {
    "contractSymbol": "contract_symbol",
    "expiration": "expiration",
    "strike": "strike",
    "lastTradeDate": "last_trade_date",
    "lastPrice": "last_price",
    "bid": "bid",
    "ask": "ask",
    "change": "change",
    "percentChange": "percent_change",
    "volume": "volume",
    "openInterest": "open_interest",
    "impliedVolatility": "implied_volatility",
    "inTheMoney": "in_the_money",
}
PRICE_COLUMNS = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
    "Dividends": "dividends",
    "Stock Splits": "stock_splits",
}


def default_db_path() -> Path:
    """Return $MMP_DB if set, else data/mmp.db in the workspace root (found by its pyproject.toml)."""
    if "MMP_DB" in environ:
        return Path(environ["MMP_DB"])
    for folder in (Path.cwd(), *Path.cwd().parents):
        if (folder / "pyproject.toml").is_file() and (folder / "data").is_dir():
            return folder / "data" / "mmp.db"
    return Path.cwd() / "data" / "mmp.db"


def _clean(value: Any) -> Any:
    """Convert a value for SQLite: NaN to None, datetimes to naive UTC, numpy scalars to Python."""
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


def _as_date(value: Any) -> date:
    value = _clean(value)
    return value.date() if isinstance(value, datetime) else value


class Store:
    def __init__(
        self, path: str | Path | None = None, *, migrate_db: bool = True
    ) -> None:
        self.path = Path(path) if path is not None else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine: Engine = create_engine(f"sqlite:///{self.path}")
        event.listen(self.engine, "connect", self._on_connect)
        if migrate_db:
            migrate(self.engine.url.render_as_string(hide_password=False))

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
                "ts": _clean(ts),
                **{col: _clean(entry.get(key)) for key, col in PRICE_COLUMNS.items()},
            }
            for ts, entry in prices.items()
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
        snapshot = snapshot or date.today()
        saved = 0
        for side, chain in (("call", options.calls), ("put", options.puts)):
            if chain is None or chain.empty:
                continue
            chain = chain.reindex(columns=list(OPTION_COLUMNS))
            rows = []
            for values in chain.itertuples(index=False, name=None):
                row = {
                    col: _clean(value)
                    for col, value in zip(OPTION_COLUMNS.values(), values, strict=True)
                }
                row["expiration"] = _as_date(row["expiration"])
                rows.append(
                    {"snapshot_date": snapshot, "symbol": symbol, "side": side, **row}
                )
            saved += self._upsert(OptionRow, rows)
        return saved

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
                "published": _as_date(rating.date),
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
