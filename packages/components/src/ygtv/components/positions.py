from __future__ import annotations

import plotly.graph_objects as go
import polars as pl
from ygperf.report import PerfReport
from ygtv.components._base import _empty


def positions_over_time(report: PerfReport) -> go.Figure:
    """Stacked area of per-symbol portfolio weights over time."""
    p = report.positions
    if p is None or p.is_empty():
        return _empty("no positions")
    required = {"timestamp", "symbol", "weight"}
    if not required.issubset(p.columns):
        return _empty("no positions")

    fig = go.Figure()
    symbols = sorted(p["symbol"].unique().to_list())
    for sym in symbols:
        sub = p.filter(pl.col("symbol") == sym).sort("timestamp")
        fig.add_trace(
            go.Scatter(
                x=sub["timestamp"].to_list(),
                y=sub["weight"].to_list(),
                stackgroup="one",
                name=sym,
            )
        )
    fig.update_layout(
        title=f"Positions — {report.eval_name}",
        xaxis_title="time",
        yaxis_title="weight",
    )
    return fig
