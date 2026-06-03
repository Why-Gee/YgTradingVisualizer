from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import polars as pl

from ygperf.report import PerfReport

_FRAME_FIELDS = ("series", "trades", "positions")


def write_report(report: PerfReport, dest_dir: str | Path) -> Path:
    """Write <run_id>.json (scalars+metadata+extras+sidecar pointers) + parquet sidecars."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    sidecars: dict[str, str] = {}
    for fname in _FRAME_FIELDS:
        frame: pl.DataFrame | None = getattr(report, fname)
        if frame is not None:
            rel = f"{report.run_id}.{fname}.parquet"
            frame.write_parquet(dest / rel)
            sidecars[fname] = rel
    doc = {
        "schema_version": report.schema_version,
        "run_id": report.run_id,
        "run_ts": report.run_ts.isoformat(),
        "git_sha": report.git_sha,
        "git_dirty": report.git_dirty,
        "eval_name": report.eval_name,
        "universe": report.universe,
        "cost_bps": report.cost_bps,
        "freq": report.freq,
        "params": report.params,
        "metrics": report.metrics,
        "extras": report.extras,
        "sidecars": sidecars,
    }
    json_path = dest / f"{report.run_id}.json"
    json_path.write_text(json.dumps(doc, indent=2, sort_keys=True), encoding="utf-8")
    return json_path


def read_report(json_path: str | Path, *, load_frames: bool = True) -> PerfReport:
    """Inverse of write_report. Sidecar URIs resolve relative to json_path's dir, or absolute (hf://)."""
    json_path = Path(json_path)
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    frames: dict[str, pl.DataFrame | None] = {f: None for f in _FRAME_FIELDS}
    if load_frames:
        for fname, ref in doc.get("sidecars", {}).items():
            uri = ref if "://" in ref or Path(ref).is_absolute() else str(json_path.parent / ref)
            frames[fname] = pl.read_parquet(uri)
    return PerfReport(
        schema_version=doc["schema_version"],
        run_id=doc["run_id"],
        run_ts=datetime.fromisoformat(doc["run_ts"]),
        git_sha=doc["git_sha"],
        git_dirty=doc["git_dirty"],
        eval_name=doc["eval_name"],
        universe=doc["universe"],
        cost_bps=doc["cost_bps"],
        freq=doc["freq"],
        params=doc.get("params", {}),
        metrics=doc.get("metrics", {}),
        series=frames["series"],
        trades=frames["trades"],
        positions=frames["positions"],
        extras=doc.get("extras", {}),
    )
