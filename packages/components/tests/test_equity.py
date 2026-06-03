from datetime import datetime, timezone

import plotly.graph_objects as go
import polars as pl

from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.equity import equity_curve


def _report(series):
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="r",
        run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc),
        git_sha="s",
        git_dirty=False,
        eval_name="e",
        universe="u",
        cost_bps=5.0,
        freq="1M",
        params={},
        metrics={},
        series=series,
        trades=None,
        positions=None,
        extras={},
    )


def test_equity_curve_returns_figure_with_one_trace():
    s = pl.DataFrame(
        {
            "timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1)],
            "equity": [1.0, 1.2],
            "returns": [0.0, 0.2],
        }
    )
    fig = equity_curve(_report(s))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [1.0, 1.2]


def test_equity_curve_handles_missing_series_defensively():
    fig = equity_curve(_report(None))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations  # shows a "no series" annotation
