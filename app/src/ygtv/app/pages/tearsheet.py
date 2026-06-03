from __future__ import annotations

import dash
from dash import dcc, html
from ygtv.components import drawdown_curve, equity_curve, monthly_returns_heatmap, rolling_sharpe


def register(source) -> None:
    """Register the Tear Sheet page at '/tearsheet' with a run dropdown and four figures."""
    runs = source.runs()
    run_ids = runs["run_id"].to_list() if not runs.is_empty() else []
    default = run_ids[0] if run_ids else None

    def _layout(run_id: str | None = default):
        if not run_id:
            return html.Div("No runs available.")
        rep = source.report(run_id)
        return html.Div(
            [
                html.H4(f"Tear sheet — {rep.eval_name} @ {rep.git_sha[:7]}"),
                dcc.Dropdown(run_ids, run_id, id="ts-run"),
                dcc.Graph(figure=equity_curve(rep)),
                dcc.Graph(figure=drawdown_curve(rep)),
                dcc.Graph(figure=rolling_sharpe(rep)),
                dcc.Graph(figure=monthly_returns_heatmap(rep)),
            ]
        )

    dash.register_page("tearsheet", path="/tearsheet", name="Tear sheet", layout=_layout)
