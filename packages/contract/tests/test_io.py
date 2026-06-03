import json
from datetime import datetime, timezone

import polars as pl

from ygperf.io import read_report, write_report
from ygperf.report import SCHEMA_VERSION, PerfReport


def _report() -> PerfReport:
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="r1",
        run_ts=datetime(2026, 6, 3, tzinfo=timezone.utc),
        git_sha="sha1",
        git_dirty=False,
        eval_name="meta_allocation_portfolio",
        universe="u",
        cost_bps=5.0,
        freq="1M",
        params={"k": 3},
        metrics={"sharpe": 0.85},
        series=pl.DataFrame(
            {
                "timestamp": [datetime(2026, 1, 1), datetime(2026, 2, 1)],
                "equity": [1.0, 1.1],
                "returns": [0.0, 0.1],
            }
        ),
        trades=None,
        positions=None,
        extras={"sweep_by_k": [0.7, 0.8]},
    )


def test_write_then_read_round_trips(tmp_path):
    json_path = write_report(_report(), tmp_path)
    assert json_path.name == "r1.json"
    assert (tmp_path / "r1.series.parquet").exists()
    # JSON holds scalars + the sidecar pointer, NOT the series rows
    raw = json.loads(json_path.read_text())
    assert raw["metrics"]["sharpe"] == 0.85
    assert raw["sidecars"]["series"] == "r1.series.parquet"
    assert "equity" not in raw

    got = read_report(json_path)
    assert got.schema_version == SCHEMA_VERSION
    assert got.metrics["sharpe"] == 0.85
    assert got.extras["sweep_by_k"] == [0.7, 0.8]
    assert got.series.shape == (2, 3)
    assert got.trades is None


def test_read_is_lazy_when_load_series_false(tmp_path):
    json_path = write_report(_report(), tmp_path)
    got = read_report(json_path, load_frames=False)
    assert got.series is None  # not loaded
    assert got.metrics["sharpe"] == 0.85  # scalars always present
