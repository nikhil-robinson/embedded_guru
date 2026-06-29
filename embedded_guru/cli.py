import argparse
import sys

from . import __version__
from .installer import install, uninstall


BANNER = r"""
  _____           _              _     _          _  _____
 | ____|_ __ ___ | |__   ___  __| | __| | ___  __| |/ ___| _   _ _ __ _   _
 |  _| | '_ ` _ \| '_ \ / _ \/ _` |/ _` |/ _ \/ _` | |  _| | | | '__| | | |
 | |___| | | | | | |_) |  __/ (_| | (_| |  __/ (_| | |_| | |_| | |  | |_| |
 |_____|_| |_| |_|_.__/ \___|\__,_|\__,_|\___|\__,_|\____|\__,_|_|   \__,_|

  Firmware development mentor for Claude Code  •  v{version}
"""


def main():
    parser = argparse.ArgumentParser(
        prog="embeddedguru",
        description="EmbeddedGuru — firmware development mentor for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  install     Install the EmbeddedGuru skill into Claude Code
  uninstall   Remove the skill (prompts before deleting student data)
  add         Add a document or datasheet to the curriculum knowledge base
  scorecard   Generate a PDF scorecard from an assessment JSON file

examples:
  embeddedguru install
  embeddedguru install --dry-run
  embeddedguru uninstall
  embeddedguru uninstall --keep-data
  embeddedguru uninstall --all
  embeddedguru add ~/Downloads/STM32F4_RM.pdf
  embeddedguru add ~/projects/can_signals.dbc
  embeddedguru scorecard ~/.claude/embedded_guru/nikhil/latest_assessment.json
        """,
    )
    parser.add_argument("--version", action="version", version=f"EmbeddedGuru {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # install
    p_install = subparsers.add_parser("install", help="Install the skill into Claude Code")
    p_install.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what will happen without making any changes",
    )
    p_install.add_argument(
        "--skip-graphify",
        action="store_true",
        help="Skip Graphify install check (offline installs, CI)",
    )

    # uninstall
    p_uninstall = subparsers.add_parser("uninstall", help="Remove the skill from Claude Code")
    group = p_uninstall.add_mutually_exclusive_group()
    group.add_argument(
        "--keep-data",
        action="store_true",
        help="Remove skill files but keep student profiles",
    )
    group.add_argument(
        "--all",
        dest="delete_all",
        action="store_true",
        help="Remove everything including student data without prompting",
    )

    # add
    p_add = subparsers.add_parser(
        "add",
        help="Add a document or datasheet to the curriculum knowledge base",
    )
    p_add.add_argument(
        "file",
        help="Path to the document to add (PDF, Markdown, DBC, etc.)",
    )

    # scorecard
    p_scorecard = subparsers.add_parser(
        "scorecard",
        help="Generate a PDF scorecard from an assessment JSON file",
    )
    p_scorecard.add_argument(
        "assessment",
        help="Path to the assessment JSON file produced by /guru assess",
    )
    p_scorecard.add_argument(
        "--out",
        metavar="DIR",
        help="Output directory (defaults to same directory as the assessment file)",
    )

    args = parser.parse_args()

    print(BANNER.format(version=__version__), flush=True)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "install":
            sys.exit(install(dry_run=args.dry_run, skip_graphify=args.skip_graphify))

        elif args.command == "uninstall":
            sys.exit(uninstall(keep_data=args.keep_data, delete_all=args.delete_all))

        elif args.command == "add":
            from .adder import add_document
            sys.exit(add_document(args.file))

        elif args.command == "scorecard":
            from pathlib import Path
            from .scorecard import generate
            from . import console as c
            try:
                out = generate(Path(args.assessment), Path(args.out) if args.out else None)
                c.ok(f"Scorecard written to: {out}")
                print()
                print(f"  Open the PDF and share it on LinkedIn!")
                print(f"  Tag it with #EmbeddedGuru #FirmwareEngineering")
                print()
                sys.exit(0)
            except FileNotFoundError as e:
                c.err(str(e))
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n  Cancelled.")
        sys.exit(1)
