"""
embeddedguru add <file> — ingest a document into the curriculum knowledge base.

Copies the file to ~/.claude/embedded_guru/curriculum/custom/ and marks
the graph as needing a rebuild. The skill picks this up on the next /guru
session and runs graphify automatically.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .paths import data_dir
from . import console as c

SUPPORTED_EXTENSIONS = {
    ".md", ".txt", ".pdf", ".rst", ".html", ".htm",
    ".csv", ".json", ".yaml", ".yml", ".dbc",
}

REBUILD_MARKER = ".needs_graph_rebuild"


def add_document(path: str) -> int:
    src = Path(path).expanduser().resolve()

    if not src.exists():
        c.err(f"File not found: {src}")
        return 1

    if not src.is_file():
        c.err(f"Not a file: {src}")
        return 1

    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        c.warn(
            f"Unsupported extension '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
        c.warn("Adding anyway — graphify may skip unsupported formats.")

    custom_dir = data_dir() / "curriculum" / "custom"
    try:
        custom_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        c.err(f"Cannot create custom directory {custom_dir}: {e}")
        c.err("Run 'embeddedguru install' first.")
        return 1

    dst = custom_dir / src.name
    if dst.exists():
        c.warn(f"{src.name} already exists in curriculum — overwriting.")

    try:
        shutil.copy2(src, dst)
    except OSError as e:
        c.err(f"Could not copy file: {e}")
        return 1

    # Place a marker so the skill knows to rebuild on next /guru call
    marker = data_dir() / "curriculum" / REBUILD_MARKER
    try:
        marker.write_text(f"rebuild requested after adding: {src.name}\n", encoding="utf-8")
    except OSError:
        pass  # non-fatal — skill will still find the new file

    c.ok(f"Added:  {dst}")
    print()
    print(f"  Document added to the curriculum knowledge base.")
    print(f"  The knowledge graph will be rebuilt on your next /guru session.")
    print(f"  The mentor will then be able to answer questions about: {src.name}")
    print()
    return 0
