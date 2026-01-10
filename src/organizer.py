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


def wait_for_stable_file(
    path: Path,
    timeout: float = 15.0,
    interval: float = 0.5,
    stable_rounds: int = 2,
) -> bool:
    """
    Wait until the file size stops changing.

    - timeout: max seconds to wait total
    - interval: how often to check the file size
    - stable_rounds: how many consecutive checks must match

    Returns True if the file became stable, False if timed out.
    """

    start = time.time()
    last_size: int | None = None
    stable_count = 0

    while True:
        # File disappeared or not ready
        if not path.exists():
            return False

        try:
            size = path.stat().st_size
        except OSError:
            # Might be temporarily locked; try again until timeout
            size = None

        if size is not None and last_size is not None and size == last_size:
            stable_count += 1
        else:
            stable_count = 0

        last_size = size if size is not None else last_size

        if stable_count >= stable_rounds:
            return True

        if time.time() - start >= timeout:
            return False

        time.sleep(interval)
