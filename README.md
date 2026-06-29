# EmbeddedGuru

A firmware development mentor skill for Claude Code. Project-driven, adaptive, no hand-holding.

Teaches bare-metal embedded firmware by building real things — registers, protocols, RTOS, and hardware truth — not tutorial code.

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and running
- Python 3.9+

## Install

```bash
pip install embedded-guru
embeddedguru install
```

Then open Claude Code and type `/guru` to start your first session.

## Upgrade

```bash
pip install --upgrade embedded-guru
embeddedguru install
```

## Uninstall

```bash
embeddedguru uninstall
pip uninstall embedded-guru
```

Student profiles in `~/.claude/embedded_guru/` are kept by default. Add `--all` to remove them too:

```bash
embeddedguru uninstall --all
```

## Usage

Everything happens inside Claude Code after install:

| Command | What it does |
|---|---|
| `/guru` | Start or continue a session |
| `/guru debug` | Jump straight to debugging |
| `/guru roadmap` | See your current roadmap and next milestone |
| `/guru assignment` | Check open assignments |
| `/guru goal` | Review or update your goal |
| `/guru profile` | See your student profile |

## What it teaches

Four domain tracks, each with structured milestones and exit criteria:

- **IoT** — ESP32/STM32 + WiFi + MQTT + OTA
- **Automotive/CAN** — bxCAN, OBD-II, DBC decoding, UDS diagnostics
- **Medical** — signal acquisition, IEC 62304 awareness, watchdog, alarm systems
- **Industrial/RTOS** — FreeRTOS, Modbus RTU, RS-485, 72-hour soak tests

All tracks share a universal foundation: GPIO, clock trees, UART, I2C, SPI, DMA — from registers, not libraries.

## Install options

```bash
# Preview what install would do without making changes
embeddedguru install --dry-run

# Skip Graphify graph build (offline installs)
embeddedguru install --skip-graphify
```

## Knowledge graph (optional)

EmbeddedGuru uses [Graphify](https://github.com/safishamsi/graphify) to build a local knowledge graph from curriculum data. This reduces hallucinations on protocol facts, register values, and hardware specs by grounding every explanation in verified source files.

Graphify is installed automatically. To build or rebuild the graph manually:

```bash
graphify ~/.claude/embedded_guru/curriculum/ --no-viz
```

## Source

[github.com/nikhil-robinson/embedded_guru](https://github.com/nikhil-robinson/embedded_guru)
