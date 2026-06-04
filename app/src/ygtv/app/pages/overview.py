from __future__ import annotations

import dash
import dash_ag_grid as dag
import polars as pl
from dash import html


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
                if t == pl.Datetime
            ]
        )

    records = runs.to_dicts() if not runs.is_empty() else []
    columns = runs.columns if not runs.is_empty() else ["run_id"]

    layout = html.Div(
        [
            html.H4("Overview"),
            dag.AgGrid(
                id="overview-grid",
                rowData=records,
                columnDefs=[{"field": c} for c in columns],
                defaultColDef={"sortable": True, "filter": True, "resizable": True},
                dashGridOptions={"pagination": True, "paginationPageSize": 20},
                style={"height": 480},
            ),
        ]
    )
    dash.register_page("overview", path="/", name="Overview", layout=layout)
