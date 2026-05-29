from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from shared.config import settings
from shared.logging_utils import write_json


def _prune_old_runs() -> None:
    if settings.max_saved_runs <= 0:
        return
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    run_dirs = sorted([p for p in settings.outputs_dir.iterdir() if p.is_dir()])
    excess = len(run_dirs) - settings.max_saved_runs
    if excess <= 0:
        return
    for old_dir in run_dirs[:excess]:
        for child in sorted(old_dir.rglob('*'), reverse=True):
            if child.is_file() or child.is_symlink():
                child.unlink(missing_ok=True)
            elif child.is_dir():
                child.rmdir()
        old_dir.rmdir()


def new_run_dir() -> tuple[str, Path]:
    _prune_old_runs()
    timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
    run_id = f'run_{timestamp}_{uuid4().hex[:8]}'
    run_dir = settings.outputs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def save_report(run_dir: Path, payload: Dict[str, Any]) -> Path:
    path = run_dir / 'report.json'
    write_json(path, payload)
    return path
