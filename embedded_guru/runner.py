"""
embeddedguru run — launch a Claude Code session with the user's preferred settings.
"""
from __future__ import annotations

import os
import shutil

from . import console as c
from .prefs import get_auto_mode


def run_session() -> int:
    claude = shutil.which("claude")
    if not claude:
        c.err("'claude' command not found.")
        c.err("Install Claude Code at: https://claude.ai/code")
        return 1

    auto = get_auto_mode()
    cmd  = [claude]

    if auto:
        cmd.append("--dangerously-skip-permissions")
        c.ok("Auto-mode ON — all permission prompts will be skipped")
    else:
        c.ok("Auto-mode OFF — Claude Code will ask before each tool call")

    cmd.append("/guru")

    print()
    os.execvp(claude, cmd)
    return 0  # unreachable — execvp replaces the process
