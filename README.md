<div align="center">

```
  _____           _              _     _          _  _____
 | ____|_ __ ___ | |__   ___  __| | __| | ___  __| |/ ___| _   _ _ __ _   _
 |  _| | '_ ` _ \| '_ \ / _ \/ _` |/ _` |/ _ \/ _` | |  _| | | | '__| | | |
 | |___| | | | | | |_) |  __/ (_| | (_| |  __/ (_| | |_| | |_| | |  | |_| |
 |_____|_| |_| |_|_.__/ \___|\__,_|\__,_|\___|\__,_|\____|\__,_|_|   \__,_|
```

**Firmware development mentor for Claude Code — adaptive, project-driven, no hand-holding.**

[![PyPI Version](https://img.shields.io/pypi/v/embedded-guru?style=for-the-badge&color=0A66C2&label=PyPI)](https://pypi.org/project/embedded-guru/)
[![Python](https://img.shields.io/pypi/pyversions/embedded-guru?style=for-the-badge&color=3776AB)](https://pypi.org/project/embedded-guru/)
[![Build](https://img.shields.io/github/actions/workflow/status/nikhil-robinson/embedded_guru/publish.yml?style=for-the-badge&label=CI)](https://github.com/nikhil-robinson/embedded_guru/actions)
[![License](https://img.shields.io/github/license/nikhil-robinson/embedded_guru?style=for-the-badge&color=22C55E)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/embedded-guru?style=for-the-badge&color=F97316&label=installs%2Fmonth)](https://pypi.org/project/embedded-guru/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-8B5CF6?style=for-the-badge)](https://github.com/nikhil-robinson/embedded_guru)

<br/>

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support%20this%20project-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/nikhilrobinson)

</div>

---

## What is this?

EmbeddedGuru is a **Claude Code skill** that teaches bare-metal embedded firmware like a senior engineer would — by making you build things, not by explaining things.

It doesn't write your code. It asks what the peripheral status register says. It assigns real hardware tasks with real exit criteria. It remembers where you left off, tracks your progress across sessions, and pushes back when you try to copy-paste your way through a concept.

It knows about registers, not libraries. It knows about datasheets, not tutorials.

---

## Four Domain Tracks

<div align="center">

| Track | Hardware | Protocols | Standards |
|:---:|:---:|:---:|:---:|
| **IoT** | ESP32 · STM32 | UART · I2C · SPI · MQTT | — |
| **Automotive / CAN** | STM32 · CAN transceiver | CAN · OBD-II · UDS · ISO-TP | ISO 11898 · ISO 14229 |
| **Medical** | STM32 · ADC frontend | I2C · SPI · ADC · IWDG | IEC 62304 · IEC 60601-1 |
| **Industrial / RTOS** | STM32 · RS-485 | FreeRTOS · Modbus RTU · DMA | IEC 61508 · MISRA-C |

</div>

Every track shares a common foundation: **GPIO → UART → I2C → SPI → DMA** — from registers, not libraries.

---

## How it works

```
pipx install embedded-guru          # install the CLI
embeddedguru install                 # seeds Claude Code with skill + curriculum graph
/guru                                # start your first session
```

Behind the scenes, the installer:

1. Copies the **SKILL.md** mentor brain into `~/.claude/skills/embedded-guru/`
2. Copies the **curriculum knowledge base** (protocols, registers, boards, standards) into `~/.claude/embedded_guru/curriculum/`
3. Builds a **knowledge graph** with [Graphify](https://github.com/safishamsi/graphify) — every protocol fact and register value becomes a node the mentor queries instead of hallucinating
4. Registers the `/guru` trigger in `~/.claude/CLAUDE.md`

Every session end, your **student graph** (profile, assignments, milestones, progress) is updated — so the mentor always knows exactly where you are.

---

## Knowledge Graph Architecture

```
~/.claude/embedded_guru/
├── curriculum/
│   ├── concepts/        UART · SPI · I2C · CAN · DMA · FreeRTOS · watchdog
│   ├── hardware/        boards, peripherals, capabilities
│   ├── milestones/      IoT · Automotive · Medical · Industrial roadmaps
│   ├── mistakes/        10 common hardware + firmware mistakes
│   ├── standards/       MISRA-C · ISO 26262 · IEC 62304 · Modbus
│   └── graphify-out/
│       └── graph.json   ← curriculum facts (read-only, seeded at install)
│
└── <your-name>/
    └── graphify-out/
        └── graph.json   ← your profile, progress, assignments (updated each session)
```

Before generating any output, the mentor queries the graph:

```bash
graphify query "I2C pull-up resistor value" --graph ~/.claude/embedded_guru/curriculum/graphify-out/graph.json
# → returns verified fact from curriculum, not hallucinated value
```

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python 3.9+
- pipx

**Install pipx if you don't have it:**

```bash
# macOS
brew install pipx

# Linux
sudo apt install pipx

# Windows
pip install pipx
```

---

## Install

```bash
pipx install embedded-guru
embeddedguru install
```

> **Note:** Run `embeddedguru install` from Claude Code's built-in terminal — it has your `ANTHROPIC_API_KEY` available for the one-time curriculum graph build.

Then open Claude Code and type:

```
/guru
```

---

## Upgrade

```bash
pipx upgrade embedded-guru
embeddedguru install
```

---

## Session Commands

| Command | What happens |
|---|---|
| `/guru` | Start or resume your session |
| `/guru debug` | Jump straight into a debugging session |
| `/guru roadmap` | See your current roadmap and next milestone |
| `/guru assignment` | Check your open assignments |
| `/guru goal` | Review or update your end goal |
| `/guru profile` | See your full student profile |

---

## Install Options

```bash
# See what would be installed without making changes
embeddedguru install --dry-run

# Skip Graphify graph build (offline installs, CI environments)
embeddedguru install --skip-graphify
```

---

## Uninstall

```bash
embeddedguru uninstall          # keeps student data
embeddedguru uninstall --all    # removes everything including progress
pipx uninstall embedded-guru
```

Student profiles in `~/.claude/embedded_guru/` are kept by default.

---

## What the mentor will and won't do

<details>
<summary><b>Will do</b></summary>

- Assess your real level (L0–L3) from how you answer questions, not what you claim
- Build a custom roadmap for your domain and board
- Assign real hardware tasks with specific exit criteria
- Tell you which register to read when you're stuck
- Push back on code dumps ("I could. You'd fix this bug and forget how.")
- Acknowledge frustration before redirecting
- Track everything across sessions — no re-explaining your background every time

</details>

<details>
<summary><b>Won't do</b></summary>

- Write your firmware for you
- Accept "it works" as a milestone exit (working code + test output required)
- Let you skip Milestone 0 (datasheet literacy) regardless of claimed experience
- Pretend a Raspberry Pi 4 is suitable for bare-metal embedded development
- Teach I2C without asking what your pull-up resistor value is

</details>

---

## Supported Boards

| Board | Domain | Level | Notes |
|---|---|---|---|
| STM32 Nucleo-F446RE | All | L1–L3 | Recommended for most tracks |
| STM32 Nucleo-F411RE | IoT, Medical | L1–L2 | Budget option |
| ESP32-DevKitC | IoT | L1–L2 | WiFi/BT built-in |
| Raspberry Pi Pico | IoT | L1 | Good starter board |
| STM32F103 Blue Pill | All | L2–L3 | Cheap, widely available |
| Arduino Uno | IoT | L0→L1 only | HAL-only, no bare-metal CAN |
| Raspberry Pi 4 | — | — | ⚠ Not suitable for bare-metal embedded |

---

## Contributing

PRs welcome for:
- New curriculum files (`concepts/`, `hardware/`, `milestones/`)
- New board entries in `hardware/boards.md`
- Regression tests that expose wrong advice
- Bug reports via [Issues](https://github.com/nikhil-robinson/embedded_guru/issues)

```bash
git clone https://github.com/nikhil-robinson/embedded_guru
cd embedded_guru
pip install -e .
embeddedguru install --dry-run
```

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built by [Nikhil Robinson](https://github.com/nikhil-robinson)

If this helped you understand why your I2C bus was stuck, consider buying a coffee.

[![Buy Me A Coffee](https://img.shields.io/badge/☕_Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logoColor=black)](https://buymeacoffee.com/nikhilrobinson)

</div>
