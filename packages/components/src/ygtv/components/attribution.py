from __future__ import annotations

from collections.abc import Sequence

import plotly.graph_objects as go
from ygtv.components._base import _empty


def factor_attribution_bars(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    title: str = "Factor attribution",
) -> go.Figure:
    """Horizontal bar chart of factor attribution contributions."""
    if not labels or not values or len(labels) != len(values):
        return _empty("no factors")

    colors = ["green" if v >= 0 else "red" for v in values]

    fig = go.Figure(
        go.Bar(
            orientation="h",
            y=list(labels),
            x=list(values),
            marker_color=colors,
            name="attribution",
        )
    )
    fig.update_layout(title=title, xaxis_title="contribution")
    return fig
