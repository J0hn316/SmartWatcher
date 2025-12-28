from __future__ import annotations

import json
from pathlib import Path


def load_rules(path: Path) -> dict[str, list[str]]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "rules.json must be an object mapping folder -> list of extensions"
        )

    rules: dict[str, list[str]] = {}

    for folder, exts in data.items():
        if not isinstance(folder, str) or not isinstance(exts, list):
            raise ValueError("rules.json must map folder names to lists of extensions")
        rules[folder] = [str(e).lower() for e in exts]

    return rules
