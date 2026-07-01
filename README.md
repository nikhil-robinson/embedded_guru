<div align="center">

<img src="https://raw.githubusercontent.com/nikhil-robinson/embedded_guru/main/.github/assets/banner.svg" alt="EmbeddedGuru" width="100%"/>

<h1>⚡ EmbeddedGuru</h1>

<p><strong>The AI mentor that teaches bare-metal embedded firmware by making you build — not by explaining.</strong></p>
<p>Runs inside <a href="https://claude.ai/code">Claude Code</a>. Zero libraries. Zero hand-holding. Just registers, datasheets, and real hardware.</p>

<p>
  <a href="https://pypi.org/project/embedded-guru/"><img src="https://img.shields.io/pypi/v/embedded-guru?style=flat-square&logo=pypi&logoColor=white&label=version&color=6C4CE0&labelColor=0D1117" alt="PyPI Version"/></a>
  <a href="https://pypi.org/project/embedded-guru/"><img src="https://img.shields.io/pypi/pyversions/embedded-guru?style=flat-square&logo=python&logoColor=white&label=python&color=00D1B2&labelColor=0D1117" alt="Python Versions"/></a>
  <a href="https://github.com/nikhil-robinson/embedded_guru/actions"><img src="https://img.shields.io/github/actions/workflow/status/nikhil-robinson/embedded_guru/publish.yml?style=flat-square&logo=githubactions&logoColor=white&label=build&labelColor=0D1117" alt="Build Status"/></a>
  <img src="https://img.shields.io/badge/license-MIT-00D1B2?style=flat-square&logo=opensourceinitiative&logoColor=white&labelColor=0D1117" alt="License"/>
  <a href="https://github.com/nikhil-robinson/embedded_guru/stargazers"><img src="https://img.shields.io/github/stars/nikhil-robinson/embedded_guru?style=flat-square&logo=github&logoColor=white&label=stars&color=FFB800&labelColor=0D1117" alt="Stars"/></a>
  <img src="https://img.shields.io/badge/platform-macOS_·_Linux_·_Windows-6C4CE0?style=flat-square&logo=gnometerminal&logoColor=white&labelColor=0D1117" alt="Platform"/>
</p>

<p>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/▶-Quick_Start-0D1117?style=for-the-badge&color=6C4CE0" alt="Quick Start"/></a>
  <a href="#-four-domain-tracks"><img src="https://img.shields.io/badge/◆-Domain_Tracks-0D1117?style=for-the-badge&color=00D1B2" alt="Domain Tracks"/></a>
  <a href="https://buymeacoffee.com/nilkhil_robinson"><img src="https://img.shields.io/badge/☕-Buy_Me_A_Coffee-0D1117?style=for-the-badge&color=FFB800" alt="Buy Me A Coffee"/></a>
</p>

</div>

---

## What is this?

