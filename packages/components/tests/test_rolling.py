from __future__ import annotations

import math
from datetime import UTC, datetime

import plotly.graph_objects as go
import polars as pl
import pytest
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.components.rolling import rolling_sharpe


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


def test_rolling_sharpe_returns_figure():
    ts = [datetime(2026, m, 1) for m in range(1, 13)]
    s = pl.DataFrame(
        {
            "timestamp": ts,
            "equity": [1.0] * 12,
            "returns": [0.01, -0.02, 0.03, 0.0, 0.02, -0.01, 0.04, 0.01, -0.03, 0.02, 0.0, 0.01],
        }
    )
    fig = rolling_sharpe(_r(s), window=3, periods_per_year=12)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    # Numeric check: first output point uses window [0.01, -0.02, 0.03]
    # mean=0.006667, var=0.000633 (sample), std=0.025166, sharpe=mean/std*sqrt(12)
    win0 = [0.01, -0.02, 0.03]
    mean0 = sum(win0) / 3
    var0 = sum((x - mean0) ** 2 for x in win0) / 2
    expected_sharpe0 = mean0 / math.sqrt(var0) * math.sqrt(12)
    assert fig.data[0].y[0] == pytest.approx(expected_sharpe0)
