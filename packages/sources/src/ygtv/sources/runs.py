from __future__ import annotations

import polars as pl


def latest_run_id(runs: pl.DataFrame | None) -> str | None:
    """Return the ``run_id`` of the most recent run (by ``run_ts``), or ``None`` if there are none.

    Operates purely on a ``runs()`` frame, so any Source — live or backtest — can be polled for its
    newest run without the source needing a dedicated ``latest()`` method. Only the ``run_id`` string
    is materialised (never the tz-aware ``run_ts``), so this is safe on Windows polars without tzdata.
    """
    if runs is None or runs.is_empty():
        return None
    return runs.sort("run_ts", descending=True)["run_id"][0]
