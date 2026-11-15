# research

Notebooks and scripts for running and exploring the packages, and for collecting data.

- `notebooks/` interactive work (`uv sync --all-packages`, then pick the `.venv` kernel)
- `scripts/`   repeatable runs
- `../data/`   collected output; gitignored except `.gitkeep` and the sample CSV

Plotting and Jupyter dependencies live in the root `research` dependency group,
so the packages under `packages/` stay free of them.

## Database

Collected data goes into SQLite (`data/mmp.db`, or `$MMP_DB`) through `foundation.persistence.Store`
(SQLAlchemy models, Alembic migrations).

In a notebook: `store = Store()`, then `store.load_prices("AAPL")`, or `with store.session() as s:`
for ORM queries. Schema changes: see `packages/foundation/README.md`.
