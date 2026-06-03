from datetime import UTC, datetime, timezone

import plotly.graph_objects as go
import polars as pl
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
