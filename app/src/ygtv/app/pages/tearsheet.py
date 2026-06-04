from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
from ygtv.components import (
    drawdown_curve,
    equity_curve,
    monthly_returns_heatmap,
    positions_over_time,
    rolling_sharpe,
    trades_timeline,
)

# Module-level flag to prevent duplicate callback registration across build_app calls
_callback_registered = False


def _render_figures(source, run_id: str) -> list:
    """Return dcc.Graph components for the given run_id (4-6 depending on data)."""
    rep = source.report(run_id)
    graphs = [
        dcc.Graph(figure=equity_curve(rep)),
        dcc.Graph(figure=drawdown_curve(rep)),
        dcc.Graph(figure=rolling_sharpe(rep)),
        dcc.Graph(figure=monthly_returns_heatmap(rep)),
    ]
    if rep.trades is not None:
        graphs.append(dcc.Graph(figure=trades_timeline(rep)))
    if rep.positions is not None:
        graphs.append(dcc.Graph(figure=positions_over_time(rep)))
    return graphs


def register(source) -> None:
    """Register the Tear Sheet page at '/tearsheet' with a run dropdown and 4-6 figures."""
    global _callback_registered

    runs = source.runs()
    run_ids = runs["run_id"].to_list() if not runs.is_empty() else []
    default = run_ids[0] if run_ids else None

    if not run_ids:
        layout = html.Div("No runs available.")
        dash.register_page("tearsheet", path="/tearsheet", name="Tear sheet", layout=layout)
        return

    initial_figures = _render_figures(source, default)

    layout = html.Div(
        [
            html.H4("Tear sheet"),
            dcc.Dropdown(run_ids, default, id="ts-run"),
            html.Div(initial_figures, id="ts-figures"),
        ]
    )

    dash.register_page("tearsheet", path="/tearsheet", name="Tear sheet", layout=layout)

    if not _callback_registered:
        _callback_registered = True

        @callback(
            Output("ts-figures", "children"),
            Input("ts-run", "value"),
            prevent_initial_call=True,
        )
        def _on_select(run_id: str | None) -> list:
            return _render_figures(source, run_id) if run_id else []
