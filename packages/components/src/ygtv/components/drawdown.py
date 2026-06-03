from __future__ import annotations

import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components._base import _empty


def drawdown_curve(report: PerfReport) -> go.Figure:
    """Drawdown curve from report.series (cols: timestamp, equity). All values <= 0."""
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    eq = s["equity"].to_list()
    peak = eq[0]
    dd = []
    for v in eq:
        peak = max(peak, v)
        dd.append(v / peak - 1.0)
    fig = go.Figure(go.Scatter(x=s["timestamp"].to_list(), y=dd, fill="tozeroy", name="drawdown"))
    fig.update_layout(title=f"Drawdown — {report.eval_name}", yaxis_title="drawdown")
    return fig
