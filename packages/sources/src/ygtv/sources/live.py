from __future__ import annotations

from ygperf.report import PerfReport
from ygtv.sources.directory import DirectorySource


class LiveSource(DirectorySource):
    """Phase-3 stub: polls a directory the producer appends to. Same contract as DirectorySource.

    A Dash `dcc.Interval` re-calls `runs()`/`latest()` on a timer. When the bot emits the contract,
    only this adapter's storage backend changes — the app and components are untouched.
    """

    def latest(self) -> PerfReport:
        runs = self.runs()
        if runs.is_empty():
            raise LookupError("no runs in live directory")
        run_id = runs.sort("run_ts", descending=True)["run_id"][0]
        return self.report(run_id)
