# YgTradingVisualizer — Design Spec

**Date:** 2026-06-03 · **Status:** approved-for-planning · **Owner:** Yaniv (Why-Gee)
**Source:** `handoff-ygtradingvisualizer-2026-06-03.md` (cerebrum design session) + this session's Q-resolution.

---

## 1. Goal

A **reusable, source-agnostic trading-performance visualization layer** (Plotly Dash) that renders
strategy results for **any** producer — cerebrum backtests/evals now, the live PolymarketTraderBot
later, future apps (`YgStocksAInvestor`) thereafter — without re-implementing charts per consumer.

The whole design turns on one principle: **separate the *what* (a shared, source-agnostic data
contract + reusable chart components) from the *where shown* (an app shell), so that backtest vs.
live vs. any-future-source differ ONLY in a thin data-source adapter.**

## 2. Three-repo architecture

A deliberate split so the generic layer NEVER imports anything producer-specific.

### Repo A — `Why-Gee/YgTradingVisualizer` (generic; THIS repo, `…\TradingVisualizer`)

uv workspace. Source-agnostic. Knows nothing about cerebrum.

| package | dist | role | deps |
|---|---|---|---|
| `packages/contract` | **`ygperf`** | `PerfReport` schema + `write_report`/`read_report` + `schema_version`. The spine. | `polars` (+ stdlib `dataclasses`) |
| `packages/components` | `ygtv-components` | pure `PerfReport → plotly.graph_objects.Figure` factories. **The reuse core the bot imports.** | `ygperf`, `plotly` |
| `packages/sources` | `ygtv-sources` | `Source` protocol + generic `DirectorySource` (reads contract artifacts from a dir/glob/`hf://`) + `LiveSource` (file-poll stub). | `ygperf`, `polars`, `[hf]`→`huggingface_hub` |
| `app/` | (not published) | generic multipage Dash shell, parameterized by an injected `Source`. | `dash`, `dash-bootstrap-components`, `ygtv-components`, `ygtv-sources`, `[quantstats]` |

`ygperf` is **neutrally named on purpose** — it is not visualization-specific and not
cerebrum-specific; it is the contract every producer and consumer agrees on.

### Repo B — `Why-Gee/YgCerebrumVisualizer` (the cerebrum bridge; `…\CerebrumVisualizer`)

The **only** place cerebrum-awareness lives. Depends on Repo A. Delivered via its **own handoff**.

- `CerebrumBacktestSource(Source)` — reads cerebrum's emitted `PerfReport`s (git `docs/eval/runs/`
  JSON + HF parquet sidecars), indexed by git SHA → feeds the generic regression view.
- Runnable cerebrum dashboard entrypoint + cerebrum-specific pages (THE-NUMBER, factor attribution
  tuned to cerebrum's `extras`).

### Repo C — cerebrum `Why-Gee/YgTradingCerebrum` (producer; external)

Pure library, stays UI-free. Delivered via its **own handoff**. Adds a `ygperf` dependency and emits
`PerfReport` from the canonical evals (`write_report()` + git-SHA capture + the run-store convention).
No charts, no Dash — emission only, preserving cerebrum's pure-library boundary.

**Boundary test for "is the visualizer cerebrum-specific?":** No. Repo A + the bot reuse path never
import cerebrum. All cerebrum knowledge is isolated in Repo B. A new producer = a new sibling bridge
repo; Repo A is untouched.

## 3. The `ygperf` contract

One `PerfReport` per run. Pure data; deps = `dataclasses` + `polars` only (no plotly/dash, so any
producer — including pure-library cerebrum and the bot — can import it freely).

```python
SCHEMA_VERSION = "1.0"

@dataclass(frozen=True)
class PerfReport:
    schema_version: str                 # SCHEMA_VERSION — guards forward-compat
    run_id: str                         # deterministic: hash(git_sha, eval_name, run_ts)
    run_ts: datetime                    # tz-aware, local
    git_sha: str                        # producer HEAD at run time — the regression x-axis
    git_dirty: bool                     # was the producer tree dirty?
    eval_name: str                      # "meta_allocation_portfolio"
    universe: str                       # "sp500_members_asof"
    cost_bps: float
    freq: str                           # "1d" | "1M"
    params: dict[str, Any]              # run knobs
    metrics: dict[str, float]           # FLAT scalar namespace: sharpe, sortino, maxdd, cagr,
                                        #   vol, turnover, beta, alpha, calmar, …
    series: PerfSeries | None           # equity/returns → parquet sidecar (NOT inline)
    trades: pl.DataFrame | None         # optional → parquet sidecar
    positions: pl.DataFrame | None      # optional → parquet sidecar
    extras: dict[str, Any]              # producer/eval-specific blocks (sweep_by_k, factor_sharpes,
                                        #   cost×time grid) — the today's-nested-report dumping ground
```

- `write_report(report, dest)` → writes `<run_id>.json` (scalars + metadata + extras + sidecar URIs)
  **and** parquet sidecars for `series`/`trades`/`positions`. `read_report(src)` → lazily rehydrates
  (sidecars loaded on demand).
- Migration of today's ad-hoc cerebrum `report.json`: the buried nested blocks (`full_portfolio`,
  `sweep_by_k`, …) move verbatim into `extras{}`; the soft-spot scalars (`sharpe`, `maxdd`, …) are
  promoted to the flat `metrics{}`. This is exactly the gap the contract closes — there is no shared
  schema today.

## 4. Storage model (run store — Q1 hybrid)

Robust + reusable across apps, git-native for the SHA history, lean git tree:

