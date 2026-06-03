# YgTradingVisualizer (Repo A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the generic, source-agnostic trading-performance visualization layer — the `ygperf` contract, the `ygtv-components` Plotly factories, the `ygtv-sources` adapters, and a generic Dash shell — as an installable uv workspace.

**Architecture:** uv workspace with three installable packages (`ygperf` contract, `ygtv-components`, `ygtv-sources`) plus a generic Dash `app/`. The contract is pure `dataclasses + polars`; components render `PerfReport → go.Figure` with zero source knowledge; sources read contract artifacts behind a `Source` protocol. cerebrum-awareness lives in a separate repo (B), never here.

**Tech Stack:** Python 3.12, uv, polars, plotly, dash, dash-bootstrap-components, pytest, ruff. Spec: `docs/superpowers/specs/2026-06-03-ygtradingvisualizer-design.md`.

---

## File Structure

```
TradingVisualizer/
├── pyproject.toml                          # uv workspace root (package=false), ruff, pytest cfg
├── README.md · LICENSE · .gitignore · CLAUDE.md
├── .github/workflows/ci.yml                # ruff check + ruff format --check + pytest, per package
├── packages/
│   ├── contract/                           # dist: ygperf  (deps: polars)
│   │   ├── pyproject.toml
│   │   ├── src/ygperf/__init__.py          # re-exports
│   │   ├── src/ygperf/report.py            # SCHEMA_VERSION, PerfReport
│   │   ├── src/ygperf/ids.py               # run_id_for()
│   │   ├── src/ygperf/git.py               # capture_git()
│   │   ├── src/ygperf/io.py                # write_report() / read_report()
│   │   └── tests/{test_report,test_ids,test_io,test_git}.py
│   ├── components/                         # dist: ygtv-components  (deps: ygperf, plotly)
│   │   ├── pyproject.toml
│   │   ├── src/ygtv/components/__init__.py
│   │   ├── src/ygtv/components/equity.py · drawdown.py · rolling.py · heatmap.py
│   │   └── tests/test_*.py
│   └── sources/                            # dist: ygtv-sources  (deps: ygperf, polars; [hf])
│       ├── pyproject.toml
│       ├── src/ygtv/sources/__init__.py
│       ├── src/ygtv/sources/base.py        # Source Protocol, RunRef
│       ├── src/ygtv/sources/directory.py   # DirectorySource
│       ├── src/ygtv/sources/live.py        # LiveSource (file-poll stub)
│       └── tests/test_*.py
└── app/                                    # not published (deps: dash, dbc, ygtv-*; [quantstats])
    ├── pyproject.toml
    ├── src/ygtv/app/__init__.py
    ├── src/ygtv/app/factory.py             # build_app(source) -> Dash; exposes .server (Flask)
    ├── src/ygtv/app/pages/{overview,tearsheet}.py
    └── tests/test_app_smoke.py
```

