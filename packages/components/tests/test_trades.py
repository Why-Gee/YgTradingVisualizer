from __future__ import annotations

from datetime import UTC, datetime

import plotly.graph_objects as go
import polars as pl
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.trades import trades_timeline


def _report(trades):
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
        series=None,
        trades=trades,
        positions=None,
        extras={},
    )


def _trades_frame():
    return pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 1, 1),
                datetime(2026, 1, 2),
                datetime(2026, 1, 3),
            ],
            "symbol": ["AAPL", "AAPL", "MSFT"],
            "qty": [100.0, -50.0, 200.0],
            "price": [150.0, 155.0, 300.0],
        }
    )


def test_trades_timeline_returns_one_scatter_trace():
    fig = trades_timeline(_report(_trades_frame()))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert isinstance(fig.data[0], go.Scatter)


def test_trades_timeline_marker_mode():
    fig = trades_timeline(_report(_trades_frame()))
    assert fig.data[0].mode == "markers"


def test_trades_timeline_correct_point_count():
    fig = trades_timeline(_report(_trades_frame()))
    assert len(fig.data[0].x) == 3
    assert len(fig.data[0].y) == 3


def test_trades_timeline_marker_colors_by_sign():
    fig = trades_timeline(_report(_trades_frame()))
    colors = list(fig.data[0].marker.color)
    # qty: 100, -50, 200 → green, red, green
    assert colors[0] == "green"
    assert colors[1] == "red"
    assert colors[2] == "green"


def test_trades_timeline_y_values_are_prices():
    fig = trades_timeline(_report(_trades_frame()))
    assert list(fig.data[0].y) == [150.0, 155.0, 300.0]


def test_trades_timeline_none_returns_empty():
    fig = trades_timeline(_report(None))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_trades_timeline_missing_required_col_returns_empty():
    # Missing 'price' column
    t = pl.DataFrame({"timestamp": [datetime(2026, 1, 1)]})
    fig = trades_timeline(_report(t))
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_trades_timeline_empty_frame_returns_empty():
    t = pl.DataFrame(
        {
            "timestamp": pl.Series([], dtype=pl.Datetime),
            "price": pl.Series([], dtype=pl.Float64),
        }
    )
    fig = trades_timeline(_report(t))
    assert len(fig.data) == 0
    assert fig.layout.annotations
