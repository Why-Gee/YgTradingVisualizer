# CLAUDE.md — YgTradingVisualizer (Repo A)

## Repo purpose

Generic, source-agnostic trading-performance visualization layer. Renders any producer's `ygperf`
reports via reusable chart components and a Dash shell. **This repo must stay source-agnostic.**
No cerebrum or strategy-specific logic lives here.

## 3-repo boundary

| Repo | Role |
|---|---|
| **YgTradingVisualizer** (this repo, Repo A) | Generic contract, components, sources, Dash app |
| **YgCerebrumVisualizer** (Repo B) | Cerebrum bridge — `CerebrumBacktestSource`, cerebrum pages |
| **Cerebrum producer** (Repo C) | Emits `ygperf` reports from cerebrum backtests / live bot |

Rule: if code mentions cerebrum, a strategy name, or a specific data provider, it belongs in Repo B
or C, not here.

## uv workspace layout

```
TradingVisualizer/
├── pyproject.toml            # workspace root (package=false); ruff + pytest config
├── packages/
│   ├── contract/             # dist: ygperf      — PerfReport contract, pure polars
│   ├── components/           # dist: ygtv-components — PerfReport → go.Figure factories
│   └── sources/              # dist: ygtv-sources  — Source protocol, DirectorySource, LiveSource
└── app/                      # dist: ygtv-app      — generic Dash shell
```

All packages share the `ygtv` PEP-420 namespace (no `ygtv/__init__.py` at the namespace root).
`ygperf` is its own top-level package — it is the source-agnostic contract any producer can import
without pulling in Plotly or Dash.

## Running tests

Run a single package:
```bash
uv run --package ygperf pytest packages/contract/
uv run --package ygtv-components pytest packages/components/
uv run --package ygtv-sources pytest packages/sources/
uv run --package ygtv-app pytest app/
```

Run the whole workspace:
```bash
uv run pytest
```

## CI gate (must be green before merging)

```bash
uv run ruff check .          # lint: E, F, I, B, UP, RUF, PT; line-length 100
uv run ruff format --check . # format check
uv run pytest                # all 19+ tests
```

Both `ruff check` AND `ruff format --check` must pass. Run `uv run ruff format .` locally to fix
formatting before committing.

## Namespace conventions

- `ygtv.*` — PEP-420 namespace for all visualization packages (components, sources, app).
  No `packages/components/src/ygtv/__init__.py`, `packages/sources/src/ygtv/__init__.py`, or
  `app/src/ygtv/__init__.py` at the `ygtv/` level — hatchling discovers sub-packages directly.
- `ygperf` — standalone top-level contract package. Import as `from ygperf.report import PerfReport`.
  Any producer (backtest, bot) can depend on `ygperf` without pulling in Dash or Plotly.

## Key architectural rules

- `PerfSeries` is realized as a `pl.DataFrame` with fixed columns `timestamp`, `equity`, `returns`
  (no wrapper class — YAGNI).
- Component factories (`equity_curve`, `drawdown_curve`, `rolling_sharpe`,
  `monthly_returns_heatmap`) accept `PerfReport` and return `go.Figure` with zero source knowledge.
- `Source` is a `runtime_checkable` Protocol — `runs() -> pl.DataFrame`,
  `report(run_id) -> PerfReport`. New sources implement only these two methods.
- `app.server` (Flask) is always exposed by `build_app(source)` for gunicorn/deploy.

## Windows / polars tz pitfall

`polars` on Windows panics when materializing tz-aware `Datetime` columns to Python objects
(`.to_dicts()`, `.row()`, `.to_list()`) if the `tzdata` package is absent. `tzdata` is in the root
`dev` dependency group as a safety net. The Overview page explicitly converts tz-aware columns to
display strings before calling `to_dicts()` — do not remove that guard.

## Syncing and reinstalling

After adding new source files to a workspace package, reinstall it:
```bash
uv sync --reinstall-package ygtv-app   # or whichever package changed
```

Add new workspace packages to root `pyproject.toml`:
- `[tool.uv.workspace] members`
- `[tool.uv.sources]` (if consumed by other packages)
- `[dependency-groups] dev` (so CI picks it up)
