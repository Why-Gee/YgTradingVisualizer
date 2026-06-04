from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
from ygtv.components import drawdown_curve, equity_curve, rolling_sharpe
from ygtv.sources import latest_run_id

# Module-level flag to prevent duplicate callback registration across build_app calls
_callback_registered = False

# Default dcc.Interval poll period (ms). Overridable via build_app(live_refresh_ms=...).
DEFAULT_REFRESH_MS = 5000

# Lean monitoring set: rendered on every tick, so deliberately fewer than the full tear sheet.
_LIVE_FIGURES = (equity_curve, drawdown_curve, rolling_sharpe)


def _body_content(source):
    """Children for the live-body container: the latest run's figures, or a placeholder.

    Source-agnostic — derives the newest run from ``source.runs()``, so it works over any Source
    (a backtest DirectorySource or a polling LiveSource alike).
    """
    run_id = latest_run_id(source.runs())
    if run_id is None:
        return "No runs yet."
    rep = source.report(run_id)
    return [
        html.Small(f"Latest run: {run_id}"),
        *[dcc.Graph(figure=make(rep)) for make in _LIVE_FIGURES],
    ]


def _build_layout(source, refresh_ms: int) -> html.Div:
    return html.Div(
        [
            html.H4("Live"),
            dcc.Interval(id="live-interval", interval=refresh_ms, n_intervals=0),
            html.Div(_body_content(source), id="live-body"),
        ]
    )


def register(source, *, refresh_ms: int = DEFAULT_REFRESH_MS) -> None:
    """Register the auto-refreshing Live page at '/live'.

    A ``dcc.Interval`` re-queries the source every ``refresh_ms`` ms and re-renders the latest run.
    ``layout`` is a callable so each navigation also pulls fresh data.
    """
    global _callback_registered

    dash.register_page(
        "live",
        path="/live",
        name="Live",
        layout=lambda: _build_layout(source, refresh_ms),
    )

    if not _callback_registered:
        _callback_registered = True

        @callback(
            Output("live-body", "children"),
            Input("live-interval", "n_intervals"),
            prevent_initial_call=True,
        )
        def _tick(_n):
            return _body_content(source)
