from datetime import UTC, datetime

import plotly.graph_objects as go
import polars as pl
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.drawdown import drawdown_curve


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


def test_drawdown_is_nonpositive_and_one_trace():
    s = pl.DataFrame(
        {
            "timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1), datetime(2026, 3, 1)],
            "equity": [1.0, 1.2, 0.9],
            "returns": [0.0, 0.2, -0.25],
        }
    )
    fig = drawdown_curve(_r(s))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert min(fig.data[0].y) < 0
    assert max(fig.data[0].y) <= 0.0
    assert fig.data[0].fill == "tozeroy"  # model drawdown stays filled


def test_drawdown_handles_missing_series_defensively():
    fig = drawdown_curve(_r(None))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert fig.layout.annotations  # "no series" annotation


def test_drawdown_overlays_both_benchmarks_three_traces():
    s = pl.DataFrame(
        {
            "timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1), datetime(2026, 3, 1)],
            "equity": [1.0, 1.2, 0.9],
            "returns": [0.0, 0.2, -0.25],
            "benchmark_equity": [1.0, 1.1, 1.0],
            "benchmark_cw_equity": [1.0, 1.05, 0.95],
        }
    )
    fig = drawdown_curve(_r(s))
    assert len(fig.data) == 3
    assert [t.name for t in fig.data] == ["model", "SP500 (cap-wt)", "SP500 (EW)"]
    # Every drawdown series is non-positive.
    for trace in fig.data:
        assert max(trace.y) <= 0.0
    # Fill stays on the model only — overlaid fills are noisy.
    assert fig.data[0].fill == "tozeroy"
    assert fig.data[1].fill is None
    assert fig.data[2].fill is None


def test_drawdown_overlays_ew_benchmark_only_two_traces():
    s = pl.DataFrame(
        {
            "timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1), datetime(2026, 3, 1)],
            "equity": [1.0, 1.2, 0.9],
            "returns": [0.0, 0.2, -0.25],
            "benchmark_equity": [1.0, 1.1, 1.0],
        }
    )
    fig = drawdown_curve(_r(s))
    assert len(fig.data) == 2
    assert [t.name for t in fig.data] == ["model", "SP500 (EW)"]


def test_drawdown_overlays_baseline_then_benchmarks_four_traces():
    s = pl.DataFrame(
        {
            "timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1), datetime(2026, 3, 1)],
            "equity": [1.0, 1.2, 0.9],
            "returns": [0.0, 0.2, -0.25],
            "baseline_equity": [1.0, 1.15, 0.85],
            "benchmark_equity": [1.0, 1.1, 1.0],
            "benchmark_cw_equity": [1.0, 1.05, 0.95],
        }
    )
    fig = drawdown_curve(_r(s))
    assert len(fig.data) == 4
    assert [t.name for t in fig.data] == [
        "model",
        "baseline (before)",
        "SP500 (cap-wt)",
        "SP500 (EW)",
    ]
    for trace in fig.data:
        assert max(trace.y) <= 0.0
    # Fill stays on the model only.
    assert fig.data[0].fill == "tozeroy"
    assert all(t.fill is None for t in fig.data[1:])
