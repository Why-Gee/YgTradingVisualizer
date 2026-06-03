from __future__ import annotations

import subprocess
from pathlib import Path


def capture_git(repo_dir: str | Path) -> tuple[str, bool]:
    """Return (HEAD sha, dirty?). ('unknown', False) if not a git repo."""
    repo_dir = str(repo_dir)
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()
        return sha, bool(status)
    except (subprocess.CalledProcessError, FileNotFoundError, NotADirectoryError):
        return "unknown", False
