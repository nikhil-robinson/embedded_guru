import re
import shutil
from pathlib import Path

from . import __version__
from .paths import claude_home, skill_dir, data_dir, claude_md, skill_assets
from . import console as c

CLAUDE_MD_BLOCK = """\
# embedded-guru
- **embedded-guru** (`~/.claude/skills/embedded-guru/SKILL.md`) - firmware development mentor. Trigger: `/guru` or `/embedded-guru`
When the user types `/guru` or `/embedded-guru`, invoke the Skill tool with `skill: "embedded-guru"` before doing anything else."""


def install(dry_run: bool = False) -> int:
    c.header(f"EmbeddedGuru — installer v{__version__}")

    _check_claude_installed()
    _check_assets()

    reinstall = skill_dir().exists()
    if reinstall:
        existing = _read_version()
        c.warn(f"EmbeddedGuru {existing} already installed — upgrading to {__version__}")

    _install_skill_files(dry_run)
    _ensure_data_dir(dry_run)
    _register(dry_run)

    print()
    prefix = f"{c.bold('[DRY RUN]')} " if dry_run else ""
    print(f"  {prefix}{c.bold(f'EmbeddedGuru {__version__} installed successfully.')}")
    print()
    print(f"  Start a session:  {c.bold('/guru')}")
    print(f"  Debug mode:       {c.bold('/guru debug')}")
    print(f"  View roadmap:     {c.bold('/guru roadmap')}")
    print(f"  Student data:     {c.bold(str(data_dir()))}")
    print()
    if reinstall:
        print(f"  {c.yellow('Upgrade note:')} student profiles in {data_dir()} were not touched.")
        print()
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
            answer = input("  Delete student data? [y/N] ").strip().lower()
            print()
            remove_data = answer == "y"

    _remove_skill_files()
    _deregister()

    if data_dir().exists():
        if remove_data:
            c.header("Removing student data")
            c.info(f"Removing {data_dir()}")
            shutil.rmtree(data_dir())
            c.ok("Student data removed")
        else:
            c.ok(f"Student data kept at {data_dir()}")

    print()
    print(f"  {c.bold('EmbeddedGuru uninstalled.')}")
    print()
    return 0


# ─── helpers ───────────────────────────────────────────────────────────────────

def _check_claude_installed():
    if not claude_home().exists():
        c.err(f"{claude_home()} not found. Is Claude Code installed?")
        print("  Get it at: https://claude.ai/code")
        raise SystemExit(1)


def _check_assets():
    if not (skill_assets() / "SKILL.md").exists():
        c.err("Skill assets missing from package — reinstall with: pip install --force-reinstall embedded-guru")
        raise SystemExit(1)


def _read_version() -> str:
    v = skill_dir() / ".version"
    return v.read_text().strip() if v.exists() else "unknown"


def _install_skill_files(dry_run: bool):
    c.header("Installing skill files")
    assets = skill_assets()

    if not dry_run:
        skill_dir().mkdir(parents=True, exist_ok=True)

    c.info(f"Copying SKILL.md")
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
        (skill_dir() / ".version").write_text(__version__)
    c.ok(f"Skill files installed to {skill_dir()}")


def _ensure_data_dir(dry_run: bool):
    c.header("Setting up student data directory")
    c.info(f"Ensuring {data_dir()} exists")
    if not dry_run:
        data_dir().mkdir(parents=True, exist_ok=True)
    c.ok(f"Student data directory ready at {data_dir()}")


def _register(dry_run: bool):
    c.header("Registering skill")
    md = claude_md()

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
        md.write_text(text, encoding="utf-8")
    c.ok(f"Registered /guru trigger in {md}")


def _remove_skill_files():
    c.header("Removing skill files")
    if skill_dir().exists():
        c.info(f"Removing {skill_dir()}")
        shutil.rmtree(skill_dir())
        c.ok("Skill files removed")
    else:
        c.warn("Skill directory not found — already uninstalled?")


def _deregister():
    c.header("Cleaning up CLAUDE.md")
    md = claude_md()
    if not md.exists():
        c.warn("CLAUDE.md not found — nothing to clean up")
        return

    text = md.read_text(encoding="utf-8")
    if "# embedded-guru" not in text:
        c.warn("No embedded-guru registration found in CLAUDE.md")
        return

    c.info("Removing registration from CLAUDE.md")
    text = re.sub(r"\n# embedded-guru\n.*\n.*", "", text, flags=re.MULTILINE)
    md.write_text(text, encoding="utf-8")
    c.ok("Registration removed")
