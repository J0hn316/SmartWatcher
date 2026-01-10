# Smart Watcher

A real-time Python CLI tool that watches a folder and automatically:

- organizes files based on rules
- quarantines risky file types
- logs every action for safety and auditing

Designed with reliability, safety, and maintainability in mind.

## Features

- Real-time folder watching (event-driven)
- Rule-based file organization (`rules.json`)
- Quarantine for risky extensions (e.g. `.exe`, `.ps1`)
- Dry-run mode by default (safe testing)
- `--apply` flag to perform real moves
- Stable file-size detection (prevents moving partial downloads)
- Conflict-safe renaming
- Recursive watching with destination-folder skipping
- Structured logging
- Graceful shutdown (`Ctrl+C`)

---

### Create and activate a virtual environment

**Windows (Git Bash / Bash in VS Code)**

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install watchdog

```

### Install dependencies

```bash
python -m pip install watchdog
```

## Usage

Run (dry-run)

```bash
python src/watcher.py --folder "C:/Users/YourName/Downloads"

```

Run (apply moves)

```bash
python src/watcher.py --folder "C:/Users/YourName/Downloads" --apply

```

Run (Override quarantine list quickly)

```bash
python src/watcher.py --folder "C:/Users/YourName/Downloads" --apply --quarantine ".exe,.msi,.bat,.ps1"
```
