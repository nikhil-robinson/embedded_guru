import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path
from typing import List, Optional

from . import __version__
from .paths import claude_home, skill_dir, data_dir, claude_md, skill_assets
from . import console as c

CLAUDE_MD_BLOCK = """\
# embedded-guru
- **embedded-guru** (`~/.claude/skills/embedded-guru/SKILL.md`) - firmware development mentor. Trigger: `/guru` or `/embedded-guru`
When the user types `/guru` or `/embedded-guru`, invoke the Skill tool with `skill: "embedded-guru"` before doing anything else."""


# ─── public API ────────────────────────────────────────────────────────────────

def install(dry_run: bool = False, skip_graphify: bool = False) -> int:
    c.header(f"EmbeddedGuru — installer v{__version__}")
    c.info(f"Platform: {_platform_label()}")

    warnings: List[str] = []   # non-fatal issues collected during install
    graphify_ok = False

    # Hard requirements — fail fast if missing
    _check_claude_installed()
    _check_assets()

    reinstall = skill_dir().exists()
    if reinstall:
        existing = _read_version()
        c.warn(f"EmbeddedGuru {existing} already installed — upgrading to {__version__}")

    # Graphify — soft dependency, skill works without it in degraded mode
    if skip_graphify:
        c.warn("--skip-graphify: skipping Graphify install and graph build")
        warnings.append("Graphify skipped — /guru will use markdown fallback (no graph queries)")
    else:
        graphify_ok = _check_or_install_graphify(dry_run, warnings)

    # Core install steps — each wrapped, failure is collected not fatal
    _install_skill_files(dry_run, warnings)
    _ensure_data_dir(dry_run, warnings)

    if graphify_ok or dry_run:
        _install_curriculum(dry_run, warnings)
    else:
        warnings.append("Curriculum graph not built — Graphify unavailable")

    _register(dry_run, warnings)

    # Summary
    _print_summary(dry_run, reinstall, graphify_ok, warnings)
    return 0