`ygtv` is a PEP-420 namespace shared by components/sources/app (mirrors cerebrum's `cerebrum.*`). `ygperf` is its own top-level package. **`PerfSeries` from the spec is realized as a `pl.DataFrame`** with fixed columns (`timestamp`, `equity`, `returns`) — no wrapper class (YAGNI).

---

## Task 1: Scaffold the uv workspace

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `README.md`, `LICENSE`, `packages/contract/pyproject.toml`, `packages/contract/src/ygperf/__init__.py`

- [ ] **Step 1: Create the workspace root `pyproject.toml`**

```toml
[project]
name = "ygtradingvisualizer"
version = "0.0.0"
description = "Source-agnostic trading-performance visualization layer (monorepo root — not installable)."
readme = "README.md"
requires-python = ">=3.12"
authors = [{ name = "Yaniv Gorali", email = "yanivg@gmail.com" }]

[tool.uv]
package = false

[tool.uv.workspace]
members = ["packages/contract", "packages/components", "packages/sources", "app"]

[tool.uv.sources]
ygperf = { workspace = true }
ygtv-components = { workspace = true }
ygtv-sources = { workspace = true }

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.6", "ygtv-components", "ygtv-sources", "ygperf"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "RUF", "PT"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"**/tests/**" = ["F401", "F811"]

[tool.pytest.ini_options]
addopts = "-q --import-mode=importlib"
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
.venv/
.ruff_cache/
.pytest_cache/
dist/
*.egg-info/
.env
```

- [ ] **Step 3: Create `packages/contract/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ygperf"
version = "0.1.0"
description = "Source-agnostic trading-performance report contract (PerfReport): pure dataclasses + polars."
readme = "README.md"
requires-python = ">=3.12"
authors = [{ name = "Yaniv Gorali", email = "yanivg@gmail.com" }]
dependencies = ["polars>=1.0", "pyarrow>=15.0"]

[tool.hatch.build.targets.wheel]
packages = ["src/ygperf"]
```

- [ ] **Step 4: Create `packages/contract/README.md` and `packages/contract/src/ygperf/__init__.py`**

`packages/contract/README.md`:
```markdown
# ygperf

Source-agnostic trading-performance report contract. One `PerfReport` per run; `write_report`/`read_report`. Deps: polars only. No plotly/dash — any producer (backtest, live bot) can import it.
```

`packages/contract/src/ygperf/__init__.py`:
```python
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygperf.ids import run_id_for
from ygperf.git import capture_git
from ygperf.io import write_report, read_report

__all__ = [
    "SCHEMA_VERSION",
    "PerfReport",
    "run_id_for",
    "capture_git",
    "write_report",
    "read_report",
]
```

- [ ] **Step 5: Create the root `README.md` and `LICENSE`**

`README.md`:
```markdown
# YgTradingVisualizer

Source-agnostic trading-performance visualization layer (Plotly Dash). Renders any producer's
`ygperf` reports — cerebrum backtests, the live bot, future apps — via reusable chart components.
See `docs/superpowers/specs/2026-06-03-ygtradingvisualizer-design.md`.
```

`LICENSE`: proprietary one-liner —
```text
Copyright (c) 2026 Yaniv Gorali. All rights reserved. Proprietary and confidential.
```

- [ ] **Step 6: Sync and verify the workspace resolves**

Run: `uv sync`
Expected: resolves with `ygperf` as a workspace member, creates `.venv`, no errors. (`ygtv-components`/`ygtv-sources` members are added in later tasks; comment them out of `members`/`sources`/`dev` until their `pyproject.toml` exists, or create empty package stubs first — simplest: create the three package `pyproject.toml` skeletons in Step-0 order before `uv sync`.)

- [ ] **Step 7: Commit**

```bash
git init
git add -A
git commit -m "chore: scaffold uv workspace + ygperf package skeleton"
```

---

## Task 2: `ygperf` — PerfReport schema

**Files:**
- Create: `packages/contract/src/ygperf/report.py`
- Test: `packages/contract/tests/test_report.py`

- [ ] **Step 1: Write the failing test**

```python
# packages/contract/tests/test_report.py
from datetime import datetime, timezone

import polars as pl

from ygperf.report import SCHEMA_VERSION, PerfReport


def _minimal() -> PerfReport:
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="abc123",
        run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc),
        git_sha="deadbeef",
        git_dirty=False,
        eval_name="meta_allocation_portfolio",
        universe="sp500_members_asof",
        cost_bps=5.0,
        freq="1M",
        params={"k": 3},
        metrics={"sharpe": 0.85, "maxdd": 0.234},
        series=pl.DataFrame({"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}),
        trades=None,
        positions=None,
        extras={"sweep_by_k": [0.7, 0.8]},
    )


def test_perfreport_is_frozen_and_carries_fields():
    r = _minimal()
    assert r.schema_version == SCHEMA_VERSION
    assert r.metrics["sharpe"] == 0.85
    assert r.series.columns == ["timestamp", "equity", "returns"]
    import dataclasses
    try:
        r.eval_name = "x"  # frozen → should raise
        raised = False
    except dataclasses.FrozenInstanceError:
        raised = True
    assert raised
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --package ygperf pytest packages/contract/tests/test_report.py -v`
Expected: FAIL — `ModuleNotFoundError: ygperf.report`.

- [ ] **Step 3: Write minimal implementation**

```python
# packages/contract/src/ygperf/report.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import polars as pl

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class PerfReport:
    """One performance report per run. Source-agnostic. Heavy frames are sidecar-serialized."""

    schema_version: str
    run_id: str
    run_ts: datetime
    git_sha: str
    git_dirty: bool
    eval_name: str
    universe: str
    cost_bps: float
    freq: str
    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    series: pl.DataFrame | None = None      # cols: timestamp, equity, returns
    trades: pl.DataFrame | None = None
    positions: pl.DataFrame | None = None
    extras: dict[str, Any] = field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --package ygperf pytest packages/contract/tests/test_report.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add packages/contract/src/ygperf/report.py packages/contract/tests/test_report.py
git commit -m "feat(ygperf): PerfReport schema + SCHEMA_VERSION"
```

---

## Task 3: `ygperf` — deterministic run_id

**Files:**
- Create: `packages/contract/src/ygperf/ids.py`
- Test: `packages/contract/tests/test_ids.py`

- [ ] **Step 1: Write the failing test**

```python
# packages/contract/tests/test_ids.py
from datetime import datetime, timezone

from ygperf.ids import run_id_for


def test_run_id_is_deterministic_and_short():
    ts = datetime(2026, 6, 3, 12, 0, tzinfo=timezone.utc)
    a = run_id_for("deadbeef", "meta_allocation_portfolio", ts)
    b = run_id_for("deadbeef", "meta_allocation_portfolio", ts)
    c = run_id_for("deadbeef", "number_robustness", ts)
    assert a == b            # deterministic
    assert a != c            # varies by eval
    assert len(a) == 16 and a.isalnum()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --package ygperf pytest packages/contract/tests/test_ids.py -v`
Expected: FAIL — `ModuleNotFoundError: ygperf.ids`.

- [ ] **Step 3: Write minimal implementation**

```python
# packages/contract/src/ygperf/ids.py
from __future__ import annotations

import hashlib
from datetime import datetime


def run_id_for(git_sha: str, eval_name: str, run_ts: datetime) -> str:
    """Deterministic 16-hex-char id from (git_sha, eval_name, run_ts)."""
    key = f"{git_sha}|{eval_name}|{run_ts.isoformat()}".encode()
    return hashlib.sha256(key).hexdigest()[:16]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --package ygperf pytest packages/contract/tests/test_ids.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add packages/contract/src/ygperf/ids.py packages/contract/tests/test_ids.py
git commit -m "feat(ygperf): deterministic run_id_for"
```

---

## Task 4: `ygperf` — git capture helper

**Files:**
- Create: `packages/contract/src/ygperf/git.py`
- Test: `packages/contract/tests/test_git.py`

- [ ] **Step 1: Write the failing test** (runs against this repo's own git)

```python
# packages/contract/tests/test_git.py
import subprocess
from pathlib import Path

import pytest

from ygperf.git import capture_git


def _is_git_repo(p: Path) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--git-dir"], cwd=p, capture_output=True
    ).returncode == 0


def test_capture_git_returns_sha_and_dirty_flag(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit",
                    "--allow-empty", "-m", "x"], cwd=tmp_path, check=True, capture_output=True)
    sha, dirty = capture_git(tmp_path)
    assert len(sha) == 40 and not dirty
    (tmp_path / "f.txt").write_text("hi")
    _, dirty2 = capture_git(tmp_path)
    assert dirty2 is True


def test_capture_git_on_non_repo_returns_unknown(tmp_path):
    sha, dirty = capture_git(tmp_path / "nope")
    assert sha == "unknown" and dirty is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --package ygperf pytest packages/contract/tests/test_git.py -v`
Expected: FAIL — `ModuleNotFoundError: ygperf.git`.

- [ ] **Step 3: Write minimal implementation**

```python
# packages/contract/src/ygperf/git.py
from __future__ import annotations

import subprocess
from pathlib import Path


def capture_git(repo_dir: str | Path) -> tuple[str, bool]:
    """Return (HEAD sha, dirty?). ('unknown', False) if not a git repo."""
    repo_dir = str(repo_dir)
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()
        return sha, bool(status)
    except (subprocess.CalledProcessError, FileNotFoundError, NotADirectoryError):
        return "unknown", False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --package ygperf pytest packages/contract/tests/test_git.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add packages/contract/src/ygperf/git.py packages/contract/tests/test_git.py
git commit -m "feat(ygperf): capture_git helper"
```

---

## Task 5: `ygperf` — write_report / read_report round-trip with parquet sidecars

**Files:**
- Create: `packages/contract/src/ygperf/io.py`
- Test: `packages/contract/tests/test_io.py`

- [ ] **Step 1: Write the failing test**

```python
# packages/contract/tests/test_io.py
import json
from datetime import datetime, timezone

import polars as pl

from ygperf.io import read_report, write_report
from ygperf.report import SCHEMA_VERSION, PerfReport


def _report() -> PerfReport:
    return PerfReport(
        schema_version=SCHEMA_VERSION, run_id="r1",
        run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc), git_sha="sha1", git_dirty=False,
        eval_name="meta_allocation_portfolio", universe="u", cost_bps=5.0, freq="1M",
        params={"k": 3}, metrics={"sharpe": 0.85},
        series=pl.DataFrame({"timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1)],
                             "equity": [1.0, 1.1], "returns": [0.0, 0.1]}),
        trades=None, positions=None, extras={"sweep_by_k": [0.7, 0.8]},
    )


def test_write_then_read_round_trips(tmp_path):
    json_path = write_report(_report(), tmp_path)
    assert json_path.name == "r1.json"
    assert (tmp_path / "r1.series.parquet").exists()
    # JSON holds scalars + the sidecar pointer, NOT the series rows
    raw = json.loads(json_path.read_text())
    assert raw["metrics"]["sharpe"] == 0.85
    assert raw["sidecars"]["series"] == "r1.series.parquet"
    assert "equity" not in raw

    got = read_report(json_path)
    assert got.schema_version == SCHEMA_VERSION
    assert got.metrics["sharpe"] == 0.85
    assert got.extras["sweep_by_k"] == [0.7, 0.8]
    assert got.series.shape == (2, 3)
    assert got.trades is None


def test_read_is_lazy_when_load_series_false(tmp_path):
    json_path = write_report(_report(), tmp_path)
    got = read_report(json_path, load_frames=False)
    assert got.series is None          # not loaded
    assert got.metrics["sharpe"] == 0.85  # scalars always present
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --package ygperf pytest packages/contract/tests/test_io.py -v`
Expected: FAIL — `ModuleNotFoundError: ygperf.io`.

- [ ] **Step 3: Write minimal implementation**

```python
# packages/contract/src/ygperf/io.py
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import polars as pl

from ygperf.report import PerfReport

_FRAME_FIELDS = ("series", "trades", "positions")


def write_report(report: PerfReport, dest_dir: str | Path) -> Path:
    """Write <run_id>.json (scalars+metadata+extras+sidecar pointers) + parquet sidecars."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    sidecars: dict[str, str] = {}
    for fname in _FRAME_FIELDS:
        frame: pl.DataFrame | None = getattr(report, fname)
        if frame is not None:
            rel = f"{report.run_id}.{fname}.parquet"
            frame.write_parquet(dest / rel)
            sidecars[fname] = rel
    doc = {
        "schema_version": report.schema_version,
        "run_id": report.run_id,
        "run_ts": report.run_ts.isoformat(),
        "git_sha": report.git_sha,
        "git_dirty": report.git_dirty,
        "eval_name": report.eval_name,
        "universe": report.universe,
        "cost_bps": report.cost_bps,
        "freq": report.freq,
        "params": report.params,
        "metrics": report.metrics,
        "extras": report.extras,
        "sidecars": sidecars,
    }
    json_path = dest / f"{report.run_id}.json"
    json_path.write_text(json.dumps(doc, indent=2, sort_keys=True), encoding="utf-8")
    return json_path


def read_report(json_path: str | Path, *, load_frames: bool = True) -> PerfReport:
    """Inverse of write_report. Sidecar URIs resolve relative to json_path's dir, or absolute (hf://)."""
    json_path = Path(json_path)
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    frames: dict[str, pl.DataFrame | None] = {f: None for f in _FRAME_FIELDS}
    if load_frames:
        for fname, ref in doc.get("sidecars", {}).items():
            uri = ref if "://" in ref or Path(ref).is_absolute() else str(json_path.parent / ref)
            frames[fname] = pl.read_parquet(uri)
    return PerfReport(
        schema_version=doc["schema_version"],
        run_id=doc["run_id"],
        run_ts=datetime.fromisoformat(doc["run_ts"]),
        git_sha=doc["git_sha"],
        git_dirty=doc["git_dirty"],
        eval_name=doc["eval_name"],
        universe=doc["universe"],
        cost_bps=doc["cost_bps"],
        freq=doc["freq"],
        params=doc.get("params", {}),
        metrics=doc.get("metrics", {}),
        series=frames["series"],
        trades=frames["trades"],
        positions=frames["positions"],
        extras=doc.get("extras", {}),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --package ygperf pytest packages/contract/tests/ -v`
Expected: PASS (all contract tests).

- [ ] **Step 5: Commit**

```bash
git add packages/contract/src/ygperf/io.py packages/contract/tests/test_io.py
git commit -m "feat(ygperf): write_report/read_report with parquet sidecars"
```

---

## Task 6: `ygtv-components` package + equity-curve factory (the component pattern)

**Files:**
- Create: `packages/components/pyproject.toml`, `packages/components/src/ygtv/components/__init__.py`, `packages/components/src/ygtv/components/equity.py`
- Test: `packages/components/tests/test_equity.py`

- [ ] **Step 1: Create `packages/components/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ygtv-components"
version = "0.1.0"
description = "Source-agnostic Plotly figure factories rendering ygperf PerfReports."
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["ygperf", "plotly>=5.20", "polars>=1.0"]

[tool.hatch.build.targets.wheel]
packages = ["src/ygtv"]
```
(Add `packages/components/README.md` with a one-line description. Uncomment the `components` member in the root workspace if it was stubbed.)

- [ ] **Step 2: Write the failing test**

```python
# packages/components/tests/test_equity.py
from datetime import datetime, timezone

import plotly.graph_objects as go
import polars as pl

from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.equity import equity_curve


def _report(series):
    return PerfReport(
        schema_version=SCHEMA_VERSION, run_id="r", run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc),
        git_sha="s", git_dirty=False, eval_name="e", universe="u", cost_bps=5.0, freq="1M",
        params={}, metrics={}, series=series, trades=None, positions=None, extras={},
    )


def test_equity_curve_returns_figure_with_one_trace():
    s = pl.DataFrame({"timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1)],
                      "equity": [1.0, 1.2], "returns": [0.0, 0.2]})
    fig = equity_curve(_report(s))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [1.0, 1.2]


def test_equity_curve_handles_missing_series_defensively():
    fig = equity_curve(_report(None))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations  # shows a "no series" annotation
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run --package ygtv-components pytest packages/components/tests/test_equity.py -v`
Expected: FAIL — `ModuleNotFoundError: ygtv.components.equity`.

- [ ] **Step 4: Write minimal implementation**

```python
# packages/components/src/ygtv/components/equity.py
from __future__ import annotations

import plotly.graph_objects as go

from ygperf.report import PerfReport


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
    return fig


def equity_curve(report: PerfReport) -> go.Figure:
    """Equity curve from report.series (cols: timestamp, equity)."""
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    fig = go.Figure(
        go.Scatter(x=s["timestamp"].to_list(), y=s["equity"].to_list(), mode="lines", name="equity")
    )
    fig.update_layout(title=f"Equity — {report.eval_name}", xaxis_title="time", yaxis_title="equity")
    return fig
```

`packages/components/src/ygtv/components/__init__.py`:
```python
from ygtv.components.equity import equity_curve

__all__ = ["equity_curve"]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run --package ygtv-components pytest packages/components/tests/test_equity.py -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add packages/components
git commit -m "feat(components): equity_curve factory + package"
```

---

## Task 7: `ygtv-components` — drawdown, rolling Sharpe, monthly-returns heatmap

**Files:**
- Create: `packages/components/src/ygtv/components/drawdown.py`, `rolling.py`, `heatmap.py`
- Modify: `packages/components/src/ygtv/components/__init__.py`
- Test: `packages/components/tests/test_drawdown.py`, `test_rolling.py`, `test_heatmap.py`

- [ ] **Step 1: Write failing tests**

```python
# packages/components/tests/test_drawdown.py
from datetime import datetime, timezone
import plotly.graph_objects as go
import polars as pl
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.drawdown import drawdown_curve

def _r(s):
    return PerfReport(schema_version=SCHEMA_VERSION, run_id="r",
        run_ts=datetime(2026,6,3,tzinfo=timezone.utc), git_sha="s", git_dirty=False,
        eval_name="e", universe="u", cost_bps=5.0, freq="1M", params={}, metrics={},
        series=s, trades=None, positions=None, extras={})

def test_drawdown_is_nonpositive_and_one_trace():
    s = pl.DataFrame({"timestamp":[datetime(2026,1,1),datetime(2026,2,1),datetime(2026,3,1)],
                      "equity":[1.0,1.2,0.9],"returns":[0.0,0.2,-0.25]})
    fig = drawdown_curve(_r(s))
    assert isinstance(fig, go.Figure) and len(fig.data) == 1
    assert min(fig.data[0].y) < 0 and max(fig.data[0].y) <= 0.0
```

```python
# packages/components/tests/test_rolling.py
from datetime import datetime, timezone
import plotly.graph_objects as go
import polars as pl
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.rolling import rolling_sharpe

def _r(s):
    return PerfReport(schema_version=SCHEMA_VERSION, run_id="r",
        run_ts=datetime(2026,6,3,tzinfo=timezone.utc), git_sha="s", git_dirty=False,
        eval_name="e", universe="u", cost_bps=5.0, freq="1M", params={}, metrics={},
        series=s, trades=None, positions=None, extras={})

def test_rolling_sharpe_returns_figure():
    ts = [datetime(2026,1,1)] * 0 + [datetime(2026,m,1) for m in range(1,13)]
    s = pl.DataFrame({"timestamp": ts, "equity":[1.0]*12,
                      "returns":[0.01,-0.02,0.03,0.0,0.02,-0.01,0.04,0.01,-0.03,0.02,0.0,0.01]})
    fig = rolling_sharpe(_r(s), window=3, periods_per_year=12)
    assert isinstance(fig, go.Figure) and len(fig.data) == 1
```

```python
# packages/components/tests/test_heatmap.py
from datetime import datetime, timezone
import plotly.graph_objects as go
import polars as pl
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.heatmap import monthly_returns_heatmap

def _r(s):
    return PerfReport(schema_version=SCHEMA_VERSION, run_id="r",
        run_ts=datetime(2026,6,3,tzinfo=timezone.utc), git_sha="s", git_dirty=False,
        eval_name="e", universe="u", cost_bps=5.0, freq="1M", params={}, metrics={},
        series=s, trades=None, positions=None, extras={})

def test_heatmap_returns_heatmap_trace():
    ts = [datetime(2025,m,1) for m in range(1,13)] + [datetime(2026,1,1)]
    s = pl.DataFrame({"timestamp": ts, "equity":[1.0]*13, "returns":[0.01]*13})
    fig = monthly_returns_heatmap(_r(s))
    assert isinstance(fig, go.Figure) and len(fig.data) == 1
    assert fig.data[0].type == "heatmap"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --package ygtv-components pytest packages/components/tests/test_drawdown.py packages/components/tests/test_rolling.py packages/components/tests/test_heatmap.py -v`
Expected: FAIL — modules not found.

- [ ] **Step 3: Write implementations**

```python
# packages/components/src/ygtv/components/drawdown.py
from __future__ import annotations
import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components.equity import _empty

def drawdown_curve(report: PerfReport) -> go.Figure:
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    eq = s["equity"].to_list()
    peak = eq[0]
    dd = []
    for v in eq:
        peak = max(peak, v)
        dd.append(v / peak - 1.0)
    fig = go.Figure(go.Scatter(x=s["timestamp"].to_list(), y=dd, fill="tozeroy", name="drawdown"))
    fig.update_layout(title=f"Drawdown — {report.eval_name}", yaxis_title="drawdown")
    return fig
```

```python
# packages/components/src/ygtv/components/rolling.py
from __future__ import annotations
import math
import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components.equity import _empty

def rolling_sharpe(report: PerfReport, *, window: int = 12, periods_per_year: int = 12) -> go.Figure:
    s = report.series
    if s is None or s.height < window:
        return _empty("series too short")
    r = s["returns"].to_list()
    ts = s["timestamp"].to_list()
    out_x, out_y = [], []
    for i in range(window - 1, len(r)):
        win = r[i - window + 1 : i + 1]
        mean = sum(win) / window
        var = sum((x - mean) ** 2 for x in win) / max(window - 1, 1)
        std = math.sqrt(var)
        sharpe = (mean / std * math.sqrt(periods_per_year)) if std > 0 else 0.0
        out_x.append(ts[i]); out_y.append(sharpe)
    fig = go.Figure(go.Scatter(x=out_x, y=out_y, mode="lines", name="rolling sharpe"))
    fig.update_layout(title=f"Rolling Sharpe (w={window}) — {report.eval_name}", yaxis_title="sharpe")
    return fig
```

```python
# packages/components/src/ygtv/components/heatmap.py
from __future__ import annotations
import plotly.graph_objects as go
import polars as pl
from ygperf.report import PerfReport
from ygtv.components.equity import _empty

def monthly_returns_heatmap(report: PerfReport) -> go.Figure:
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    df = s.select(
        pl.col("timestamp").dt.year().alias("year"),
        pl.col("timestamp").dt.month().alias("month"),
        pl.col("returns"),
    ).group_by(["year", "month"]).agg(pl.col("returns").sum()).sort(["year", "month"])
    years = sorted(df["year"].unique().to_list())
    z = [[None] * 12 for _ in years]
    yi = {y: i for i, y in enumerate(years)}
    for row in df.iter_rows(named=True):
        z[yi[row["year"]]][row["month"] - 1] = row["returns"]
    fig = go.Figure(go.Heatmap(z=z, x=[f"{m:02d}" for m in range(1, 13)], y=[str(y) for y in years],
                               colorscale="RdYlGn", zmid=0))
    fig.update_layout(title=f"Monthly returns — {report.eval_name}")
    return fig
```

Update `__init__.py`:
```python
from ygtv.components.equity import equity_curve
from ygtv.components.drawdown import drawdown_curve
from ygtv.components.rolling import rolling_sharpe
from ygtv.components.heatmap import monthly_returns_heatmap

__all__ = ["equity_curve", "drawdown_curve", "rolling_sharpe", "monthly_returns_heatmap"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --package ygtv-components pytest packages/components/tests/ -v`
Expected: PASS (all component tests).

- [ ] **Step 5: Commit**

```bash
git add packages/components
git commit -m "feat(components): drawdown, rolling sharpe, monthly-returns heatmap"
```

---

## Task 8: `ygtv-sources` — Source protocol + DirectorySource

**Files:**
- Create: `packages/sources/pyproject.toml`, `packages/sources/src/ygtv/sources/__init__.py`, `base.py`, `directory.py`
- Test: `packages/sources/tests/test_directory.py`

- [ ] **Step 1: Create `packages/sources/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ygtv-sources"
version = "0.1.0"
description = "Source adapters that feed ygperf PerfReports to the visualizer (Source protocol + DirectorySource + LiveSource)."
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["ygperf", "polars>=1.0"]

[project.optional-dependencies]
hf = ["huggingface_hub>=1.0"]

[tool.hatch.build.targets.wheel]
packages = ["src/ygtv"]
```
(Add a one-line `packages/sources/README.md`.)

- [ ] **Step 2: Write the failing test**

```python
# packages/sources/tests/test_directory.py
from datetime import datetime, timezone

import polars as pl

from ygperf.io import write_report
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.sources.directory import DirectorySource


def _write(tmp_path, run_id, sha, sharpe):
    r = PerfReport(schema_version=SCHEMA_VERSION, run_id=run_id,
        run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc), git_sha=sha, git_dirty=False,
        eval_name="meta_allocation_portfolio", universe="u", cost_bps=5.0, freq="1M",
        params={}, metrics={"sharpe": sharpe, "maxdd": 0.2},
        series=pl.DataFrame({"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}),
        trades=None, positions=None, extras={})
    write_report(r, tmp_path)


def test_directory_source_indexes_runs_and_loads_reports(tmp_path):
    _write(tmp_path, "r1", "sha_old", 0.70)
    _write(tmp_path, "r2", "sha_new", 0.85)
    src = DirectorySource(tmp_path)

    runs = src.runs()                       # tidy frame for overview/regression
    assert set(runs["run_id"]) == {"r1", "r2"}
    assert "sharpe" in runs.columns and "git_sha" in runs.columns
    assert runs.filter(pl.col("run_id") == "r2")["sharpe"].item() == 0.85

    rep = src.report("r1")                  # full report w/ series
    assert rep.git_sha == "sha_old"
    assert rep.series.height == 1


def test_runs_frame_is_empty_for_empty_dir(tmp_path):
    assert DirectorySource(tmp_path).runs().is_empty()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run --package ygtv-sources pytest packages/sources/tests/test_directory.py -v`
Expected: FAIL — `ModuleNotFoundError: ygtv.sources.directory`.

- [ ] **Step 4: Write implementations**

```python
# packages/sources/src/ygtv/sources/base.py
from __future__ import annotations

from typing import Protocol, runtime_checkable

import polars as pl

from ygperf.report import PerfReport


@runtime_checkable
class Source(Protocol):
    """A provider of ygperf runs. Backtest vs live differ ONLY in the implementation."""

    def runs(self) -> pl.DataFrame:
        """Tidy frame, one row per run: run_id, git_sha, run_ts, eval_name + flattened metrics."""
        ...

    def report(self, run_id: str) -> PerfReport:
        """Full report (with frames) for one run."""
        ...
```

```python
# packages/sources/src/ygtv/sources/directory.py
from __future__ import annotations

from pathlib import Path

import polars as pl

from ygperf.io import read_report
from ygperf.report import PerfReport


class DirectorySource:
    """Reads ygperf JSON reports from a directory (glob `*.json`). Source-agnostic."""

    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)

    def _json_paths(self) -> list[Path]:
        return sorted(self._dir.glob("*.json"))

    def runs(self) -> pl.DataFrame:
        rows = []
        for p in self._json_paths():
            r = read_report(p, load_frames=False)
            rows.append({
                "run_id": r.run_id, "git_sha": r.git_sha, "run_ts": r.run_ts,
                "eval_name": r.eval_name, "cost_bps": r.cost_bps, **r.metrics,
            })
        return pl.DataFrame(rows) if rows else pl.DataFrame()

    def report(self, run_id: str) -> PerfReport:
        return read_report(self._dir / f"{run_id}.json")
```

```python
# packages/sources/src/ygtv/sources/__init__.py
from ygtv.sources.base import Source
from ygtv.sources.directory import DirectorySource

__all__ = ["Source", "DirectorySource"]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run --package ygtv-sources pytest packages/sources/tests/test_directory.py -v`
Expected: PASS (2 tests). Also assert the protocol: `isinstance(DirectorySource(tmp_path), Source)` is True (add to test if desired).

- [ ] **Step 6: Commit**

```bash
git add packages/sources
git commit -m "feat(sources): Source protocol + DirectorySource"
```

---

## Task 9: `ygtv-sources` — LiveSource file-poll stub

**Files:**
- Create: `packages/sources/src/ygtv/sources/live.py`
- Modify: `packages/sources/src/ygtv/sources/__init__.py`
- Test: `packages/sources/tests/test_live.py`

- [ ] **Step 1: Write the failing test**

```python
# packages/sources/tests/test_live.py
from datetime import datetime, timezone
import polars as pl
from ygperf.io import write_report
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.sources.base import Source
from ygtv.sources.live import LiveSource

def _write(d, rid, ts):
    write_report(PerfReport(schema_version=SCHEMA_VERSION, run_id=rid, run_ts=ts, git_sha="live",
        git_dirty=True, eval_name="live_strategy", universe="u", cost_bps=0.0, freq="1d",
        params={}, metrics={"sharpe": 1.0},
        series=pl.DataFrame({"timestamp":[ts],"equity":[1.0],"returns":[0.0]}),
        trades=None, positions=None, extras={}), d)

def test_livesource_satisfies_protocol_and_reads_latest(tmp_path):
    _write(tmp_path, "a", datetime(2026,6,3,10,tzinfo=timezone.utc))
    _write(tmp_path, "b", datetime(2026,6,3,11,tzinfo=timezone.utc))
    src = LiveSource(tmp_path)
    assert isinstance(src, Source)
    assert src.runs().height == 2
    assert src.latest().run_id == "b"   # newest by run_ts
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --package ygtv-sources pytest packages/sources/tests/test_live.py -v`
Expected: FAIL — `ModuleNotFoundError: ygtv.sources.live`.

- [ ] **Step 3: Write implementation**

```python
# packages/sources/src/ygtv/sources/live.py
from __future__ import annotations

from pathlib import Path

import polars as pl

from ygperf.report import PerfReport
from ygtv.sources.directory import DirectorySource


class LiveSource(DirectorySource):
    """Phase-3 stub: polls a directory the producer appends to. Same contract as DirectorySource.

    A Dash `dcc.Interval` re-calls `runs()`/`latest()` on a timer. When the bot emits the contract,
    only this adapter's storage backend changes — the app and components are untouched.
    """

    def latest(self) -> PerfReport:
        runs = self.runs()
        if runs.is_empty():
            raise LookupError("no runs in live directory")
        newest = runs.sort("run_ts", descending=True).row(0, named=True)["run_id"]
        return self.report(newest)
```

Update `__init__.py` to also export `LiveSource`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --package ygtv-sources pytest packages/sources/tests/ -v`
Expected: PASS (all source tests).

- [ ] **Step 5: Commit**

```bash
git add packages/sources
git commit -m "feat(sources): LiveSource file-poll stub"
```

---

## Task 10: `app/` — generic Dash shell (Overview + tear sheet), deploy-ready

**Files:**
- Create: `app/pyproject.toml`, `app/src/ygtv/app/__init__.py`, `app/src/ygtv/app/factory.py`, `app/src/ygtv/app/pages/overview.py`, `app/src/ygtv/app/pages/tearsheet.py`
- Test: `app/tests/test_app_smoke.py`

- [ ] **Step 1: Create `app/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ygtv-app"
version = "0.1.0"
description = "Generic multipage Dash shell rendering any ygperf Source."
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["ygperf", "ygtv-components", "ygtv-sources", "dash>=3.0", "dash-bootstrap-components>=1.6", "polars>=1.0"]

[project.optional-dependencies]
quantstats = ["quantstats>=0.0.62"]

[tool.hatch.build.targets.wheel]
packages = ["src/ygtv"]
```
(Add a one-line `app/README.md`. Add `app` to the workspace `members` + a `ygtv-app` workspace source if needed.)

- [ ] **Step 2: Write the failing smoke test**

```python
# app/tests/test_app_smoke.py
from datetime import datetime, timezone

import polars as pl
from dash import Dash

from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.app.factory import build_app


class _FakeSource:
    def runs(self):
        return pl.DataFrame({"run_id": ["r1"], "git_sha": ["s1"],
                             "run_ts": [datetime(2026, 6, 3, tzinfo=timezone.utc)],
                             "eval_name": ["e"], "sharpe": [0.85]})

    def report(self, run_id):
        return PerfReport(schema_version=SCHEMA_VERSION, run_id=run_id,
            run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc), git_sha="s1", git_dirty=False,
            eval_name="e", universe="u", cost_bps=5.0, freq="1M", params={}, metrics={"sharpe": 0.85},
            series=pl.DataFrame({"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}),
            trades=None, positions=None, extras={})


def test_build_app_returns_dash_with_pages_and_flask_server():
    app = build_app(_FakeSource())
    assert isinstance(app, Dash)
    assert app.layout is not None
    assert app.server is not None                 # Flask server exposed for deploy
    # Overview + tear sheet registered
    import dash
    paths = {p["path"] for p in dash.page_registry.values()}
    assert "/" in paths
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run --package ygtv-app pytest app/tests/test_app_smoke.py -v`
Expected: FAIL — `ModuleNotFoundError: ygtv.app.factory`.

- [ ] **Step 4: Write the implementation**

```python
# app/src/ygtv/app/factory.py
from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from ygtv.app.pages import overview, tearsheet


def build_app(source) -> Dash:
    """Build a generic multipage Dash app over any ygperf Source. Returns the Dash app;
    `app.server` is the Flask server (for gunicorn/deploy). Auth/hosting are deferred."""
    app = Dash(__name__, use_pages=True, pages_folder="",
               external_stylesheets=[dbc.themes.BOOTSTRAP])

    overview.register(source)
    tearsheet.register(source)

    app.layout = dbc.Container([
        html.H3("YgTradingVisualizer"),
        html.Div([dcc.Link(f"{p['name']}", href=p["relative_path"], className="me-3")
                  for p in dash.page_registry.values()]),
        html.Hr(),
        dash.page_container,
    ], fluid=True)
    return app
```

```python
# app/src/ygtv/app/pages/overview.py
from __future__ import annotations

import dash
from dash import dash_table, html


def register(source) -> None:
    runs = source.runs()
    records = runs.to_dicts() if not runs.is_empty() else []
    columns = [{"name": c, "id": c} for c in (runs.columns if not runs.is_empty() else ["run_id"])]
    layout = html.Div([
        html.H4("Overview"),
        dash_table.DataTable(data=records, columns=columns, page_size=20, sort_action="native"),
    ])
    dash.register_page("overview", path="/", name="Overview", layout=layout)
```

```python
# app/src/ygtv/app/pages/tearsheet.py
from __future__ import annotations

import dash
from dash import dcc, html

from ygtv.components import drawdown_curve, equity_curve, monthly_returns_heatmap, rolling_sharpe


def register(source) -> None:
    runs = source.runs()
    run_ids = runs["run_id"].to_list() if not runs.is_empty() else []
    default = run_ids[0] if run_ids else None

    def _layout(run_id: str | None = default):
        if not run_id:
            return html.Div("No runs available.")
        rep = source.report(run_id)
        return html.Div([
            html.H4(f"Tear sheet — {rep.eval_name} @ {rep.git_sha[:7]}"),
            dcc.Dropdown(run_ids, run_id, id="ts-run"),
            dcc.Graph(figure=equity_curve(rep)),
            dcc.Graph(figure=drawdown_curve(rep)),
            dcc.Graph(figure=rolling_sharpe(rep)),
            dcc.Graph(figure=monthly_returns_heatmap(rep)),
        ])

    dash.register_page("tearsheet", path="/tearsheet", name="Tear sheet", layout=_layout)
```

`app/src/ygtv/app/__init__.py`: `from ygtv.app.factory import build_app` + `__all__ = ["build_app"]`.
`app/src/ygtv/app/pages/__init__.py`: empty.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run --package ygtv-app pytest app/tests/test_app_smoke.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app
git commit -m "feat(app): generic multipage Dash shell (overview + tear sheet)"
```

---

## Task 11: CI workflow + repo creation + push

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write the CI workflow**

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --all-extras
      - name: ruff check
        run: uv run ruff check .
      - name: ruff format --check
        run: uv run ruff format --check .
      - name: pytest
        run: uv run pytest
        env:
          PYTHONIOENCODING: utf-8
          PYTHONUTF8: "1"
```

- [ ] **Step 2: Run the full suite + lint locally**

Run: `uv run ruff check . ; uv run ruff format --check . ; uv run pytest`
Expected: ruff clean (both), all tests PASS.

- [ ] **Step 3: Create the GitHub repo and push**

```bash
gh repo create Why-Gee/YgTradingVisualizer --private --source=. --remote=origin --description "Source-agnostic trading-performance visualization layer (Plotly Dash). Renders any producer's ygperf reports."
git branch -M main
git push -u origin main
```

- [ ] **Step 4: Verify CI is green**

Run: `gh run watch` (or `gh run list`)
Expected: the `ci` workflow passes on `main`.

- [ ] **Step 5: Generate `CLAUDE.md`**

Use the `/init` skill to write `CLAUDE.md` (workspace layout, `uv run --package <slug> pytest`, ruff-both gate, namespace conventions). Commit:
```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md"
git push
```

---

## Self-Review

**Spec coverage:** §2 packages → Tasks 1,6,8,10. §3 contract → Tasks 2-5. §4 storage (JSON+sidecars) → Task 5 + DirectorySource Task 8 (hf:// path-handling in `read_report`). §6 deploy-ready (`app.server`) → Task 10 Step 4 + smoke assert. §6 quantstats optional → `app[quantstats]` extra Task 10. §7 live file-poll → Task 9. §9 testing/CI (ruff both + pytest, Windows UTF-8) → Task 11. **Gap intentionally deferred:** Regression-over-time page, factor-attribution, cost×time panels (spec Phase 2) and the bridge/producer (Repos B/C) are out of this plan's scope — tracked as follow-on issues + external handoffs.

**Placeholder scan:** No TBD/TODO; every code step shows real code; commands have expected output.

**Type consistency:** `PerfReport` field names identical across Tasks 2/5/6/8/10. `Source` protocol methods `runs()`/`report()` consistent in Tasks 8/9/10. `equity_curve`/`drawdown_curve`/`rolling_sharpe`/`monthly_returns_heatmap` names consistent between Task 7 `__init__` and Task 10 import. `_empty` helper defined in `equity.py` (Task 6), reused in Task 7 — consistent.

---

## Out of scope (this plan) → tracked separately
- **Repo B handoff** — `YgCerebrumVisualizer` bridge (`CerebrumBacktestSource`, cerebrum pages).
- **Repo C handoff** — cerebrum `ygperf` emission (canonical 3 evals + run-store).
- **Phase 2 (Repo A)** — regression-over-time, factor-attribution, cost×time components/pages.
