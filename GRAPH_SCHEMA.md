# EmbeddedGuru — Knowledge Graph Schema

Every fact the skill needs lives in this graph. The LLM queries specific nodes instead of reading large markdown files. No fact is inferred from context — it is retrieved from the graph. This eliminates hallucination at every point where the skill currently loads text into context and hopes the model reads it correctly.

---

## Design Principles

- **Graph is the single source of truth.** Markdown files are human-readable exports generated from the graph, not the source.
- **Every fact is a node or edge property.** Nothing lives in freeform text that needs to be parsed.
- **Two graph partitions:** Curriculum (seeded at install, rarely changes) and Student (written each session, changes constantly).
- **Immutable curriculum facts.** Curriculum nodes are never modified after seeding — only new student nodes are written. This means the LLM cannot accidentally corrupt embedded knowledge by writing wrong things.
- **Queries replace context loading.** Instead of loading 4 markdown files (400–800 tokens per session), the skill fires 3–5 targeted queries and gets exact facts back.

---

## Node Types

### Curriculum Nodes (seeded at install, immutable)

#### `:Domain`
```
name: "IoT" | "Automotive" | "Medical" | "Industrial"
description: one-line summary
```

#### `:Milestone`
```
id: "automotive_m3"           # domain + number, unique
number: 3
title: "CAN Frame Transmit"
domain: "Automotive"
constraint_summary: "Send raw CAN frame, verify on bus"
is_gate: false                # true only for Milestone 0
```

#### `:ExitCriteria`
```
milestone_id: "automotive_m3"
text: "Frame appears on bus with correct ID, DLC, and payload..."
requires_artifact: true       # false = can explain; true = must show code+output
artifact_description: "Working code + UART output OR automated test"
level_variant: "L3"           # null means applies to all levels
```

#### `:HardwareRequirement`
```
milestone_id: "automotive_m3"
item: "CAN transceiver"
specifics: "SN65HVD230 or MCP2551"
blocking: true                # if true, milestone cannot start without this HW
alternatives: "Second STM32 node running loopback"
```

#### `:Board`
```
name: "STM32 Nucleo-F446RE"   # unique display name
mcu: "STM32F446RE"
vendor: "STMicroelectronics"
architecture: "Cortex-M4"
is_microcontroller: true      # RPi4 = false, Arduino Mega = true
price_usd_approx: 15
reference_manual: "RM0390"
```

#### `:Peripheral`
```
name: "bxCAN"
type: "CAN"                   # CAN | SPI | I2C | UART | IWDG | WWDG | DMA | ADC | Timer | WiFi | BLE
notes: "bxCAN on F4 series, not FDCAN — different register map"
bare_metal_capable: true      # false for SocketCAN on Linux SBCs
```

#### `:Concept`
```
name: "CAN arbitration"
domain: "Automotive"          # "universal" if cross-domain
layer: "protocol"             # hardware | protocol | software | safety | rtos
one_liner: "Bitwise dominance: 0 beats 1. Lower ID wins."
```

#### `:Fact`
```
concept: "CAN arbitration"
text: "CAN uses CSMA/CA — Carrier Sense Multiple Access with Collision Avoidance via bitwise arbitration. A dominant bit (0) overwrites a recessive bit (1). The node transmitting the lower ID wins automatically and continues. Unlike Ethernet CSMA/CD, there is no collision — the loser backs off silently."
fact_type: "spec"             # spec | register | timing | pinout | safety_rule | common_mistake
source: "ISO 11898-1"
```

#### `:CommonMistake`
```
concept: "I2C pullup"
mistake: "Using 1-ohm resistors for 'stronger' signal"
why_wrong: "I2C is open-drain. A 1Ω pullup draws 3.3A from the 3.3V rail — 130x over STM32 GPIO sink limit. The line may never reach logic-high, and you risk damaging the GPIO."
correct: "Use 2.2kΩ–10kΩ. At 100kHz/3.3V, 4.7kΩ is the standard starting point."
```

