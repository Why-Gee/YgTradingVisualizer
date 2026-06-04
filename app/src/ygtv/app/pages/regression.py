from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
from ygtv.components import metric_regression

# Module-level flag to prevent duplicate callback registration across build_app calls
_callback_registered = False

# Columns that are never plotted as metrics (run metadata, not metrics)
_RESERVED = {"run_id", "git_sha", "run_ts", "eval_name", "universe", "cost_bps", "git_dirty"}

# Sentinel for the "All evals" choice — null-byte prefix can't collide with a real eval_name
_ALL_EVALS = "\x00ALL"


def _metric_columns(runs) -> list[str]:
    """Return numeric columns that are not in the reserved set."""
    return [
        col
        for col, dtype in zip(runs.columns, runs.dtypes, strict=True)
        if col not in _RESERVED and dtype.is_numeric()
    ]


def register(source) -> None:
    """Register the Regression-over-time page at '/regression'."""
    global _callback_registered

    runs = source.runs()

    if runs is None or runs.is_empty():
        layout = html.Div("No runs available.")
        dash.register_page("regression", path="/regression", name="Regression", layout=layout)
        return

    metrics = _metric_columns(runs)

    if not metrics:
        layout = html.Div("No numeric metrics available.")
        dash.register_page("regression", path="/regression", name="Regression", layout=layout)
        return

    # Eval options: an "All" sentinel that cannot collide with a real eval_name, then sorted uniques
    eval_options = [{"label": "All", "value": _ALL_EVALS}]
    if "eval_name" in runs.columns:
        eval_options += [
            {"label": e, "value": e}
            for e in sorted(runs["eval_name"].drop_nulls().unique().to_list())
        ]

    default_metric = metrics[0]

    initial_figure = metric_regression(runs, default_metric)

    def _layout():
        return html.Div(
            [
                html.H4("Regression over time"),
                dcc.Dropdown(metrics, default_metric, id="reg-metric"),
                dcc.Dropdown(eval_options, _ALL_EVALS, id="reg-eval"),
                html.Div(
                    dcc.Graph(figure=initial_figure),
                    id="reg-figure",
                ),
            ]
        )

    dash.register_page("regression", path="/regression", name="Regression", layout=_layout)

    if not _callback_registered:
        _callback_registered = True

        @callback(
            Output("reg-figure", "children"),
            Input("reg-metric", "value"),
            Input("reg-eval", "value"),
            prevent_initial_call=True,
        )
        def _on_select(metric: str | None, eval_val: str | None):
            if not metric:
                return []
            eval_name = None if eval_val in (None, _ALL_EVALS) else eval_val
            return dcc.Graph(figure=metric_regression(source.runs(), metric, eval_name=eval_name))
