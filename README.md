# EmbeddedGuru

A firmware development mentor skill for Claude Code. Project-driven, adaptive, no hand-holding.

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python 3.7+
- pipx

**Install pipx if you don't have it:**

| Platform | Command |
|---|---|
| Mac | `brew install pipx` |
| Linux | `sudo apt install pipx` |
| Windows | `pip install pipx` |

## Install

```
pipx install git+https://github.com/nikhil-robinson/embedded_guru.git
embeddedguru install
```

Then open Claude Code and type `/guru` to start your first session.

## Upgrade

```
pipx upgrade embedded-guru
embeddedguru install
```

## Uninstall

```
embeddedguru uninstall
pipx uninstall embedded-guru
```

Student profiles in `~/.claude/embedded_guru/` are kept by default. Add `--all` to remove them too.

## Usage

Once installed, everything happens inside Claude Code:

| Command | What it does |
|---|---|
| `/guru` | Start or continue a session |
| `/guru debug` | Jump straight to debugging |
| `/guru roadmap` | See your current roadmap and next milestone |
| `/guru assignment` | Check open assignments |
| `/guru goal` | Review or update your goal |
| `/guru profile` | See your student profile |