- **Small JSON (scalars + metadata + extras + sidecar URIs)** → committed by the producer to
  `docs/eval/runs/<date>-<eval>-<sha7>.json`. The git-SHA regression history *is* the git log:
  diffable, PR-reviewable, zero infra.
- **Heavy series/trades/positions parquet** → published to an HF dataset (`Why-Gee/cerebrum-perf-runs`
  for the cerebrum producer), mirroring the existing `Why-Gee/cerebrum-*-snapshot` convention. The
  JSON carries the `hf://…` URI; the dashboard pulls a curve only when a tear sheet needs it.

`DirectorySource` (generic) and `CerebrumBacktestSource` (Repo B) both read this layout; the only
cerebrum-specific knowledge is *where* the runs dir and HF dataset are.

## 5. Cross-repo dependency mechanism

`ygperf` is the single hard coupling and is intentionally tiny.

- **Producers / Repo B** pin it via git+subdirectory:
  `ygperf @ git+https://github.com/Why-Gee/YgTradingVisualizer.git#subdirectory=packages/contract`
  (gh-token auth in CI).
- **Local dev** uses an editable uv source / path dependency to the local checkout.

## 6. Hosting (Q3) & optional deps (Q5)

- **Local-only, deploy-ready:** the Dash app runs locally (`uv run`), but exposes the underlying
  Flask `server` object and reads config from env (no hard local-path assumptions) so a later
  container/Cloud Run/Fly deploy is a packaging change, not a rewrite. **Auth deferred** until a
  remote consumer exists.
- **QuantStats is an optional extra** (`app[quantstats]`), used solely for tear-sheet export. Core
  `ygtv-components` render native Plotly from the contract with no quantstats, keeping the reuse core
  dependency-light. Mirrors cerebrum's `[yahoo]`/`[hf]`/`[rl]` convention.

## 7. Live path (Q6 — deferred)

`LiveSource` is built now against the `ygperf` contract with a **file-poll stub** (producer appends
`PerfReport`-shaped records to a parquet/JSONL; dashboard reads via `dcc.Interval`). Real infra
(Postgres/redis) is chosen only if/when the bot actually emits and multi-writer/low-latency is
required — YAGNI now. Phase 3 also writes the bot-side contract doc for the bot's owner.

## 8. Phasing

| Phase | Repo | Deliverable |
|---|---|---|
| 0 | C (cerebrum) | **Handoff:** add `ygperf` dep; emit `PerfReport` from canonical 3 evals (meta-allocation, number-robustness, fundamentals-factors); establish `docs/eval/runs/` + HF run-store. `cerebrum-perf`-style new-package work, `0.1.0`. |
| 1 | A | Scaffold uv workspace + CI (ruff check & format) + `/init` CLAUDE.md; `ygperf`; `ygtv-components` (equity, drawdown, rolling-Sharpe, monthly-returns heatmap); `ygtv-sources` (Source + DirectorySource); generic Dash shell (Overview + per-strategy tear sheet). |
| 1b | B | **Handoff:** scaffold bridge; `CerebrumBacktestSource`; wire the generic app to cerebrum's run store; runnable cerebrum dashboard. |
| 2 | A + B | Regression-over-time (metric vs SHA) + factor-attribution + cost×time panels + remaining components (factor-alpha bars, positions/trades). Generic pieces in A; cerebrum-tuned pages in B. |
| 3 | A + B | `LiveSource` file-poll + `dcc.Interval` auto-refresh; bot-side contract doc. |

**This session builds Repo A (Phases 1, plus the components/sources that Phase 2 needs) and produces
the Repo B + Repo C handoffs.** Repos B and C are external → not edited here.

## 9. Testing / CI (TDD; mirrors cerebrum conventions)

- `ygperf`: `write → read` round-trip equality; `schema_version` handling; sidecar parquet integrity;
  git-SHA capture; deterministic `run_id`.
- `ygtv-components`: each factory returns a valid `go.Figure` from a synthetic `PerfReport`
  (structural assertions — trace count/types/titles — not pixels).
- `ygtv-sources`: a fixture run-set → SHA-indexed tidy frame for the regression view;
  `DirectorySource` glob + `hf://`; `LiveSource` poll.
- `app/`: import/layout/callback-registration smoke (Dash `dash.testing` optional).
- **CI** (per package, uv): `ruff check` **and** `ruff format --check` (both gates) + `pytest`.
  Windows prints set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`. New repo starts `0.1.0`; per-package
  SemVer + tags.

## 10. Risks / open items

- **Producer git-SHA semantics:** the regression x-axis is the *producer's* HEAD SHA, captured at run
  time; dirty trees flagged via `git_dirty`. Ordering across SHAs uses `run_ts` + topological git
  order where available (Repo B concern).
- **HF private-read auth** in the dashboard (token on disk / `storage_options`) — known pattern from
  cerebrum-store v0.6.1; carry it into `DirectorySource[hf]`.
- **`extras{}` is intentionally schemaless** — components must defensively handle missing keys; the
  regression/overview pages depend only on `metrics{}` + metadata, never on `extras{}`.

## 11. Naming summary

- Repo A `Why-Gee/YgTradingVisualizer`; packages `ygperf`, `ygtv-components`, `ygtv-sources`; import
  namespace `ygtv` for the viz packages, `ygperf` for the contract.
- Repo B `Why-Gee/YgCerebrumVisualizer` @ `L:\Work\Programming\Trading\CerebrumVisualizer`.
- Repo C cerebrum `Why-Gee/YgTradingCerebrum` (producer; emission only).
