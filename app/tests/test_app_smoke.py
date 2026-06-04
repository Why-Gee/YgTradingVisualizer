from datetime import UTC, datetime

import dash
import plotly.graph_objects as go
import polars as pl
from dash import Dash
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.app.factory import build_app
from ygtv.app.pages.tearsheet import _render_figures


class _FakeSource:
    def runs(self):
        return pl.DataFrame(
            {
                "run_id": ["r1"],
                "git_sha": ["s1"],
                "run_ts": [datetime(2026, 6, 3, tzinfo=UTC)],
                "eval_name": ["e"],
                "sharpe": [0.85],
            }
        )

    def report(self, run_id):
        return PerfReport(
            schema_version=SCHEMA_VERSION,
            run_id=run_id,
            run_ts=datetime(2026, 6, 3, tzinfo=UTC),
            git_sha="s1",
            git_dirty=False,
            eval_name="e",
            universe="u",
            cost_bps=5.0,
            freq="1M",
            params={},
            metrics={"sharpe": 0.85},
            series=pl.DataFrame(
                {"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}
            ),
            trades=None,
            positions=None,
            extras={},
        )


def test_build_app_returns_dash_with_pages_and_flask_server():
    app = build_app(_FakeSource())
    assert isinstance(app, Dash)
    assert app.layout is not None
    assert app.server is not None  # Flask server exposed for deploy
    paths = {p["path"] for p in dash.page_registry.values()}
    assert {"/", "/tearsheet", "/regression"} <= paths


def test_build_app_idempotent_no_page_leak():
    """Calling build_app twice must not leak or duplicate page registrations."""
    build_app(_FakeSource())
    build_app(_FakeSource())
    paths = {p["path"] for p in dash.page_registry.values()}
    assert paths == {"/", "/tearsheet", "/regression"}
    assert len(dash.page_registry) == 3


def test_render_figures_returns_four_graphs():
    """_render_figures returns exactly 4 dcc.Graph components with go.Figure figures."""
    figures = _render_figures(_FakeSource(), "r1")
    assert len(figures) == 4
    for graph in figures:
        assert isinstance(graph, dash.dcc.Graph)
        assert isinstance(graph.figure, go.Figure)
