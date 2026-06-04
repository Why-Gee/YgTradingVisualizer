from __future__ import annotations

from datetime import UTC, datetime

import polars as pl
from ygtv.sources import latest_run_id


def _runs(rows: list[tuple[str, datetime]]) -> pl.DataFrame:
    return pl.DataFrame(
        {"run_id": [r for r, _ in rows], "run_ts": [t for _, t in rows]},
    )


# Picks the run_id of the newest run_ts, regardless of row order
def test_latest_run_id_picks_newest_by_run_ts():
    runs = _runs(
        [
            ("old", datetime(2026, 6, 3, 9, tzinfo=UTC)),
            ("newest", datetime(2026, 6, 3, 12, tzinfo=UTC)),
            ("mid", datetime(2026, 6, 3, 10, tzinfo=UTC)),
        ]
    )
    assert latest_run_id(runs) == "newest"


# Empty frame → None (no run yet)
def test_latest_run_id_empty_frame_returns_none():
    empty = pl.DataFrame(schema={"run_id": pl.String, "run_ts": pl.Datetime})
    assert latest_run_id(empty) is None


# None → None
def test_latest_run_id_none_returns_none():
    assert latest_run_id(None) is None
