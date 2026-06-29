import os
import sys
from pathlib import Path


def claude_home() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", Path.home()))
    else:
        base = Path.home()
    return base / ".claude"


def skill_dir() -> Path:
    return claude_home() / "skills" / "embedded-guru"


def data_dir() -> Path:
    return claude_home() / "embedded_guru"


def claude_md() -> Path:
    return claude_home() / "CLAUDE.md"


def skill_assets() -> Path:
    return Path(__file__).parent / "data"
