# research

Notebooks for running and exploring the packages.

- `notebooks/watchlist.ipynb` price projection from options and recommendation scores from analyst ratings (`uv sync --all-packages`, then pick the `.venv` kernel)
- `notebooks/watchlist.py` the `Watchlist` and `Charts` classes the notebook imports
- `../data/`   collected output; gitignored except `.gitkeep`

Plotting and Jupyter dependencies live in the root `research` dependency group,
so the packages under `packages/` stay free of them.

## Database

Collected data goes into SQLite (`data/mmp.db`, or `$MMP_DB`) through `foundation.persistence.Store`
(SQLAlchemy models, Alembic migrations).

In a notebook: `store = Store()`, then `store.load_prices("AAPL")`, or `with store.session() as s:`
for ORM queries. Schema changes: see `packages/foundation/README.md`.
