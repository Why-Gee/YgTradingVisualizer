from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go
import polars as pl
from ygtv.components.regression import metric_regression


def _runs() -> pl.DataFrame:
    """Minimal runs frame for testing (naive datetimes, no tz dependency)."""
    return pl.DataFrame(
        {
            "run_id": ["r1", "r2", "r3"],
            "git_sha": ["abcdef1234", "bbcdef5678", "ccdef9012"],
            "run_ts": [
                datetime(2026, 1, 1),
                datetime(2026, 2, 1),
                datetime(2026, 3, 1),
            ],
            "eval_name": ["alpha", "alpha", "beta"],
            "sharpe": [0.5, 0.8, 1.2],
            "maxdd": [-0.1, -0.2, -0.15],
        }
    )


# (a) Multi-row runs frame → one trace; y equals metric values in run_ts order
def test_metric_regression_returns_one_trace_with_correct_values():
    fig = metric_regression(_runs(), "sharpe")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [0.5, 0.8, 1.2]


# (b) eval_name filter restricts rows
def test_metric_regression_eval_name_filter():
    fig = metric_regression(_runs(), "sharpe", eval_name="alpha")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    # Only the two "alpha" rows
    assert list(fig.data[0].y) == [0.5, 0.8]


# (c) Missing metric column → empty figure (0 traces) with annotation
def test_metric_regression_missing_metric_column():
    fig = metric_regression(_runs(), "nonexistent_metric")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations  # annotation present


# (d) Empty frame → empty figure
def test_metric_regression_empty_frame():
    empty = pl.DataFrame(
        {
            "run_id": pl.Series([], dtype=pl.Utf8),
            "git_sha": pl.Series([], dtype=pl.Utf8),
            "run_ts": pl.Series([], dtype=pl.Datetime),
            "eval_name": pl.Series([], dtype=pl.Utf8),
            "sharpe": pl.Series([], dtype=pl.Float64),
            "maxdd": pl.Series([], dtype=pl.Float64),
        }
    )
    fig = metric_regression(empty, "sharpe")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations


# (d-bis) None → empty figure
def test_metric_regression_none_frame():
    fig = metric_regression(None, "sharpe")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations


# (e) Hovertext of a point contains the expected 7-char sha
def test_metric_regression_hovertext_contains_7char_sha():
    fig = metric_regression(_runs(), "sharpe")
    hover_texts = list(fig.data[0].text)
    # First run has git_sha "abcdef1234" → first 7 chars = "abcdef1"
    assert "abcdef1" in hover_texts[0]
    # Second run: "bbcdef5"
    assert "bbcdef5" in hover_texts[1]


# (f) x-axis tick labels are the short (7-char) git SHAs, in run order
def test_metric_regression_xaxis_is_short_git_sha():
    fig = metric_regression(_runs(), "sharpe")
    assert list(fig.layout.xaxis.ticktext) == ["abcdef1", "bbcdef5", "ccdef90"]
