from __future__ import annotations

from collections.abc import Callable, Iterable

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from ygtv.app.pages import live, overview, regression, tearsheet


def build_app(
    source,
    *,
    extra_pages: Iterable[Callable[[object], None]] = (),
    live_refresh_ms: int = live.DEFAULT_REFRESH_MS,
) -> Dash:
    """Build a generic multipage Dash app over any ygperf Source.

    `app.server` is the Flask WSGI server (for gunicorn/deploy).
    Auth and hosting configuration are deferred to the deployment layer.

    Parameters
    ----------
    source:
        A ygperf Source (provides ``runs()`` / ``report()``).
    extra_pages:
        Page registrants a source bridge can inject. Each is called as
        ``register(source)`` after the built-in pages, so bridge-specific pages
        (e.g. cerebrum's THE-NUMBER / factor attribution) appear with nav links
        without re-implementing this factory.
    live_refresh_ms:
        Poll period (ms) for the auto-refreshing Live page's ``dcc.Interval``.
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
    regression.register(source)
    live.register(source, refresh_ms=live_refresh_ms)
    for register_page in extra_pages:
        register_page(source)

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
