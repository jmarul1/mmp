# foundation

Shared code for the other packages: how market data flows from download to model input.

- `download/` prices, option chains and analyst ratings (yfinance, Finnhub, Robinhood)
- `entities/` Stock, Prices, Options, Rating, Prediction
- `encoding/` DataFrame columns to numeric input
- `persistence/` SQLite store (SQLAlchemy models, Alembic migrations)
- `datatypes.py`, `cloning.py` value type detection, unfitted object copies

The database is `data/mmp.db` or `$MMP_DB`; datetimes are stored as naive UTC. `Store()` applies pending migrations on open.

New migration after editing `persistence/models.py`:

    uv run --package foundation alembic -c packages/foundation/alembic.ini revision --autogenerate -m "message"
