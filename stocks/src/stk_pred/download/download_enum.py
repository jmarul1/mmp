from enum import StrEnum, auto


class RobinhoodEnum(StrEnum):
    SUMMARY = "summary"
    NEWS = "ratings"
    BUY = "num_buy_ratings"
    HOLD = "num_hold_ratings"
    SELL = "num_sell_ratings"
    PUBLISHED = "ratings_published_at"


class FinhubEnum(StrEnum):
    BUY = "buy"
    STRONG_BUY = "strongBuy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strongSell"
    PUBLISHED = "period"


class OptionsEnum(StrEnum):
    EXPIRATION = "expiration"
    STRIKE = "strike"
    BID = "bid"
    ASK = "ask"
    LAST = "last"


class StockInfoEnum(StrEnum):
    PE_RATIO = "trailingPegRatio"
    REVENUE_GROWTH = "revenueGrowth"
    MARKET_CAP = "marketCap"


class TimeZone(StrEnum):
    DEFAULT = "America/New_York"
