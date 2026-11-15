# mmp

uv workspace (Python 3.15): `packages/foundation` (shared data flow and SQLite persistence), `packages/stk_guide` (models and pipeline pieces used by notebooks); `research/` for notebooks; `data/` and `work/` are gitignored.

## Current phase: refactor only
- Keep new code to a minimum. Moves, renames, typing and lint fixes are in scope; new features and behavior changes are not.
- If you find a bug or an obvious improvement, note it in one line and leave it for later.
- Add new modules or scripts only when asked, as small as the request allows.

## Conventions
- Shared code goes in `foundation`, never `stk_guide`. No folders named `utils`.
- No model training here: no tensorflow, keras or torch (sklearn models are fine).

## Checks
- `uv sync --all-packages`
- `uv run ruff check packages/*/src && uv run ruff format --check packages/*/src`
- `uv run ty check`
