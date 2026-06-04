from __future__ import annotations

from datetime import UTC, datetime

import plotly.graph_objects as go
import polars as pl
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.positions import positions_over_time


def _report(positions):
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
        trades=None,
        positions=positions,
        extras={},
    )


def _positions_frame():
    return pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 1, 1),
                datetime(2026, 2, 1),
                datetime(2026, 3, 1),
                datetime(2026, 1, 1),
                datetime(2026, 2, 1),
                datetime(2026, 3, 1),
            ],
            "symbol": ["AAPL", "AAPL", "AAPL", "MSFT", "MSFT", "MSFT"],
            "weight": [0.4, 0.5, 0.45, 0.3, 0.25, 0.35],
        }
    )


def test_positions_over_time_returns_two_traces():
    fig = positions_over_time(_report(_positions_frame()))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2


def test_positions_over_time_trace_names_are_symbols():
    fig = positions_over_time(_report(_positions_frame()))
    names = {t.name for t in fig.data}
    assert names == {"AAPL", "MSFT"}


def test_positions_over_time_traces_are_scatter():
    fig = positions_over_time(_report(_positions_frame()))
    for trace in fig.data:
        assert isinstance(trace, go.Scatter)


def test_positions_over_time_stacked_area():
    fig = positions_over_time(_report(_positions_frame()))
    for trace in fig.data:
        assert trace.stackgroup == "one"


def test_positions_over_time_correct_point_count_per_symbol():
    fig = positions_over_time(_report(_positions_frame()))
    for trace in fig.data:
        assert len(trace.x) == 3


def test_positions_over_time_none_returns_empty():
    fig = positions_over_time(_report(None))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_positions_over_time_missing_required_col_returns_empty():
    p = pl.DataFrame({"timestamp": [datetime(2026, 1, 1)], "symbol": ["AAPL"]})
    fig = positions_over_time(_report(p))
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_positions_over_time_empty_frame_returns_empty():
    p = pl.DataFrame(
        {
            "timestamp": pl.Series([], dtype=pl.Datetime),
            "symbol": pl.Series([], dtype=pl.Utf8),
            "weight": pl.Series([], dtype=pl.Float64),
        }
    )
    fig = positions_over_time(_report(p))
    assert len(fig.data) == 0
    assert fig.layout.annotations
