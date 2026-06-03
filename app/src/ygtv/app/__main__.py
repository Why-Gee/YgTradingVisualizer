from __future__ import annotations

import os

from ygtv.app.factory import build_app
from ygtv.sources import DirectorySource


def _source_from_env() -> DirectorySource:
    source_dir = os.environ.get("YGTV_SOURCE_DIR")
    if not source_dir:
        raise SystemExit("YGTV_SOURCE_DIR must point to a directory of ygperf reports")
    return DirectorySource(source_dir)


def main() -> None:
    app = build_app(_source_from_env())
    app.run(
        host=os.environ.get("YGTV_HOST", "127.0.0.1"),
        port=int(os.environ.get("YGTV_PORT", "8050")),
        debug=os.environ.get("YGTV_DEBUG", "").lower() in {"1", "true", "yes"},
    )


if __name__ == "__main__":
    main()
