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
                "run_id": r.run_id,
                "git_sha": r.git_sha,
                "run_ts": r.run_ts,
                "eval_name": r.eval_name,
                "cost_bps": r.cost_bps,
                **r.metrics,
            })
        return pl.DataFrame(rows) if rows else pl.DataFrame()

    def report(self, run_id: str) -> PerfReport:
        return read_report(self._dir / f"{run_id}.json")
