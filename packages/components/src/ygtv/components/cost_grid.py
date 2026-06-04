from __future__ import annotations

from collections.abc import Sequence

import plotly.graph_objects as go
from ygtv.components._base import _empty


def cost_time_grid(
    x_labels: Sequence,
    y_labels: Sequence,
    z: Sequence[Sequence[float]],
    *,
    title: str = "Cost x time",
) -> go.Figure:
    """Heatmap of a cost x time grid."""
    if not x_labels or not y_labels or not z or all(len(row) == 0 for row in z):
        return _empty("no grid")

    fig = go.Figure(
        go.Heatmap(
            z=list(z),
            x=list(x_labels),
            y=list(y_labels),
            colorscale="Viridis",
        )
    )
    fig.update_layout(title=title)
    return fig
