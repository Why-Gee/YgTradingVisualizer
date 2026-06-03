from __future__ import annotations

import math

import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components.equity import _empty


def rolling_sharpe(
    report: PerfReport, *, window: int = 12, periods_per_year: int = 12
) -> go.Figure:
    """Rolling Sharpe ratio from report.series returns. Falls back to empty if series too short."""
    s = report.series
    if s is None or s.height < window:
        return _empty("series too short")
    r = s["returns"].to_list()
    ts = s["timestamp"].to_list()
    out_x, out_y = [], []
    for i in range(window - 1, len(r)):
        win = r[i - window + 1 : i + 1]
        mean = sum(win) / window
        var = sum((x - mean) ** 2 for x in win) / max(window - 1, 1)
        std = math.sqrt(var)
        sharpe = (mean / std * math.sqrt(periods_per_year)) if std > 0 else 0.0
        out_x.append(ts[i])
        out_y.append(sharpe)
    fig = go.Figure(go.Scatter(x=out_x, y=out_y, mode="lines", name="rolling sharpe"))
    fig.update_layout(
        title=f"Rolling Sharpe (w={window}) — {report.eval_name}", yaxis_title="sharpe"
    )
    return fig
