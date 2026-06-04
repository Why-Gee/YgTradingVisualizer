from __future__ import annotations

import os

from ygtv.app.factory import build_app
from ygtv.app.pages.live import DEFAULT_REFRESH_MS
from ygtv.sources import DirectorySource


def _source_from_env() -> DirectorySource:
    source_dir = os.environ.get("YGTV_SOURCE_DIR")
    if not source_dir:
        raise SystemExit("YGTV_SOURCE_DIR must point to a directory of ygperf reports")
    return DirectorySource(source_dir)


def _live_refresh_ms_from_env() -> int:
    raw = os.environ.get("YGTV_LIVE_REFRESH_MS")
    if not raw:
        return DEFAULT_REFRESH_MS
    try:
        ms = int(raw)
    except ValueError as e:
        raise SystemExit(f"YGTV_LIVE_REFRESH_MS must be an integer, got {raw!r}") from e
    if ms <= 0:
        raise SystemExit("YGTV_LIVE_REFRESH_MS must be a positive integer")
    return ms


def main() -> None:
    app = build_app(_source_from_env(), live_refresh_ms=_live_refresh_ms_from_env())
    app.run(
        host=os.environ.get("YGTV_HOST", "127.0.0.1"),
        port=int(os.environ.get("YGTV_PORT", "8050")),
        debug=os.environ.get("YGTV_DEBUG", "").lower() in {"1", "true", "yes"},
    )


if __name__ == "__main__":
    main()
