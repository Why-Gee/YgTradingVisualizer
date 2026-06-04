from __future__ import annotations

from datetime import UTC, datetime

import dash
import plotly.graph_objects as go
import polars as pl
from dash import Dash, dcc
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.app.factory import build_app
from ygtv.app.pages.live import _body_content, _build_layout


def _report(run_id: str) -> PerfReport:
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id=run_id,
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
        git_sha="s",
        git_dirty=False,
        eval_name=run_id,  # echo run_id so a test can assert which run was rendered
        universe="u",
        cost_bps=0.0,
        freq="1d",
        params={},
        metrics={"sharpe": 1.0},
        series=pl.DataFrame(
            {"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}
        ),
        trades=None,
        positions=None,
        extras={},
    )


class _TwoRunSource:
    def runs(self):
        return pl.DataFrame(
            {
                "run_id": ["old", "new"],
                "git_sha": ["a", "b"],
                "run_ts": [
                    datetime(2026, 6, 3, 9, tzinfo=UTC),
                    datetime(2026, 6, 3, 12, tzinfo=UTC),
                ],
                "eval_name": ["e", "e"],
                "sharpe": [0.5, 0.9],
            }
        )

    def report(self, run_id):
        return _report(run_id)


class _EmptySource:
    def runs(self):
        return pl.DataFrame(
            schema={
                "run_id": pl.String,
                "git_sha": pl.String,
                "run_ts": pl.Datetime,
                "eval_name": pl.String,
            }
        )

    def report(self, run_id):  # pragma: no cover - must not be reached
        raise AssertionError("report() must not be called when there are no runs")


def _graphs(content) -> list:
    return [c for c in content if isinstance(c, dcc.Graph)]


# Renders 3 monitoring figures (equity, drawdown, rolling sharpe) for the latest run
def test_live_body_renders_three_graphs_for_latest_run():
    content = _body_content(_TwoRunSource())
    graphs = _graphs(content)
    assert len(graphs) == 3
    for g in graphs:
        assert isinstance(g.figure, go.Figure)


# Picks the NEWEST run by run_ts (header echoes its run_id)
def test_live_body_uses_newest_run():
    content = _body_content(_TwoRunSource())
    header = content[0]
    assert "new" in header.children
    assert "old" not in header.children


# Empty source → placeholder, no graphs; report() is never called
def test_live_body_placeholder_when_no_runs():
    assert _body_content(_EmptySource()) == "No runs yet."


# refresh_ms threads into the dcc.Interval poll period
def test_build_layout_threads_refresh_ms():
    layout = _build_layout(_TwoRunSource(), refresh_ms=1234)
    intervals = [c for c in layout.children if isinstance(c, dcc.Interval)]
    assert len(intervals) == 1
    assert intervals[0].interval == 1234


# build_app registers the /live page
def test_build_app_registers_live_page():
    app = build_app(_TwoRunSource())
    assert isinstance(app, Dash)
    paths = {p["path"] for p in dash.page_registry.values()}
    assert "/live" in paths
