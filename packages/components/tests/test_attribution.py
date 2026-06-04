from __future__ import annotations

import plotly.graph_objects as go
from ygtv.components.attribution import factor_attribution_bars


def test_attribution_bars_returns_one_bar_trace():
    labels = ["momentum", "value", "size"]
    values = [0.3, -0.1, 0.05]
    fig = factor_attribution_bars(labels, values)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert isinstance(fig.data[0], go.Bar)


def test_attribution_bars_orientation_horizontal():
    labels = ["a", "b"]
    values = [0.1, -0.2]
    fig = factor_attribution_bars(labels, values)
    assert fig.data[0].orientation == "h"


def test_attribution_bars_x_matches_values():
    labels = ["momentum", "value", "size"]
    values = [0.3, -0.1, 0.05]
    fig = factor_attribution_bars(labels, values)
    assert list(fig.data[0].x) == values


def test_attribution_bars_y_matches_labels():
    labels = ["momentum", "value", "size"]
    values = [0.3, -0.1, 0.05]
    fig = factor_attribution_bars(labels, values)
    assert list(fig.data[0].y) == labels


def test_attribution_bars_marker_colors_by_sign():
    labels = ["a", "b", "c"]
    values = [0.1, -0.2, 0.0]
    fig = factor_attribution_bars(labels, values)
    colors = list(fig.data[0].marker.color)
    assert colors[0] == "green"
    assert colors[1] == "red"
    assert colors[2] == "green"  # 0 >= 0 → green


def test_attribution_bars_custom_title():
    labels = ["x"]
    values = [1.0]
    fig = factor_attribution_bars(labels, values, title="My Attribution")
    assert fig.layout.title.text == "My Attribution"


def test_attribution_bars_empty_labels_returns_empty():
    fig = factor_attribution_bars([], [])
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_attribution_bars_mismatched_lengths_returns_empty():
    fig = factor_attribution_bars(["a", "b"], [0.1])
    assert len(fig.data) == 0
    assert fig.layout.annotations


def test_attribution_bars_empty_values_returns_empty():
    fig = factor_attribution_bars(["a"], [])
    assert len(fig.data) == 0
    assert fig.layout.annotations
