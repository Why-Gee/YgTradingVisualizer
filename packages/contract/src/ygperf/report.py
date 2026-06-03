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
    series: pl.DataFrame | None = None  # cols: timestamp, equity, returns
    trades: pl.DataFrame | None = None
    positions: pl.DataFrame | None = None
    extras: dict[str, Any] = field(default_factory=dict)
