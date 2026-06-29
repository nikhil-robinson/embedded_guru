"""
User preferences for EmbeddedGuru — stored in ~/.claude/embedded_guru/prefs.json.
"""
from __future__ import annotations

import json
from pathlib import Path

from .paths import data_dir


def _path() -> Path:
    return data_dir() / "prefs.json"


def load() -> dict:
    p = _path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save(prefs: dict) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(prefs, indent=2), encoding="utf-8")


def get_auto_mode() -> bool:
    return bool(load().get("auto_mode", False))


def set_auto_mode(enabled: bool) -> None:
    prefs = load()
    prefs["auto_mode"] = enabled
    save(prefs)
