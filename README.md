# Smart Watcher

Watches a folder in real-time and:

- Organizes files into folders based on rules.json
- Quarantines risky extensions into a Quarantine folder

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
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