#### `:Standard`
```
name: "IEC 62304"
domain: "Medical"
summary: "Software lifecycle standard for medical device software. Defines development, maintenance, and risk management processes."
key_rules: ["No dynamic allocation in safety-critical paths", "Document software units with purpose, inputs, outputs, failure modes"]
```

#### `:Register`
```
name: "RCC_APB1ENR"
address: "0x40023840"
peripheral: "I2C1"
board_family: "STM32F4"
bit_field: "I2C1EN"
bit_position: 21
description: "Enable clock for I2C1 peripheral. Must set before configuring any I2C1 register."
```

---

### Student Nodes (written each session)

#### `:Student`
```
name: "Arjun"                 # unique key
level: "L2"                   # L0 | L1 | L2 | L3
domain: "Automotive"
sessions_count: 3
last_session: "2026-06-29"
c_experience: true            # explicitly probed during assessment
```

#### `:Goal`
```
student: "Arjun"
text: "Real-time CAN OBD-II logger to SD card — speed, RPM, throttle position"
domain_implied: "Automotive"
is_concrete: true
created_date: "2026-06-29"
archived_date: null           # null = active
```

#### `:StudentMilestone`
```
student: "Arjun"
milestone_id: "automotive_m0"
status: "complete"            # open | complete | blocked | pre_credited
completed_date: "2026-07-05"
what_they_built: "I2C read of LM75, raw register, prints Celsius over UART"
what_broke: "NACK on first read — forgot to set pointer register before read command"
```

#### `:Assignment`
```
id: 1
student: "Arjun"
title: "Read Temperature Sensor over I2C, Raw Registers"
assigned_date: "2026-06-29"
status: "open"                # open | complete | deferred | skipped
milestone_id: "automotive_m0"
board: "STM32 Nucleo-F446RE"
skipped_count: 0
```

#### `:AssignmentComponent`
```
assignment_id: 1
component_type: "outcome"     # outcome | constraint | hint_threshold | stretch | checkpoint
text: "Print real temperature value over UART using only raw I2C register access"
```

#### `:Session`
```
student: "Arjun"
number: 1
date: "2026-06-29"
session_type: "Onboarding"    # Onboarding | Regular | Debug | Roadmap | Goal
```

#### `:SessionEntry`
```
session_id: "arjun_s1"
entry_type: "next_focus"      # covered | student_signal | assigned | unresolved | next_focus
text: "Assignment #1 checkpoint: temperature register address and output format from datasheet"
```

#### `:SkillConfirmed`
```
student: "Arjun"
skill: "I2C raw register read"
confirmed_date: "2026-07-05"
demonstrated_by: "Printed LM75 temperature from register 0x00 without HAL_I2C_Mem_Read"
```

#### `:MentorNote`
```
student: "Arjun"
date: "2026-06-29"
text: "Honest and self-aware about gaps. Accepted constraint framing without pushback. Goal is concrete and personally motivated."
```

---

## Edge Types

### Student ↔ Everything
```
(Student)-[:HAS_ACTIVE_GOAL]->(Goal)
(Student)-[:HAD_GOAL {archived_date}]->(Goal)
(Student)-[:USES_BOARD]->(Board)
(Student)-[:HAS_ASSIGNMENT]->(Assignment)
(Student)-[:HAD_SESSION]->(Session)
(Student)-[:ON_MILESTONE]->(StudentMilestone)           # current milestone
(Student)-[:CONFIRMED_SKILL]->(SkillConfirmed)
(Student)-[:HAS_NOTE]->(MentorNote)
(Student)-[:IN_DOMAIN]->(Domain)
```

### Roadmap Structure (curriculum, immutable)
```
(Domain)-[:HAS_MILESTONE {order}]->(Milestone)
(Milestone)-[:PRECEDES]->(Milestone)
(Milestone)-[:REQUIRES_HW]->(HardwareRequirement)
(Milestone)-[:TEACHES]->(Concept)
(Milestone)-[:HAS_EXIT_CRITERIA]->(ExitCriteria)
```