**EmbeddedGuru** is a [Claude Code](https://claude.ai/code) skill that teaches bare-metal embedded firmware the way a senior engineer would — by making you build real things, not by explaining slides at you.

It won't write your code. It'll ask what the peripheral status register says. It assigns real hardware tasks with specific exit criteria, remembers exactly where you left off, tracks your progress across sessions, and pushes back the moment you try to copy-paste your way through a concept.

> It knows registers, not libraries. Datasheets, not tutorials.

New to embedded systems entirely? New to Claude Code? Both are fine — the sections below walk through everything from scratch.

---

## 🚀 Quick Start

New here? Start with **step 0** — it's the one people skip and then get stuck on.

### 0. Install Claude Code

EmbeddedGuru is a skill that runs *inside* [Claude Code](https://claude.ai/code), Anthropic's official CLI. If you don't have it yet:

```bash
npm install -g @anthropic-ai/claude-code
claude          # launches Claude Code — sign in with your Anthropic account when prompted
```

> Don't have Node.js? Grab it from [nodejs.org](https://nodejs.org) first (v18+). Full install docs: [docs.claude.com/claude-code](https://docs.claude.com/en/docs/claude-code)

### 1. Install EmbeddedGuru

```bash
pipx install embedded-guru      # install the CLI (isolated, no dependency conflicts)
embeddedguru install            # seeds Claude Code with the mentor skill + curriculum graph
```

Don't have `pipx`? See [Prerequisites](#prerequisites) below.

### 2. Start learning

```bash
embeddedguru run
```

That's it — `embeddedguru run` launches Claude Code and drops you straight into your first `/guru` session. Prefer to do it manually? Open Claude Code yourself and type `/guru`.

Behind the scenes, the installer:

1. Checks [Graphify](https://github.com/safishamsi/graphify) is installed — installs it if not
2. Copies the **SKILL.md** mentor brain into `~/.claude/skills/embedded-guru/`
3. Copies the **curriculum knowledge base** (protocols, registers, boards, standards) into `~/.claude/embedded_guru/curriculum/`
4. Registers the `/guru` trigger in `~/.claude/CLAUDE.md`

On your **first session**, the skill builds the curriculum knowledge graph automatically inside Claude Code. Every session end, your **student graph** (profile, assignments, milestones, progress) is updated — so the mentor always knows exactly where you are.

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
# → returns verified fact from curriculum, not a hallucinated value
```

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed — see [step 0](#-quick-start) above
- Python 3.9+
- pipx

**Install pipx:**

```bash
brew install pipx        # macOS
sudo apt install pipx    # Linux
pip install pipx         # Windows
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
| `/guru interview` | Run a mock technical interview — calibrated to your level and domain |
| `/guru assess` | Run a formal assessment → generates a PNG scorecard you can share |

---

## Mock Interview

`/guru interview` simulates a real embedded engineering technical interview: 8–10 questions across warm-up, register-level, debugging scenario, and system design categories — calibrated to your current level.

No hints. No feedback mid-session. Debrief with per-question scores, strengths, gaps, and interview readiness at the end.

---

## Assessment Scorecard

`/guru assess` runs a formal 5-category scored test and generates a **PNG certificate** you can share on LinkedIn.

**Categories:**
- Core Firmware Fundamentals (20%)
- Protocol Knowledge (25%)
- Safety & Reliability (20%)
- Domain Expertise (25%)
- Debugging & Problem Solving (10%)

**Grades:** Novice → Practitioner → Engineer → Senior Engineer → Expert → Principal Engineer

The scorecard PNG is watermarked with EmbeddedGuru branding and your name.

---

## Teach the Mentor Your Datasheets

Drop any datasheet, reference manual, DBC file, or application note into the curriculum:

```bash
embeddedguru add ~/Downloads/STM32H7_RM.pdf
embeddedguru add ~/projects/vehicle_signals.dbc
embeddedguru add ~/docs/company_spi_spec.md
```

On your next `/guru` session, the knowledge graph is rebuilt automatically — and the mentor can now answer questions grounded in your exact chip, bus definition, or document.

---

## Install Options

```bash
embeddedguru install --dry-run        # preview without making changes
embeddedguru install --skip-graphify  # skip graphify check (offline / CI)
embeddedguru add <file>               # add any document to the curriculum
embeddedguru scorecard <file.json>    # generate PNG from an assessment JSON
```

---

## Uninstall

```bash
embeddedguru uninstall          # keeps student data
embeddedguru uninstall --all    # removes everything including progress
pipx uninstall embedded-guru
```

---

## What the mentor will and won't do

<details>
<summary><b>Will do</b></summary>

- Ask who you are first (12th standard, college student, ECE/EEE grad, or working professional) — then assess your real level (L0–L3) *within that persona* from how you answer questions, not what you claim
- Teach you your first program from scratch if you've never written code at all, on your own board, in the same session — not send you off to learn elsewhere first
- Build a custom roadmap for your domain and board
- Assign real hardware tasks with specific exit criteria
- Tell you which register to read when you're stuck
- Push back on code dumps — *"I could. You'd fix this bug and forget how."*
- Acknowledge frustration before redirecting
- Track everything across sessions — no re-explaining your background each time

</details>

<details>
<summary><b>Won't do</b></summary>

- Write your firmware for you
- Accept "it works" as a milestone exit — working code + test output required
- Let you skip Milestone 0 (datasheet literacy) regardless of claimed experience
- Pretend a Raspberry Pi 4 is suitable for bare-metal embedded development
- Teach I2C without first asking what pull-up resistor value you used

</details>

---

## Supported Boards

| Board | Domain | Level | Notes |
|---|---|---|---|
| STM32 Nucleo-F446RE | All | L1–L3 | Recommended for most tracks |
| STM32 Nucleo-F411RE | IoT · Medical | L1–L2 | Budget option |
| ESP32-DevKitC | IoT | L1–L2 | WiFi/BT built-in |
| Raspberry Pi Pico | IoT | L1 | Good starter board |
| STM32F103 Blue Pill | All | L2–L3 | Cheap, widely available |
| Arduino Uno | IoT | L0 → L1 only | HAL-only, no bare-metal CAN |
| Raspberry Pi 4 | — | — | ⚠ Not suitable for bare-metal embedded |

---

## Contributing

PRs welcome for curriculum files, new board entries, and regression tests that expose wrong advice.

```bash
git clone https://github.com/nikhil-robinson/embedded_guru
cd embedded_guru
pip install -e .
embeddedguru install --dry-run
```

Open issues at [github.com/nikhil-robinson/embedded_guru/issues](https://github.com/nikhil-robinson/embedded_guru/issues)

---

## Acknowledgements

Knowledge graph powered by [Graphify](https://github.com/safishamsi/graphify) — built by [@safishamsi](https://github.com/safishamsi). Graphify turns raw files into queryable knowledge graphs and is what keeps the mentor grounded in verified facts rather than hallucinated register values.

---

## Disclaimer & Legal Notice

**EmbeddedGuru is an educational tool. It is not a professional engineering service, a certified design tool, or a substitute for human expert review.**

### No Data Collection

EmbeddedGuru collects no personal data. All student profiles, progress files, curriculum graphs, and assessment results are stored exclusively on your local machine under `~/.claude/embedded_guru/`. Nothing is transmitted to the developer or any third party by this software.

> EmbeddedGuru runs inside [Claude Code](https://claude.ai/code), an Anthropic product. Your conversations are subject to [Anthropic's Privacy Policy](https://www.anthropic.com/privacy). EmbeddedGuru has no control over or access to that data.

### AI Limitations — Verify Everything

Outputs produced by this skill are generated by a large language model and **may contain errors**, including but not limited to:

- Incorrect register addresses, bit masks, or timing values
- Inaccurate protocol specifications (CAN, I2C, SPI, Modbus, UDS, ISO-TP)
- Outdated or inapplicable references to datasheets and standards
- Plausible-sounding but incorrect debugging guidance

**Always verify any register value, timing requirement, voltage level, or protocol detail against the official datasheet or reference manual for your specific hardware revision before using it in real firmware.**

### Safety-Critical Domains

EmbeddedGuru teaches concepts related to medical devices (IEC 62304, IEC 60601-1) and automotive systems (ISO 26262, ISO 14229, MISRA-C) for **educational purposes only**.

- It is **not** a certified validation or verification tool under any standard.
- It does **not** produce outputs suitable for submission to any regulatory body.
- Firmware intended for use in medical devices, vehicles, industrial control systems, or any other safety-critical application **must** be designed, reviewed, and validated by qualified engineers following the applicable certification processes.

Using this tool for safety-critical production firmware without proper human expert review and certification is done entirely at your own risk.

### No Warranty / Limitation of Liability

This software is provided **"as is"** without warranty of any kind, express or implied. To the maximum extent permitted by applicable law:

- The developer (Nikhil Robinson) and any contributors are **not liable** for any direct, indirect, incidental, special, or consequential damages arising from the use of this software or the AI-generated content it produces.
- This includes, without limitation: hardware damage, data loss, personal injury, regulatory non-compliance, financial loss, or any other harm resulting from acting on AI-generated advice without independent verification.

See [LICENSE](LICENSE) for the full MIT license terms.

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Built by [Nikhil Robinson](https://github.com/nikhil-robinson)**

*If this helped you understand why your I2C bus was stuck at 3am, consider buying a coffee.*

<a href="https://buymeacoffee.com/nilkhil_robinson"><img src="https://img.shields.io/badge/☕-Buy_Me_A_Coffee-0D1117?style=for-the-badge&color=FFB800" alt="Buy Me A Coffee"/></a>
<a href="https://github.com/nikhil-robinson/embedded_guru"><img src="https://img.shields.io/badge/⭐-Star_on_GitHub-0D1117?style=for-the-badge&color=6C4CE0" alt="Star on GitHub"/></a>

</div>
