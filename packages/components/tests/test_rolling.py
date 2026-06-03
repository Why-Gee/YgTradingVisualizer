from datetime import UTC, datetime, timezone

import plotly.graph_objects as go
import polars as pl
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
