from __future__ import annotations

import plotly.graph_objects as go

# Optional overlay traces drawn on top of the model, in plot order: (equity column, legend
# name, line dash). A trace is drawn only when its column is present in the report's series,
# so single-series reports render the model alone. Shared by equity_curve and drawdown_curve
# so the legend naming and styling have a single source of truth across both charts.
#   baseline_*     = baseline (before) — a model variant (e.g. the pre-hardening deployable)
#   benchmark_cw_* = SP500 (cap-weighted) — the literal index (may be absent in older runs)
#   benchmark_*    = SP500 (EW)           — the members_asof equal-weight market
# Baseline is ordered first (right after the model) since it's a model variant, not a market.
OVERLAY_TRACES: tuple[tuple[str, str, str], ...] = (
    ("baseline_equity", "baseline (before)", "dashdot"),
    ("benchmark_cw_equity", "SP500 (cap-wt)", "dot"),
    ("benchmark_equity", "SP500 (EW)", "dash"),
)


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
    return fig
