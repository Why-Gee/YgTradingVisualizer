from __future__ import annotations

import plotly.graph_objects as go
from ygperf.report import PerfReport
from ygtv.components._base import OVERLAY_TRACES, _empty


def _drawdown(equity: list[float]) -> list[float]:
    """Peak-to-trough drawdown for an equity path. All values <= 0."""
    peak = equity[0]
    out: list[float] = []
    for v in equity:
        peak = max(peak, v)
        out.append(v / peak - 1.0)
    return out


def drawdown_curve(report: PerfReport) -> go.Figure:
    """Drawdown curve from report.series (cols: timestamp, equity). All values <= 0.

    Plots the model drawdown (filled), plus an optional line for each overlay ``*_equity``
    column present (see ``OVERLAY_TRACES``: baseline + SP500 benchmarks). Fill stays on the
    model only — overlaid fills are noisy.
    """
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    t = s["timestamp"].to_list()
    fig = go.Figure()
    fig.add_scatter(
        x=t, y=_drawdown(s["equity"].to_list()), mode="lines", fill="tozeroy", name="model"
    )
    for col, name, dash in OVERLAY_TRACES:
        if col in s.columns:
            fig.add_scatter(
                x=t, y=_drawdown(s[col].to_list()), mode="lines", name=name, line={"dash": dash}
            )
    fig.update_layout(title=f"Drawdown — {report.eval_name}", yaxis_title="drawdown")
    return fig
