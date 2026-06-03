from __future__ import annotations

from pathlib import Path

import polars as pl
from ygperf.io import read_report
from ygperf.report import PerfReport

_RESERVED = {"run_id", "git_sha", "run_ts", "eval_name", "cost_bps"}

_EMPTY = pl.DataFrame(
    schema={
        "run_id": pl.String,
        "git_sha": pl.String,
        "run_ts": pl.Datetime,
        "eval_name": pl.String,
        "cost_bps": pl.Float64,
    }
)


class DirectorySource:
    """Reads ygperf JSON reports from a directory (glob `*.json`). Source-agnostic."""

    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)

    def _json_paths(self) -> list[Path]:
        return sorted(self._dir.glob("*.json"))

    def runs(self) -> pl.DataFrame:
        rows = []
        for p in self._json_paths():
            try:
                r = read_report(p, load_frames=False)
            except Exception as e:
                raise ValueError(f"failed to read report {p}") from e
            collisions = _RESERVED & r.metrics.keys()
            if collisions:
                key = next(iter(collisions))
                raise ValueError(
                    f"report {r.run_id!r} has a metric named {key!r} that collides with a reserved column"
                )
            rows.append(
                {
                    "run_id": r.run_id,
                    "git_sha": r.git_sha,
                    "run_ts": r.run_ts,
                    "eval_name": r.eval_name,
                    "cost_bps": r.cost_bps,
                    **r.metrics,
                }
            )
        return pl.DataFrame(rows) if rows else _EMPTY

    def report(self, run_id: str) -> PerfReport:
        path = self._dir / f"{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"no report with run_id {run_id!r} in {self._dir}")
        return read_report(path)
