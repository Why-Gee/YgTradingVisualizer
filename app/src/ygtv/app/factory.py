from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from ygtv.app.pages import overview, tearsheet


def build_app(source) -> Dash:
    """Build a generic multipage Dash app over any ygperf Source.

    `app.server` is the Flask WSGI server (for gunicorn/deploy).
    Auth and hosting configuration are deferred to the deployment layer.
    """
    dash.page_registry.clear()  # idempotent: don't leak pages across app instances/tests
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder="",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )

    overview.register(source)
    tearsheet.register(source)

    app.layout = dbc.Container(
        [
            html.H3("YgTradingVisualizer"),
            html.Div(
                [
                    dcc.Link(p["name"], href=p["relative_path"], className="me-3")
                    for p in dash.page_registry.values()
                ]
            ),
            html.Hr(),
            dash.page_container,
        ],
        fluid=True,
    )
    return app
