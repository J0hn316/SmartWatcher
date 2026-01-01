from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path


def next_available_path(dest: Path) -> Path:
    """
    If dest already exists, create dest like:
    file.ext -> file (1).ext -> file (2).ext ...
    """

    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent

    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def move_file(src: Path, dest_dir: Path, dry_run: bool, logger: logging.Logger) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)

    desired = dest_dir / src.name
    dest = next_available_path(desired)

    if dry_run:
        if dest == desired:
            logger.info("[DRY RUN] Move %s → %s/", src.name, dest_dir.name)
        else:
            logger.info(
                "[DRY RUN] Move %s → %s/ as %s", src.name, dest_dir.name, dest.name
            )
        return

    try:
        shutil.move(str(src), str(dest))
        logger.info("Move %s → %s/", src.name, dest_dir.name)
    except Exception as exc:
        logger.error("Failed move %s → %s (%s)", src, dest, exc)


def settle_wait(seconds: float) -> None:
    """
    Small delay to avoid moving files while they are still being written.
    (This will be improved later with a 'stable size' check.)
    """

    if seconds > 0:
        time.sleep(seconds)
