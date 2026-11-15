from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PriceRow(Base):
    __tablename__ = "prices"

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    open: Mapped[float | None]
    high: Mapped[float | None]
    low: Mapped[float | None]
    close: Mapped[float | None]
    volume: Mapped[float | None]
    dividends: Mapped[float | None]
    stock_splits: Mapped[float | None]


class OptionRow(Base):
    __tablename__ = "options"
    __table_args__ = (Index("options_symbol", "symbol", "snapshot_date"),)

    snapshot_date: Mapped[date] = mapped_column(Date, primary_key=True)
    contract_symbol: Mapped[str] = mapped_column(String, primary_key=True)
    symbol: Mapped[str]
    side: Mapped[str]
    expiration: Mapped[date] = mapped_column(Date)
    strike: Mapped[float]
    last_trade_date: Mapped[datetime | None]
    last_price: Mapped[float | None]
    bid: Mapped[float | None]
    ask: Mapped[float | None]
    change: Mapped[float | None]
    percent_change: Mapped[float | None]
    volume: Mapped[float | None]
    open_interest: Mapped[float | None]
    implied_volatility: Mapped[float | None]
    in_the_money: Mapped[bool | None]


class RatingRow(Base):
    __tablename__ = "ratings"

    snapshot_date: Mapped[date] = mapped_column(Date, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, primary_key=True)
    published: Mapped[date] = mapped_column(Date, primary_key=True)
    buy: Mapped[float | None]
    hold: Mapped[float | None]
    sell: Mapped[float | None]
