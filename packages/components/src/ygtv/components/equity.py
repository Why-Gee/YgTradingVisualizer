from __future__ import annotations

import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components._base import BENCHMARK_TRACES, _empty


def equity_curve(report: PerfReport) -> go.Figure:
    """Equity curve from report.series (cols: timestamp, equity).

    Always plots the model. Overlays an optional benchmark line for each benchmark
    ``*_equity`` column present (see ``BENCHMARK_TRACES``) — so single-series reports
    render the model alone and benchmark-bearing reports show the model-vs-SP500 comparison.
    """
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    t = s["timestamp"].to_list()
    fig = go.Figure()
    fig.add_scatter(x=t, y=s["equity"].to_list(), mode="lines", name="model")
    for col, name, dash in BENCHMARK_TRACES:
        if col in s.columns:
            fig.add_scatter(x=t, y=s[col].to_list(), mode="lines", name=name, line={"dash": dash})
    fig.update_layout(
        title=f"Equity — {report.eval_name}", xaxis_title="time", yaxis_title="equity"
    )
    return fig
