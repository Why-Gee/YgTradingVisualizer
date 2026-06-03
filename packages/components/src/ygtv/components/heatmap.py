from __future__ import annotations

import plotly.graph_objects as go
import polars as pl
from ygperf.report import PerfReport
from ygtv.components._base import _empty


def monthly_returns_heatmap(report: PerfReport) -> go.Figure:
    """Monthly returns heatmap (rows=years, cols=months) from report.series."""
    s = report.series
    if s is None or s.is_empty():
        return _empty("no series")
    df = (
        s.select(
            pl.col("timestamp").dt.year().alias("year"),
            pl.col("timestamp").dt.month().alias("month"),
            pl.col("returns"),
        )
        .group_by(["year", "month"])
        .agg(pl.col("returns").sum())
        .sort(["year", "month"])
    )
    years = sorted(df["year"].unique().to_list())
    z = [[None] * 12 for _ in years]
    yi = {y: i for i, y in enumerate(years)}
    for row in df.iter_rows(named=True):
        z[yi[row["year"]]][row["month"] - 1] = row["returns"]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=[f"{m:02d}" for m in range(1, 13)],
            y=[str(y) for y in years],
            colorscale="RdYlGn",
            zmid=0,
        )
    )
    fig.update_layout(title=f"Monthly returns — {report.eval_name}")
    return fig
