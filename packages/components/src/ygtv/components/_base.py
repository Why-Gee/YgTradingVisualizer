from __future__ import annotations

import plotly.graph_objects as go

# Optional benchmark overlays, in plot order: (equity column, legend name, line dash).
# A trace is drawn only when its column is present in the report's series, so single-series
# reports render the model alone. Shared by equity_curve and drawdown_curve so the legend
# naming and styling have a single source of truth across both charts.
#   benchmark_cw_* = SP500 (cap-weighted) — the literal index (may be absent in older runs)
#   benchmark_*    = SP500 (EW)           — the members_asof equal-weight market
BENCHMARK_TRACES: tuple[tuple[str, str, str], ...] = (
    ("benchmark_cw_equity", "SP500 (cap-wt)", "dot"),
    ("benchmark_equity", "SP500 (EW)", "dash"),
)


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
    return fig
