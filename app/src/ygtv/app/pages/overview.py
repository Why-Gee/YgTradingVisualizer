from __future__ import annotations

import dash
import polars as pl
from dash import dash_table, html


def register(source) -> None:
    """Register the Overview page at '/' showing a table of all runs."""
    runs = source.runs()

    # Convert tz-aware Datetime columns to display strings before to_dicts()
    # (Windows polars panics on tz-aware → Python datetime materialisation without tzdata)
    if not runs.is_empty():
        runs = runs.with_columns(
            [
                pl.col(c).dt.to_string("%Y-%m-%d %H:%M")
                for c, t in zip(runs.columns, runs.dtypes, strict=False)
                if t == pl.Datetime or (hasattr(t, "base_type") and t.base_type() == pl.Datetime)
            ]
        )

    records = runs.to_dicts() if not runs.is_empty() else []
    columns = [{"name": c, "id": c} for c in (runs.columns if not runs.is_empty() else ["run_id"])]

    layout = html.Div(
        [
            html.H4("Overview"),
            dash_table.DataTable(
                data=records,
                columns=columns,
                page_size=20,
                sort_action="native",
            ),
        ]
    )
    dash.register_page("overview", path="/", name="Overview", layout=layout)
