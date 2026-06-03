from __future__ import annotations

import hashlib
from datetime import UTC, datetime


def run_id_for(git_sha: str, eval_name: str, run_ts: datetime) -> str:
    """Deterministic 16-hex-char id from (git_sha, eval_name, run_ts)."""
    ts = run_ts.astimezone(UTC) if run_ts.tzinfo is not None else run_ts
    key = f"{git_sha}|{eval_name}|{ts.isoformat()}".encode()
    return hashlib.sha256(key).hexdigest()[:16]
