from datetime import UTC, datetime

import polars as pl
import pytest
from ygperf.io import write_report
from ygperf.report import SCHEMA_VERSION, PerfReport
from ygtv.sources.base import Source
from ygtv.sources.directory import DirectorySource


def _write(tmp_path, run_id, sha, sharpe, metrics=None):
    r = PerfReport(
        schema_version=SCHEMA_VERSION,
        run_id=run_id,
        run_ts=datetime(2026, 6, 3, tzinfo=UTC),
        git_sha=sha,
        git_dirty=False,
        eval_name="meta_allocation_portfolio",
        universe="u",
        cost_bps=5.0,
        freq="1M",
        params={},
        metrics=metrics if metrics is not None else {"sharpe": sharpe, "maxdd": 0.2},
        series=pl.DataFrame(
            {"timestamp": [datetime(2026, 1, 1)], "equity": [1.0], "returns": [0.0]}
        ),
        trades=None,
        positions=None,
        extras={},
    )
    write_report(r, tmp_path)


def test_directory_source_indexes_runs_and_loads_reports(tmp_path):
    _write(tmp_path, "r1", "sha_old", 0.70)
    _write(tmp_path, "r2", "sha_new", 0.85)
    src = DirectorySource(tmp_path)

    assert isinstance(src, Source)  # protocol check

    runs = src.runs()  # tidy frame for overview/regression
    assert set(runs["run_id"]) == {"r1", "r2"}
    assert "sharpe" in runs.columns
    assert "git_sha" in runs.columns
    assert runs.filter(pl.col("run_id") == "r2")["sharpe"].item() == 0.85

    rep = src.report("r1")  # full report w/ series
    assert rep.git_sha == "sha_old"
    assert rep.series.height == 1


def test_runs_frame_is_empty_for_empty_dir(tmp_path):
    frame = DirectorySource(tmp_path).runs()
    assert frame.is_empty()
    assert "run_id" in frame.columns


def test_runs_raises_on_reserved_metric_name(tmp_path):
    _write(tmp_path, "bad", "sha", 0.0, metrics={"git_sha": 0.99})
    with pytest.raises(ValueError, match="git_sha"):
        DirectorySource(tmp_path).runs()
