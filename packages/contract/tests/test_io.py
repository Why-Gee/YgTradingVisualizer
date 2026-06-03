import json
from datetime import UTC, datetime

import polars as pl
import pytest
from ygperf.io import read_report, write_report
from ygperf.report import SCHEMA_VERSION, PerfReport


def _report() -> PerfReport:
    return PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="r1",
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
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


def test_read_skips_frames_when_load_frames_false(tmp_path):
    json_path = write_report(_report(), tmp_path)
    got = read_report(json_path, load_frames=False)
    assert got.series is None  # not loaded
    assert got.metrics["sharpe"] == 0.85  # scalars always present


def test_trades_and_positions_round_trip(tmp_path):
    from datetime import UTC, datetime

    trades_df = pl.DataFrame(
        {
            "ts": [datetime(2026, 1, 2, tzinfo=UTC), datetime(2026, 1, 3, tzinfo=UTC)],
            "symbol": ["AAPL", "MSFT"],
            "qty": [10, -5],
            "price": [150.0, 310.0],
        }
    )
    positions_df = pl.DataFrame(
        {
            "ts": [datetime(2026, 1, 31, tzinfo=UTC)],
            "symbol": ["AAPL"],
            "weight": [0.6],
        }
    )
    report = PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="r2",
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
        git_sha="sha2",
        git_dirty=False,
        eval_name="meta_allocation_portfolio",
        universe="u2",
        cost_bps=3.0,
        freq="1D",
        params={},
        metrics={"sharpe": 1.2},
        series=pl.DataFrame(
            {
                "timestamp": [datetime(2026, 1, 1, tzinfo=UTC)],
                "equity": [1.0],
                "returns": [0.0],
            }
        ),
        trades=trades_df,
        positions=positions_df,
        extras={},
    )

    json_path = write_report(report, tmp_path)

    # All three sidecar files must exist
    assert (tmp_path / "r2.series.parquet").exists()
    assert (tmp_path / "r2.trades.parquet").exists()
    assert (tmp_path / "r2.positions.parquet").exists()

    # JSON sidecars dict has all three keys; frame rows not inlined
    raw = json.loads(json_path.read_text())
    assert set(raw["sidecars"].keys()) == {"series", "trades", "positions"}
    assert "symbol" not in raw
    assert "qty" not in raw

    # Full round-trip with load_frames=True
    got = read_report(json_path)
    assert got.trades is not None
    assert got.positions is not None
    assert got.trades.shape == trades_df.shape
    assert got.positions.shape == positions_df.shape
    assert got.trades.equals(trades_df)
    assert got.positions.equals(positions_df)

    # load_frames=False leaves all three None
    got_no_frames = read_report(json_path, load_frames=False)
    assert got_no_frames.series is None
    assert got_no_frames.trades is None
    assert got_no_frames.positions is None


def test_write_report_raises_for_unsafe_run_id(tmp_path):
    bad = PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id="../evil",
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
        git_sha="sha1",
        git_dirty=False,
        eval_name="meta_allocation_portfolio",
        universe="u",
        cost_bps=5.0,
        freq="1M",
        params={},
        metrics={},
        series=None,
        trades=None,
        positions=None,
        extras={},
    )
    with pytest.raises(ValueError, match="run_id must be filesystem-safe"):
        write_report(bad, tmp_path)
