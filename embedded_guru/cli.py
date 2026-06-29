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
    print(BANNER.format(version=__version__))

    parser = argparse.ArgumentParser(
        prog="embeddedguru",
        description="EmbeddedGuru — firmware development mentor for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  install     Install the EmbeddedGuru skill into Claude Code
  uninstall   Remove the skill (prompts before deleting student data)

examples:
  embeddedguru install
  embeddedguru install --dry-run
  embeddedguru uninstall
  embeddedguru uninstall --keep-data
  embeddedguru uninstall --all
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

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "install":
            sys.exit(install(dry_run=args.dry_run))
        elif args.command == "uninstall":
            sys.exit(uninstall(keep_data=args.keep_data, delete_all=args.delete_all))
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        sys.exit(1)
