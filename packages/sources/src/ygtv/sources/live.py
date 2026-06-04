from __future__ import annotations

from ygperf.report import PerfReport
from ygtv.sources.directory import DirectorySource
from ygtv.sources.runs import latest_run_id


class LiveSource(DirectorySource):
    """Phase-3 stub: polls a directory the producer appends to. Same contract as DirectorySource.

    A Dash `dcc.Interval` re-calls `runs()`/`latest()` on a timer. When the bot emits the contract,
    only this adapter's storage backend changes — the app and components are untouched.
    """

    def latest(self) -> PerfReport:
        run_id = latest_run_id(self.runs())
        if run_id is None:
            raise LookupError("no runs in live directory")
        return self.report(run_id)
