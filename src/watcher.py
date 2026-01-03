from __future__ import annotations

import json
import argparse
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from rules import load_rules
from logger_utils import setup_logger
from organizer import move_file, settle_wait


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
RULES_PATH = PROJECT_ROOT / "rules.json"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_ext_list(cvs: str) -> list[str]:
    # ".exe,.msi,.bat" → [".exe", ".msi", ".bat"]
    parts = [p.strip().lower() for p in cvs.split(",") if p.strip()]
    return [p if p.startswith(".") else f".{p}" for p in parts]


def build_parser(config: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smart Watcher (organize + quarantine)"
    )
    specs = [
        dict(
            flags=["--folder"],
            kwargs=dict(
                type=Path,
                default=Path(config["default_folder"]),
                help="Folder to watch",
            ),
        ),
        dict(
            flags=["--rules"],
            kwargs=dict(
                type=Path,
                default=RULES_PATH,
                help="Rules JSON path",
            ),
        ),
        dict(
            flags=["--apply"],
            kwargs=dict(
                action="store_true",
                help="Apply changes (default: dry-run)",
            ),
        ),
        dict(
            flags=["--recursive"],
            kwargs=dict(
                action="store_true",
                default=bool(config.get("recursive", True)),
                help="Watch subfolders recursively",
            ),
        ),
        dict(
            flags=["--settle"],
            kwargs=dict(
                type=float,
                default=float(config.get("settle_seconds", 1.5)),
                help="Seconds to wait before handling a new file",
            ),
        ),
        dict(
            flags=["--quarantine"],
            kwargs=dict(
                type=str,
                default="",
                help="Override quarantine extensions CSV (.exe,.msi,...)",
            ),
        ),
    ]
    for spec in specs:
        parser.add_argument(*spec["flags"], **spec["kwargs"])

    return parser


class SmartHandler(FileSystemEventHandler):
    def __init__(
        self,
        base_dir: Path,
        rules: dict[str, list[str]],
        quarantine_dir: Path,
        quarantine_exts: set[str],
        dry_run: bool,
        recursive: bool,
        settle_seconds: float,
        logger,
    ) -> None:
        self.base_dir = base_dir
        self.rules = rules
        self.quarantine_dir = quarantine_dir
        self.quarantine_exts = quarantine_exts
        self.dry_run = dry_run
        self.recursive = recursive
        self.settle_seconds = settle_seconds
        self.logger = logger

        # To avoid processing files after we move them into these folders
        self.dest_folders = set(rules.keys()) | {quarantine_dir.name}

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        self._handle_path(Path(event.src_path))

    def on_moved(self, event) -> None:
        if event.is_directory:
            return
        self._handle_path(Path(event.dest_path))

    def _handle_path(self, path: Path) -> None:
        # Only manage files inside the target base dir
        try:
            path.relative_to(self.base_dir)
        except ValueError:
            return

        # If recursive, avoid reprocessing files already inside destination folders
        if self.recursive and any(
            parent.name in self.dest_folders for parent in path.parents
        ):
            return

        # Wait briefly so downloads finish writing.
        settle_wait(self.settle_seconds)

        if not path.exists() or not path.is_file():
            return

        ext = path.suffix.lower()

        # Quarantine first (wins over organize rules)
        if ext in self.quarantine_exts:
            move_file(
                path, self.quarantine_dir, dry_run=self.dry_run, logger=self.logger
            )
            return

        # Organize by rules
        for folder, exts in self.rules.items():
            if ext in exts:
                move_file(
                    path,
                    self.base_dir / folder,
                    dry_run=self.dry_run,
                    logger=self.logger,
                )
                return


def main() -> None:
    config = load_config()

    parser = build_parser(config)
    args = parser.parse_args()

    base_dir = Path = args.folder.resolve()
    rules = load_rules(args.rules)

    quarantine_dir = base_dir / str(config.get("quarantine_folder", "Quarantine"))

    quarantine_exts = set(str(e).lower() for e in config.get("quarantine_exts", []))

    if args.quarantine.strip():
        quarantine_exts = set(parse_ext_list(args.quarantine))

    logger = setup_logger(PROJECT_ROOT / "logs" / "smart_watcher.log")

    handler = SmartHandler(
        base_dir=base_dir,
        rules=rules,
        quarantine_dir=quarantine_dir,
        quarantine_exts=quarantine_exts,
        dry_run=not args.apply,
        recursive=bool(args.recursive),
        settle_seconds=float(args.settle),
        logger=logger,
    )

    observer = Observer()
    observer.schedule(handler, str(base_dir), recursive=bool(args.recursive))
    observer.start()

    logger.info(
        "Watching: %s | dry_run=%s | recursive=%s",
        base_dir,
        (not args.apply),
        bool(args.recursive),
    )

    try:
        observer.join()
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
