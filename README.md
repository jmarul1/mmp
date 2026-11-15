# mmp

Stock and options research: market data, analyst ratings and price prediction.

- `packages/foundation` downloads, entities, encoding, SQLite persistence
- `packages/stk_guide` pipeline, strategies and sklearn models
- `research/` notebooks
- `data/` collected data (gitignored)

Setup: `uv sync --all-packages`, then put `FINHUB_TOKEN=...` in `.env`.