### Student Roadmap Progress
```
(StudentMilestone)-[:INSTANCE_OF]->(Milestone)          # links to curriculum milestone
(StudentMilestone)-[:CUSTOMIZED_TITLE {text}]->()       # student-specific version of milestone
(Assignment)-[:FOR_MILESTONE]->(Milestone)
(Assignment)-[:HAS_COMPONENT]->(AssignmentComponent)
(Assignment)-[:ISSUED_IN]->(Session)
(Assignment)-[:CLOSED_IN]->(Session)
```

### Session Chain
```
(Session)-[:HAS_ENTRY]->(SessionEntry)
(Session)-[:COVERED_CONCEPT]->(Concept)
(Session)-[:PRODUCED_ASSIGNMENT]->(Assignment)
(Session)-[:RESOLVED_ASSIGNMENT]->(Assignment)
(Session)-[:FOLLOWED_BY]->(Session)
```

### Hardware
```
(Board)-[:HAS_PERIPHERAL]->(Peripheral)
(Board)-[:LACKS_PERIPHERAL {workaround}]->(Peripheral)  # critical for RPi4 / bare-metal detection
(Board)-[:RECOMMENDED_FOR]->(Domain)
(Board)-[:RECOMMENDED_FOR_LEVEL]->(Level)
```

### Knowledge
```
(Concept)-[:HAS_FACT]->(Fact)
(Concept)-[:HAS_COMMON_MISTAKE]->(CommonMistake)
(Concept)-[:PREREQUISITE_FOR]->(Concept)
(Concept)-[:USED_IN]->(Domain)
(Concept)-[:SPECIFIED_BY]->(Standard)
(Concept)-[:HAS_REGISTER]->(Register)
```

---

## Query Patterns

### Session Start (replaces loading 4 markdown files)

```cypher
-- Student state
MATCH (s:Student {name: $name})
RETURN s.level, s.domain, s.sessions_count, s.last_session, s.c_experience

-- Open assignments
MATCH (s:Student {name: $name})-[:HAS_ASSIGNMENT]->(a:Assignment {status: "open"})
RETURN a.id, a.title, a.assigned_date, a.skipped_count

-- Last session's next focus
MATCH (s:Student {name: $name})-[:HAD_SESSION]->(sess:Session)
MATCH (sess)-[:HAS_ENTRY]->(e:SessionEntry {entry_type: "next_focus"})
ORDER BY sess.date DESC LIMIT 1
RETURN e.text

-- Current milestone
MATCH (s:Student {name: $name})-[:ON_MILESTONE]->(sm:StudentMilestone)
MATCH (sm)-[:INSTANCE_OF]->(m:Milestone)
MATCH (m)-[:HAS_EXIT_CRITERIA]->(ec:ExitCriteria)
RETURN m.title, sm.status, ec.text, ec.requires_artifact
```

### Before Explaining a Concept (replaces freehand generation)

```cypher
-- Get facts for concept
MATCH (c:Concept {name: $concept})-[:HAS_FACT]->(f:Fact)
RETURN f.text, f.fact_type, f.source

-- Get common mistakes for concept
MATCH (c:Concept {name: $concept})-[:HAS_COMMON_MISTAKE]->(m:CommonMistake)
RETURN m.mistake, m.why_wrong, m.correct

-- Get relevant registers for board
MATCH (r:Register {board_family: $board_family, peripheral: $peripheral})
RETURN r.name, r.address, r.bit_field, r.description
```

### Before Assigning a Milestone

