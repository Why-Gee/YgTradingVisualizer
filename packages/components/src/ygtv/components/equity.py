from __future__ import annotations

import plotly.graph_objects as go

from ygperf.report import PerfReport


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
    return fig


def equity_curve(report: PerfReport) -> go.Figure:
    """Equity curve from report.series (cols: timestamp, equity)."""
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    fig = go.Figure(
        go.Scatter(x=s["timestamp"].to_list(), y=s["equity"].to_list(), mode="lines", name="equity")
    )
    fig.update_layout(
        title=f"Equity — {report.eval_name}", xaxis_title="time", yaxis_title="equity"
    )
    return fig
