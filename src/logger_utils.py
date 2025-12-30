from __future__ import annotations

import logging
from pathlib import Path


def setup_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("smart_watcher")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if you re-run in same interpreter session
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(fmt)

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(sh)

    return logger
