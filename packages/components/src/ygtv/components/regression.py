from __future__ import annotations

import plotly.graph_objects as go
import polars as pl
from ygtv.components._base import _empty


def metric_regression(
    runs: pl.DataFrame | None,
    metric: str,
    *,
    eval_name: str | None = None,
) -> go.Figure:
    """Plot a metric value over successive runs (git SHA timeline).

    Parameters
    ----------
    runs:
        DataFrame with at least columns: run_id, git_sha, run_ts, eval_name, <metric>.
    metric:
        Name of the numeric column to plot on the y-axis.
    eval_name:
        If given and an ``eval_name`` column exists, restrict to rows where
        ``eval_name`` matches this value.
    """
    if runs is None or runs.is_empty():
        return _empty(f"no data for {metric}")

    if metric not in runs.columns:
        return _empty(f"no data for {metric}")

    df = runs

    if eval_name is not None and "eval_name" in df.columns:
        df = df.filter(pl.col("eval_name") == eval_name)

    if df.is_empty():
        return _empty(f"no data for {metric}")

    df = df.sort("run_ts")

    # Build per-point hovertext
    hover_parts_exprs = [
        pl.format("sha: {}", pl.col("git_sha").str.slice(0, 7)),
        pl.format("run_ts: {}", pl.col("run_ts").cast(pl.String)),
    ]
    if "eval_name" in df.columns:
        hover_parts_exprs.append(pl.format("eval: {}", pl.col("eval_name")))

    # Concatenate the parts with newlines
    hovertext_expr = hover_parts_exprs[0]
    for part in hover_parts_exprs[1:]:
        hovertext_expr = pl.concat_str([hovertext_expr, part], separator="<br>")

    df = df.with_columns(hovertext_expr.alias("_hover"))

    # x = run order (sorted by run_ts), tick-labelled by short git SHA. An index-based x keeps
    # every run distinct even when two runs share a SHA (a categorical SHA axis would merge them).
    shas7 = [s[:7] for s in df["git_sha"].to_list()]
    x = list(range(len(shas7)))

    fig = go.Figure(
        go.Scatter(
            x=x,
            y=df[metric].to_list(),
            mode="lines+markers",
            text=df["_hover"].to_list(),
            hoverinfo="text+y",
            name=metric,
        )
    )
    fig.update_xaxes(tickmode="array", tickvals=x, ticktext=shas7)
    fig.update_layout(
        title=f"{metric} over runs",
        xaxis_title="git sha (run order)",
        yaxis_title=metric,
    )
    return fig
