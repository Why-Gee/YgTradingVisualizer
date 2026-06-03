import dataclasses
from datetime import UTC, datetime

import polars as pl
import pytest
from ygperf.report import SCHEMA_VERSION, PerfReport


def _minimal() -> PerfReport:
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="abc123",
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
        git_sha="deadbeef",
        git_dirty=False,
        eval_name="meta_allocation_portfolio",
        universe="sp500_members_asof",
        cost_bps=5.0,
        freq="1M",
        params={"k": 3},
        metrics={"sharpe": 0.85, "maxdd": 0.234},
        series=pl.DataFrame(
            {"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}
        ),
        trades=None,
        positions=None,
        extras={"sweep_by_k": [0.7, 0.8]},
    )


def test_perfreport_is_frozen_and_carries_fields():
    r = _minimal()
    assert r.schema_version == SCHEMA_VERSION
    assert r.metrics["sharpe"] == 0.85
    assert r.series.columns == ["timestamp", "equity", "returns"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.eval_name = "x"
