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
