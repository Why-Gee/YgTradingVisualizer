from datetime import UTC, datetime

import plotly.graph_objects as go
import polars as pl
import pytest
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.heatmap import monthly_returns_heatmap


def _r(s):
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="r",
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
        git_sha="s",
        git_dirty=False,
        eval_name="e",
        universe="u",
        cost_bps=5.0,
        freq="1M",
        params={},
        metrics={},
        series=s,
        trades=None,
        positions=None,
        extras={},
    )


def test_heatmap_returns_heatmap_trace():
    ts = [datetime(2025, m, 1) for m in range(1, 13)] + [datetime(2026, 1, 1)]
    s = pl.DataFrame({"timestamp": ts, "equity": [1.0] * 13, "returns": [0.01] * 13})
    fig = monthly_returns_heatmap(_r(s))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "heatmap"
    # Numeric check: 2025 Jan has one row with returns=0.01 → sum=0.01
    # z rows are ordered by year; 2025 is first row (index 0), Jan is col index 0
    assert fig.data[0].z[0][0] == pytest.approx(0.01)
