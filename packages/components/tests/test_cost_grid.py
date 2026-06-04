from __future__ import annotations

import plotly.graph_objects as go
from ygtv.components.cost_grid import cost_time_grid


def test_cost_time_grid_returns_one_heatmap_trace():
    x = ["1bps", "5bps", "10bps"]
    y = ["1d", "5d"]
    z = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    fig = cost_time_grid(x, y, z)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert isinstance(fig.data[0], go.Heatmap)


def test_cost_time_grid_z_matches_input():
    x = ["1bps", "5bps", "10bps"]
    y = ["1d", "5d"]
    z = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    fig = cost_time_grid(x, y, z)
    assert list(fig.data[0].z[0]) == [0.1, 0.2, 0.3]
    assert list(fig.data[0].z[1]) == [0.4, 0.5, 0.6]


def test_cost_time_grid_x_y_labels():
    x = ["1bps", "5bps", "10bps"]
    y = ["1d", "5d"]
    z = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    fig = cost_time_grid(x, y, z)
    assert list(fig.data[0].x) == x
    assert list(fig.data[0].y) == y


def test_cost_time_grid_colorscale():
    x = ["a"]
    y = ["b"]
    z = [[1.0]]
    fig = cost_time_grid(x, y, z)
    # Plotly expands the named colorscale to tuples; verify it's set (not None/empty)
    assert fig.data[0].colorscale is not None
    assert len(fig.data[0].colorscale) > 0


def test_cost_time_grid_custom_title():
    x = ["a"]
    y = ["b"]
    z = [[1.0]]
    fig = cost_time_grid(x, y, z, title="My Grid")
    assert fig.layout.title.text == "My Grid"


def test_cost_time_grid_empty_z_returns_empty():
    fig = cost_time_grid(["a"], ["b"], [])
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_cost_time_grid_empty_x_labels_returns_empty():
    fig = cost_time_grid([], ["b"], [[1.0]])
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_cost_time_grid_empty_y_labels_returns_empty():
    fig = cost_time_grid(["a"], [], [[1.0]])
    assert len(fig.data) == 0
    assert fig.layout.annotations