```cypher
-- Check hardware requirements
MATCH (m:Milestone {id: $milestone_id})-[:REQUIRES_HW]->(hw:HardwareRequirement)
RETURN hw.item, hw.specifics, hw.blocking, hw.alternatives

-- Check student's board has needed peripherals
MATCH (b:Board {name: $board_name})-[:HAS_PERIPHERAL]->(p:Peripheral {type: $peripheral_type})
RETURN p.name, p.notes
-- If no result: board lacks peripheral → flag before assigning
```

### On "CAN is like I2C" Type Correction

```cypher
MATCH (c1:Concept {name: "CAN bus"})-[:HAS_FACT]->(f:Fact)
MATCH (c2:Concept {name: "I2C"})-[:HAS_FACT]->(f2:Fact)
RETURN f.text, f2.text
-- Returns exact protocol facts → correction is graph-sourced, not hallucinated
```

### Domain Pivot (cross-domain M0 transfer)

```cypher
MATCH (s:Student {name: $name})-[:ON_MILESTONE]->(sm:StudentMilestone {status: "complete"})
MATCH (sm)-[:INSTANCE_OF]->(m:Milestone {number: 0})
RETURN sm.completed_date, sm.what_they_built
-- If result exists → mark new domain M0 as pre_credited, carry the completion date
```

### Board Recommendation (no-board students)

```cypher
MATCH (b:Board)-[:RECOMMENDED_FOR]->(d:Domain {name: $domain})
MATCH (b)-[:RECOMMENDED_FOR_LEVEL]->(l:Level {name: $level})
RETURN b.name, b.mcu, b.price_usd_approx
ORDER BY b.price_usd_approx ASC LIMIT 2
```

### Assignment History (detect repeat skipping)

```cypher
MATCH (s:Student {name: $name})-[:HAS_ASSIGNMENT]->(a:Assignment)
WHERE a.status IN ["open", "skipped"]
RETURN a.title, a.assigned_date, a.skipped_count
ORDER BY a.assigned_date DESC
-- Two or more skipped_count > 0 → trigger recalibration conversation
```

---

## Write Patterns

### End of Onboarding

```cypher
CREATE (s:Student {name: "Arjun", level: "L2", domain: "Automotive", sessions_count: 1, last_session: "2026-06-29", c_experience: false})
CREATE (g:Goal {student: "Arjun", text: "...", is_concrete: true, created_date: "2026-06-29"})
CREATE (s)-[:HAS_ACTIVE_GOAL]->(g)
CREATE (s)-[:USES_BOARD]->(b:Board {name: "STM32 Nucleo-F446RE"})
-- Link to domain
MATCH (d:Domain {name: "Automotive"})
CREATE (s)-[:IN_DOMAIN]->(d)
-- Create M0 as open
MATCH (m:Milestone {id: "automotive_m0"})
CREATE (sm:StudentMilestone {student: "Arjun", milestone_id: "automotive_m0", status: "open"})
CREATE (sm)-[:INSTANCE_OF]->(m)
CREATE (s)-[:ON_MILESTONE]->(sm)
-- Create assignment #1
CREATE (a:Assignment {id: 1, student: "Arjun", title: "...", assigned_date: "2026-06-29", status: "open", milestone_id: "automotive_m0"})
CREATE (s)-[:HAS_ASSIGNMENT]->(a)
```

### End of Session

```cypher
-- Increment session count
MATCH (s:Student {name: "Arjun"})
SET s.sessions_count = s.sessions_count + 1, s.last_session = "2026-07-06"
-- Create session node
CREATE (sess:Session {student: "Arjun", number: 2, date: "2026-07-06", session_type: "Regular"})
CREATE (s)-[:HAD_SESSION]->(sess)
-- Session entries
CREATE (e1:SessionEntry {entry_type: "covered", text: "LM75 datasheet register map"})
CREATE (sess)-[:HAS_ENTRY]->(e1)
CREATE (e2:SessionEntry {entry_type: "next_focus", text: "Bring UART output showing temperature value"})
CREATE (sess)-[:HAS_ENTRY]->(e2)
```

