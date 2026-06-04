from __future__ import annotations

import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components._base import _empty

_MIN_SIZE = 6
_MAX_SIZE = 18


def trades_timeline(report: PerfReport) -> go.Figure:
    """Scatter of trade executions: x=timestamp, y=price, coloured/sized by qty."""
    t = report.trades
    if t is None or t.is_empty():
        return _empty("no trades")
    required = {"timestamp", "price"}
    if not required.issubset(t.columns):
        return _empty("no trades")

    xs = t["timestamp"].to_list()
    ys = t["price"].to_list()

    has_qty = "qty" in t.columns
    has_symbol = "symbol" in t.columns

    if has_qty:
        qtys = t["qty"].to_list()
        colors = ["green" if q > 0 else "red" if q < 0 else "gray" for q in qtys]
        abs_qtys = [abs(q) for q in qtys]
        max_q = max(abs_qtys) if abs_qtys else 1.0
        if max_q == 0:
            max_q = 1.0
        sizes = [_MIN_SIZE + (_MAX_SIZE - _MIN_SIZE) * (a / max_q) for a in abs_qtys]
    else:
        colors = None
        sizes = None
        qtys = None

    hover = []
    for i in range(len(xs)):
        parts = [f"price: {ys[i]}"]
        if has_symbol:
            parts.insert(0, f"symbol: {t['symbol'][i]}")
        if has_qty:
            parts.append(f"qty: {qtys[i]}")  # type: ignore[index]
        hover.append("<br>".join(parts))

    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker=go.scatter.Marker(color=colors, size=sizes) if colors is not None else None,
            text=hover,
            hoverinfo="text",
            name="trades",
        )
    )
    fig.update_layout(
        title=f"Trades — {report.eval_name}",
        xaxis_title="time",
        yaxis_title="price",
    )
    return fig