def uninstall(keep_data: bool = False, delete_all: bool = False) -> int:
    c.header("EmbeddedGuru — uninstaller")

    remove_data = False
    if data_dir().exists() and not keep_data:
        if delete_all:
            remove_data = True
        else:
            c.warn(f"Student data found at {data_dir()}")
            print()
            print(f"  {c.bold('Remove student profiles too?')}")
            print(f"  This deletes all progress, assignments, and roadmaps.")
            print(f"  {c.red('Cannot be undone.')}")
            print()
            try:
                answer = input("  Delete student data? [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                answer = "n"
            print()
            remove_data = answer == "y"

    _remove_skill_files()
    _deregister()

    if data_dir().exists():
        if remove_data:
            c.header("Removing student data")
            c.info(f"Removing {data_dir()}")
            try:
                shutil.rmtree(data_dir())
                c.ok("Student data removed")
            except OSError as e:
                c.err(f"Could not remove student data: {e}")
                c.err(f"Remove manually: {data_dir()}")
        else:
            c.ok(f"Student data kept at {data_dir()}")

    print()
    print(f"  {c.bold('EmbeddedGuru uninstalled.')}")
    print()
    return 0


# ─── graphify detection and install ────────────────────────────────────────────

def _find_graphify() -> Optional[str]:
    """Find the graphify binary. Checks PATH first, then Python Scripts dir."""
    # 1. Already on PATH (most common case)
    found = shutil.which("graphify")
    if found:
        return found

    # 2. Installed by pip but Scripts dir not on PATH yet (common on Windows and Mac)
    scripts_dir = Path(sysconfig.get_path("scripts"))
    candidates = ["graphify", "graphify.exe", "graphify.cmd"]
    for name in candidates:
        candidate = scripts_dir / name
        if candidate.exists():
            return str(candidate)

    # 3. pipx / uv tool installs to ~/.local/bin (Linux/Mac) or %LOCALAPPDATA%\uv\bin (Windows)
    local_bin_dirs = [
        Path.home() / ".local" / "bin",
    ]
    if sys.platform == "win32":
        local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
        if local_appdata:
            local_bin_dirs.append(local_appdata / "uv" / "bin")
    for d in local_bin_dirs:
        for name in candidates:
            candidate = d / name
            if candidate.exists():
                return str(candidate)

    return None


def _graphify_importable() -> bool:
    """Check if the graphify Python module is installed, regardless of CLI PATH."""
    result = subprocess.run(
        [sys.executable, "-c", "import graphify"],
        capture_output=True,
    )
    return result.returncode == 0


def _check_or_install_graphify(dry_run: bool, warnings: List[str]) -> bool:
    """Returns True if graphify is available (or dry_run). Appends to warnings on soft failure."""
    c.header("Checking Graphify")

    found = _find_graphify()
    if found:
        c.ok(f"graphify found at {found}")
        return True

    if _graphify_importable():
        # Module is installed but CLI not on PATH — can run via python -m graphify
        c.ok("graphify module found (will run via python -m graphify)")
        return True

    c.warn("graphify not found — attempting install")

    if dry_run:
        c.info("[DRY RUN] would install graphifyy")
        return True

    # Try install methods in order of preference
    installed = (
        _try_install_uv()
        or _try_install_pip()
        or _try_install_pip_user()
    )

    if not installed:
        msg = (
            "Could not install graphifyy automatically. "
            "Install manually: uv tool install graphifyy  OR  pip install graphifyy"
        )
        c.warn(msg)
        warnings.append(f"Graphify not installed — {msg}")
        warnings.append("/guru will run in degraded mode (markdown fallback, no graph queries)")
        return False

    # Verify install succeeded — check module import since PATH may not be updated yet
    if not _graphify_importable():
        c.warn("graphify installed but module not importable — check your Python environment")
        warnings.append("graphify installed but import failed — graph build skipped")
        return False

    c.ok("graphify installed successfully")
    return True


def _try_install_uv() -> bool:
    uv = shutil.which("uv")
    if not uv:
        return False
    c.info("Trying: uv tool install graphifyy")
    result = subprocess.run(
        [uv, "tool", "install", "graphifyy", "-q"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        c.ok("graphify installed via uv tool")
        return True
    return False


def _try_install_pip() -> bool:
    c.info("Trying: pip install graphifyy")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "graphifyy", "-q"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def _try_install_pip_user() -> bool:
    c.info("Trying: pip install --user graphifyy")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "graphifyy", "-q"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        c.ok("graphify installed via pip --user")
        return True
    return False


# ─── graphify runner ───────────────────────────────────────────────────────────

def _detect_backend() -> Optional[str]:
    """Return the graphify --backend value based on available API keys in env."""
    key_map = [
        ("ANTHROPIC_API_KEY",  "claude"),
        ("OPENAI_API_KEY",     "openai"),
        ("GEMINI_API_KEY",     "gemini"),
        ("GOOGLE_API_KEY",     "gemini"),
        ("DEEPSEEK_API_KEY",   "deepseek"),
        ("MOONSHOT_API_KEY",   "kimi"),
    ]
    for env_var, backend in key_map:
        if os.environ.get(env_var):
            return backend
    return None


def _run_graphify(path: Path, update: bool = False, dry_run: bool = False) -> bool:
    """Run graphify on path. Returns True on success."""
    # Prefer CLI binary; fall back to python -m graphify
    graphify_bin = _find_graphify()

    if graphify_bin:
        cmd = [graphify_bin, str(path), "--no-viz"]
    elif _graphify_importable():
        cmd = [sys.executable, "-m", "graphify", str(path), "--no-viz"]
    else:
        c.warn("graphify not available — skipping graph build")
        return False

    backend = _detect_backend()
    if backend:
        cmd += ["--backend", backend]
    else:
        c.warn("No LLM API key found in environment — set ANTHROPIC_API_KEY and re-run install")
        return False

    if update:
        cmd.append("--update")

    if dry_run:
        c.info(f"[DRY RUN] would run: {' '.join(str(x) for x in cmd)}")
        return True

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        c.warn("graphify build timed out after 5 minutes — skipping")
        return False
    except OSError as e:
        c.warn(f"graphify could not start: {e}")
        return False

    if result.returncode != 0:
        c.warn(f"graphify exited with code {result.returncode}")
        if result.stderr:
            # Show first 300 chars of stderr, not the full wall of text
            c.warn(result.stderr[:300].strip())
        return False

    c.ok("graphify build complete")
    return True


# ─── curriculum install ────────────────────────────────────────────────────────

def _curriculum_dir() -> Path:
    return data_dir() / "curriculum"


def _install_curriculum(dry_run: bool, warnings: List[str]):
    c.header("Installing curriculum knowledge base")
    src = skill_assets() / "curriculum"
    dst = _curriculum_dir()

    if not src.is_dir():
        msg = "No curriculum/ directory in package assets — skipping graph build"
        c.warn(msg)
        warnings.append(msg)
        return

    if dry_run:
        c.info(f"[DRY RUN] would copy curriculum/ to {dst}")
        c.info(f"[DRY RUN] would run: graphify {dst} --no-viz")
        return

    # Atomic copy: write to temp dir first, rename on success
    # This prevents a broken state if the copy fails midway
    parent = dst.parent
    try:
        with tempfile.TemporaryDirectory(dir=parent, prefix=".curriculum_tmp_") as tmp:
            tmp_dst = Path(tmp) / "curriculum"
            shutil.copytree(src, tmp_dst)

            # Copy succeeded — atomically swap in
            if dst.exists():
                old_backup = parent / ".curriculum_old"
                if old_backup.exists():
                    shutil.rmtree(old_backup)
                dst.rename(old_backup)
                try:
                    shutil.copytree(tmp_dst, dst)
                    shutil.rmtree(old_backup)
                except Exception:
                    # Restore backup on failure
                    if old_backup.exists() and not dst.exists():
                        old_backup.rename(dst)
                    raise
            else:
                shutil.copytree(tmp_dst, dst)

    except (OSError, shutil.Error) as e:
        msg = f"Could not copy curriculum files: {e}"
        c.warn(msg)
        warnings.append(msg)
        warnings.append("Curriculum graph not built — /guru will use SKILL.md fallback")
        return

    c.ok(f"Curriculum files copied to {dst}")

    # Build or update the graph
    graph_json = dst / "graphify-out" / "graph.json"
    if graph_json.exists():
        c.info("Curriculum graph exists — running incremental update")
        ok = _run_graphify(dst, update=True)
    else:
        c.info("Building curriculum knowledge graph (~30s)...")
        ok = _run_graphify(dst, update=False)

    if ok and graph_json.exists():
        c.ok(f"Curriculum graph ready")
    else:
        msg = "Curriculum graph build failed — /guru will fall back to SKILL.md context"
        c.warn(msg)
        warnings.append(msg)


# ─── core install helpers ──────────────────────────────────────────────────────

def _check_claude_installed():
    if not claude_home().exists():
        c.err(f"{claude_home()} not found. Is Claude Code installed?")
        c.err("Get Claude Code at: https://claude.ai/code")
        raise SystemExit(1)


def _check_assets():
    if not (skill_assets() / "SKILL.md").exists():
        c.err("Skill assets missing from package.")
        c.err("Reinstall: pipx install --force git+https://github.com/nikhil-robinson/embedded_guru.git")
        raise SystemExit(1)


def _read_version() -> str:
    v = skill_dir() / ".version"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "unknown"


def _install_skill_files(dry_run: bool, warnings: List[str]):
    c.header("Installing skill files")
    assets = skill_assets()

    try:
        if not dry_run:
            skill_dir().mkdir(parents=True, exist_ok=True)

        c.info("Copying SKILL.md")
        if not dry_run:
            shutil.copy2(assets / "SKILL.md", skill_dir() / "SKILL.md")

        for sub in ("references", "templates"):
            src = assets / sub
            dst = skill_dir() / sub
            if src.is_dir():
                c.info(f"Copying {sub}/")
                if not dry_run:
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)

        if not dry_run:
            (skill_dir() / ".version").write_text(__version__, encoding="utf-8")
        c.ok(f"Skill files installed to {skill_dir()}")

    except (OSError, shutil.Error) as e:
        c.err(f"Failed to install skill files: {e}")
        raise SystemExit(1)   # hard failure — skill is unusable without these


def _ensure_data_dir(dry_run: bool, warnings: List[str]):
    c.header("Setting up student data directory")
    try:
        if not dry_run:
            data_dir().mkdir(parents=True, exist_ok=True)
        c.ok(f"Student data directory ready at {data_dir()}")
    except OSError as e:
        msg = f"Could not create data directory {data_dir()}: {e}"
        c.warn(msg)
        warnings.append(msg)


def _register(dry_run: bool, warnings: List[str]):
    c.header("Registering skill")
    md = claude_md()

    try:
        if not dry_run and not md.exists():
            md.write_text("", encoding="utf-8")

        text = md.read_text(encoding="utf-8") if md.exists() else ""

        if "# embedded-guru" in text:
            c.info("Updating existing registration in CLAUDE.md")
            text = re.sub(r"# embedded-guru\n.*\n.*\n?", "", text, flags=re.MULTILINE)
        else:
            c.info("Adding registration to CLAUDE.md")

        text = text.rstrip("\n") + "\n\n" + CLAUDE_MD_BLOCK + "\n"

        if not dry_run:
            # Write atomically: temp file → rename (avoids corruption if killed mid-write)
            tmp = md.with_suffix(".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(md)

        c.ok(f"Registered /guru trigger in {md}")

    except OSError as e:
        msg = f"Could not register skill in CLAUDE.md: {e}"
        c.err(msg)
        warnings.append(msg)
        warnings.append(f"Add manually to {md}:\n{CLAUDE_MD_BLOCK}")


def _remove_skill_files():
    c.header("Removing skill files")
    if skill_dir().exists():
        try:
            shutil.rmtree(skill_dir())
            c.ok("Skill files removed")
        except OSError as e:
            c.warn(f"Could not fully remove {skill_dir()}: {e}")
            c.warn(f"Remove manually: {skill_dir()}")
    else:
        c.warn("Skill directory not found — already uninstalled?")


def _deregister():
    c.header("Cleaning up CLAUDE.md")
    md = claude_md()
    if not md.exists():
        c.warn("CLAUDE.md not found — nothing to clean up")
        return

    try:
        text = md.read_text(encoding="utf-8")
        if "# embedded-guru" not in text:
            c.warn("No embedded-guru registration found in CLAUDE.md")
            return

        c.info("Removing registration from CLAUDE.md")
        text = re.sub(r"\n# embedded-guru\n.*\n.*", "", text, flags=re.MULTILINE)

        tmp = md.with_suffix(".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(md)
        c.ok("Registration removed")

    except OSError as e:
        c.warn(f"Could not update CLAUDE.md: {e}")
        c.warn(f"Remove the # embedded-guru block from {md} manually")


# ─── summary ───────────────────────────────────────────────────────────────────

def _print_summary(dry_run: bool, reinstall: bool, graphify_ok: bool, warnings: List[str]):
    print()
    prefix = f"{c.bold('[DRY RUN]')} " if dry_run else ""

    if warnings:
        print(f"  {prefix}{c.bold(f'EmbeddedGuru {__version__} installed with warnings.')}")
    else:
        print(f"  {prefix}{c.bold(f'EmbeddedGuru {__version__} installed successfully.')}")

    print()
    print(f"  Start a session:  {c.bold('/guru')}")
    print(f"  Debug mode:       {c.bold('/guru debug')}")
    print(f"  View roadmap:     {c.bold('/guru roadmap')}")
    print(f"  Student data:     {c.bold(str(data_dir()))}")

    graph_json = _curriculum_dir() / "graphify-out" / "graph.json"
    if graphify_ok and (graph_json.exists() or dry_run):
        print(f"  Curriculum graph: {c.bold(str(graph_json))}")
    else:
        print(f"  Curriculum graph: {c.yellow('not built — degraded mode')}")

    if reinstall:
        print()
        print(f"  {c.yellow('Upgrade note:')} student profiles in {data_dir()} were not touched.")

    if warnings:
        print()
        print(f"  {c.yellow('Warnings:')}")
        for w in warnings:
            print(f"    {c.yellow('⚠')} {w}")
        print()
        if not graphify_ok:
            print(f"  {c.bold('To enable graph queries later:')}")
            print(f"    export ANTHROPIC_API_KEY=sk-ant-...")
            print(f"    embeddedguru install")

    print()


def _platform_label() -> str:
    if sys.platform == "win32":
        import platform
        return f"Windows {platform.release()}"
    if sys.platform == "darwin":
        import platform
        return f"macOS {platform.mac_ver()[0]}"
    return f"Linux ({sys.platform})"