### Milestone Completion

```cypher
MATCH (s:Student {name: "Arjun"})-[:ON_MILESTONE]->(sm:StudentMilestone {milestone_id: "automotive_m0"})
SET sm.status = "complete", sm.completed_date = "2026-07-12", sm.what_they_built = "...", sm.what_broke = "..."
-- Move to next milestone
MATCH (m_current:Milestone {id: "automotive_m0"})-[:PRECEDES]->(m_next:Milestone)
CREATE (sm_next:StudentMilestone {student: "Arjun", milestone_id: m_next.id, status: "open"})
CREATE (sm_next)-[:INSTANCE_OF]->(m_next)
MATCH (s:Student {name: "Arjun"})
DELETE (s)-[:ON_MILESTONE]->(sm)
CREATE (s)-[:ON_MILESTONE]->(sm_next)
-- Add confirmed skill
CREATE (sk:SkillConfirmed {student: "Arjun", skill: "I2C raw register read", confirmed_date: "2026-07-12", demonstrated_by: "..."})
CREATE (s)-[:CONFIRMED_SKILL]->(sk)
```

---

## Graph Partition Map

```
Curriculum Graph (seeded at install, read-only at runtime)
├── :Domain (4 nodes)
├── :Milestone (4 domains × 9 milestones = 36 nodes)
├── :ExitCriteria (36+, with level variants)
├── :HardwareRequirement (per milestone, ~60 nodes)
├── :Board (~20 common boards)
├── :Peripheral (~15 types)
├── :Concept (~80 nodes — I2C, SPI, CAN, UART, DMA, watchdog, FreeRTOS task, mutex...)
├── :Fact (~300 nodes — sourced from datasheets and specs)
├── :CommonMistake (~40 nodes)
├── :Register (~200 nodes — key registers for STM32F4, STM32G0, ESP32, AVR)
└── :Standard (8 nodes — IEC 62304, MISRA-C, ISO 26262, IEC 60601-1, Modbus RTU...)

Student Graph (written each session)
├── :Student (one per student)
├── :Goal (active + archived)
├── :StudentMilestone (one per milestone attempted)
├── :Assignment (all assignments ever given)
├── :AssignmentComponent (outcome, constraint, hint_threshold, stretch per assignment)
├── :Session (one per session)
├── :SessionEntry (covered, signals, next_focus per session)
├── :SkillConfirmed (what they've demonstrated)
└── :MentorNote (mentor observations)
```

---

## Integration with EmbeddedGuru Skill

SKILL.md is updated to: **query before generating**. Every time the skill would previously say something about protocols, hardware, or student state, it queries the graph first and grounds its output in graph facts.

### Grounding rules in SKILL.md

1. **Student state** → always query, never infer from context
2. **Protocol explanations** → query Concept + Fact nodes, cite source
3. **Hardware checks** → query Board → Peripheral before assigning a milestone
4. **Register names** → query Register nodes, never generate from memory
5. **Exit criteria checks** → query ExitCriteria node, apply `requires_artifact` flag
6. **Board recommendation** → query Board → Domain + Level, return top 2 by price

### Data that still touches markdown (exports only)

Human-readable exports can be generated from graph queries for student review — but the graph is authoritative. If the student edits the markdown export, those edits are ignored unless explicitly synced back via a write operation.

---

## Implementation Phases

| Phase | What | Dependencies |
|---|---|---|
| 1 | Schema definition (this document) | — |
| 2 | Curriculum seed data — Concepts, Facts, CommonMistakes, Boards, Peripherals | Graphify skill installed |
| 3 | Registers seed data — key registers for STM32F4, ESP32, AVR | Phase 2 |
| 4 | SKILL.md updated — query patterns replace markdown reads | Phase 2 |
| 5 | Write patterns — session end, milestone completion, assignment update | Phase 4 |
| 6 | `embeddedguru install` seeds the graph | Phase 2 + 3 |
