from datetime import UTC, datetime

import polars as pl
import pytest
from ygperf.io import write_report
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.sources.base import Source
from ygtv.sources.live import LiveSource


def _write(d, rid, ts):
    write_report(
        PerfReport(
            schema_version=SCHEMA_VERSION,
            run_id=rid,
            run_ts=ts,
            git_sha="live",
            git_dirty=True,
            eval_name="live_strategy",
            universe="u",
            cost_bps=0.0,
            freq="1d",
            params={},
            metrics={"sharpe": 1.0},
            series=pl.DataFrame({"timestamp": [ts], "equity": [1.0], "returns": [0.0]}),
            trades=None,
            positions=None,
            extras={},
        ),
        d,
    )


def test_livesource_satisfies_protocol_and_reads_latest(tmp_path):
    _write(tmp_path, "a", datetime(2026, 6, 3, 10, tzinfo=UTC))
    _write(tmp_path, "b", datetime(2026, 6, 3, 11, tzinfo=UTC))
    src = LiveSource(tmp_path)
    assert isinstance(src, Source)
    assert src.runs().height == 2
    assert src.latest().run_id == "b"  # newest by run_ts


def test_livesource_latest_raises_on_empty_dir(tmp_path):
    with pytest.raises(LookupError):
        LiveSource(tmp_path).latest()
