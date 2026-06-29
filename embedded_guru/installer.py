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

    warnings: List[str] = []
    graphify_ok = False

    _check_claude_installed()
    _check_assets()

    reinstall = skill_dir().exists()
    if reinstall:
        existing = _read_version()
        c.warn(f"EmbeddedGuru {existing} already installed — upgrading to {__version__}")

    if skip_graphify:
        c.warn("--skip-graphify: skipping Graphify check")
        warnings.append("Graphify skipped — /guru will prompt you to install it on first session")
    else:
        graphify_ok = _check_or_install_graphify(dry_run, warnings)

    _install_skill_files(dry_run, warnings)
    _ensure_data_dir(dry_run, warnings)
    _install_curriculum(dry_run, warnings)
    _register(dry_run, warnings)

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
    found = shutil.which("graphify")
    if found:
        return found

    scripts_dir = Path(sysconfig.get_path("scripts"))
    for name in ("graphify", "graphify.exe", "graphify.cmd"):
        candidate = scripts_dir / name
        if candidate.exists():
            return str(candidate)

    import os
    local_bin_dirs = [Path.home() / ".local" / "bin"]
    if sys.platform == "win32":
        local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
        if local_appdata:
            local_bin_dirs.append(local_appdata / "uv" / "bin")
    for d in local_bin_dirs:
        for name in ("graphify", "graphify.exe", "graphify.cmd"):
            candidate = d / name
            if candidate.exists():
                return str(candidate)

    return None


def _graphify_importable() -> bool:
    result = subprocess.run(
        [sys.executable, "-c", "import graphify"],
        capture_output=True,
    )
    return result.returncode == 0


def _check_or_install_graphify(dry_run: bool, warnings: List[str]) -> bool:
    c.header("Checking Graphify")

    found = _find_graphify()
    if found:
        c.ok(f"graphify found at {found}")
        return True

    if _graphify_importable():
        c.ok("graphify module found (will run via python -m graphify)")
        return True

    c.warn("graphify not found — attempting install")

    if dry_run:
        c.info("[DRY RUN] would install graphifyy")
        return True

    installed = (
        _try_install_uv()
        or _try_install_pip()
        or _try_install_pip_user()
    )

    if not installed:
        msg = "Could not install graphifyy — install manually: pipx install graphifyy"
        c.warn(msg)
        warnings.append(msg)
        return False

    if not _graphify_importable():
        c.warn("graphify installed but module not importable — check your Python environment")
        warnings.append("graphify installed but import check failed")
        return False

    c.ok("graphify installed successfully")
    return True


def _try_install_uv() -> bool:
    uv = shutil.which("uv")
    if not uv:
        return False
    c.info("Trying: uv tool install graphifyy")
    result = subprocess.run([uv, "tool", "install", "graphifyy", "-q"], capture_output=True)
    if result.returncode == 0:
        c.ok("graphify installed via uv tool")
        return True
    return False


def _try_install_pip() -> bool:
    c.info("Trying: pip install graphifyy")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "graphifyy", "-q"], capture_output=True
    )
    return result.returncode == 0


def _try_install_pip_user() -> bool:
    c.info("Trying: pip install --user graphifyy")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "graphifyy", "-q"], capture_output=True
    )
    if result.returncode == 0:
        c.ok("graphify installed via pip --user")
        return True
    return False


# ─── curriculum install (files only — graph built by the skill on first /guru) ─

def _curriculum_dir() -> Path:
    return data_dir() / "curriculum"


def _install_curriculum(dry_run: bool, warnings: List[str]):
    c.header("Installing curriculum files")
    src = skill_assets() / "curriculum"
    dst = _curriculum_dir()

    if not src.is_dir():
        msg = "No curriculum/ directory in package assets"
        c.warn(msg)
        warnings.append(msg)
        return

    if dry_run:
        c.info(f"[DRY RUN] would copy curriculum/ to {dst}")
        return

    parent = dst.parent
    try:
        with tempfile.TemporaryDirectory(dir=parent, prefix=".curriculum_tmp_") as tmp:
            tmp_dst = Path(tmp) / "curriculum"
            shutil.copytree(src, tmp_dst)

            if dst.exists():
                old_backup = parent / ".curriculum_old"
                if old_backup.exists():
                    shutil.rmtree(old_backup)
                dst.rename(old_backup)
                try:
                    shutil.copytree(tmp_dst, dst)
                    shutil.rmtree(old_backup)
                except Exception:
                    if old_backup.exists() and not dst.exists():
                        old_backup.rename(dst)
                    raise
            else:
                shutil.copytree(tmp_dst, dst)

    except (OSError, shutil.Error) as e:
        msg = f"Could not copy curriculum files: {e}"
        c.warn(msg)
        warnings.append(msg)
        return

    c.ok(f"Curriculum files ready at {dst}")
    c.info("Knowledge graph will be built on your first /guru session")


# ─── core install helpers ──────────────────────────────────────────────────────

def _check_claude_installed():
    if not claude_home().exists():
        c.err(f"{claude_home()} not found. Is Claude Code installed?")
        c.err("Get Claude Code at: https://claude.ai/code")
        raise SystemExit(1)


def _check_assets():
    if not (skill_assets() / "SKILL.md").exists():
        c.err("Skill assets missing from package.")
        c.err("Reinstall: pipx install --force embedded-guru")
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
        raise SystemExit(1)


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
    print(f"  Graphify:         {c.bold('ready') if graphify_ok else c.yellow('not found — install with: pipx install graphifyy')}")

    if reinstall:
        print()
        print(f"  {c.yellow('Upgrade note:')} student profiles in {data_dir()} were not touched.")

    if warnings:
        print()
        print(f"  {c.yellow('Warnings:')}")
        for w in warnings:
            print(f"    {c.yellow('⚠')} {w}")

    print()
    print(f"  Open Claude Code and type {c.bold('/guru')} to start.")
    print()


def _platform_label() -> str:
    if sys.platform == "win32":
        import platform
        return f"Windows {platform.release()}"
    if sys.platform == "darwin":
        import platform
        return f"macOS {platform.mac_ver()[0]}"
    return f"Linux ({sys.platform})"
