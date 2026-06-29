# Embedded Standards Reference

## MISRA-C 2012

**What it is:** A set of C coding guidelines for safety-critical embedded software. Developed by the Motor Industry Software Reliability Association. Originally for automotive, now used in medical, aerospace, and industrial.

**Who uses it:** Automotive (required in ISO 26262), medical (referenced in IEC 62304), industrial, aerospace.

**Key rules relevant to embedded firmware:**

| Rule | Category | What it says |
|---|---|---|
| Rule 1.3 | Required | No undefined behavior |
| Rule 2.1 | Required | All statements reachable |
| Rule 8.4 | Required | Compatible declaration in header for every function with external linkage |
| Rule 10.1 | Required | Operands of operator must be of appropriate essential type |
| Rule 14.4 | Required | Controlling expression of if/while must be essentially Boolean |
| Rule 15.5 | Advisory | Function must have single exit point |
| Rule 17.7 | Required | Return value of non-void function must be used |
| Rule 18.4 | Advisory | No pointer arithmetic except [] |
| Rule 21.3 | Required | No malloc/free/realloc/calloc (dynamic memory prohibited) |
| Rule 21.6 | Required | No printf/scanf from <stdio.h> in safety-critical application code |

**Tooling:** PC-lint Plus, LDRA, Polyspace, SonarQube (embedded), cppcheck (partial).

**For EmbeddedGuru purposes:** Students don't need to memorize rules. They need to understand: (1) why dynamic memory is prohibited, (2) why undefined behavior matters in embedded (compiler may eliminate safety-critical checks), (3) why function return values must be checked (unchecked error codes are a common embedded bug class).

---

## ISO 26262 — Automotive Functional Safety

**What it is:** Functional safety standard for road vehicles. Covers the entire development lifecycle from concept to production. Defines ASIL (Automotive Safety Integrity Level) from ASIL A (lowest) to ASIL D (highest).

**ASIL levels:**
- ASIL A: Low probability of occurrence, low severity (e.g., seat adjustment motor)
- ASIL B: (e.g., engine management)
- ASIL C: (e.g., ABS, airbag deployment)
- ASIL D: Highest — high probability + severe/fatal injury risk (e.g., steering, braking)

**Software requirements by ASIL:**
- ASIL A/B: Software unit testing, code coverage (statement), MISRA-C
- ASIL C: + branch coverage, software integration testing, semi-formal methods
- ASIL D: + MC/DC coverage, formal verification, hardware/software independence, fault injection testing

**Relevance to students:** CAN-based automotive features (braking, steering, powertrain) have ASIL requirements. Understanding that "CAN message missed" at ASIL D requires diagnostic coverage, not just a retry.

---

## IEC 62304 — Medical Device Software

**What it is:** International standard for medical device software lifecycle processes. Defines software safety classes.

**Software safety classes:**
- Class A: No injury possible if software fails (e.g., hospital administration app)
- Class B: Possible non-serious injury (e.g., a device that tracks and displays non-critical data)
- Class C: Possible serious injury or death (e.g., infusion pump, ventilator, cardiac monitor)

**Requirements by class (key items):**
| Activity | Class A | Class B | Class C |
|---|---|---|---|
| Software development plan | Required | Required | Required |
| Software requirements | Required | Required | Required |
| Software architecture | — | Required | Required |
| Unit testing | — | Required | Required |
| Integration testing | — | Required | Required |
| System testing | Required | Required | Required |
| Traceability requirements ↔ tests | — | Required | Required |
| Code coverage for unit tests | — | — | Required (MC/DC for critical paths) |

**For EmbeddedGuru purposes:** Students need to know: (1) Class A/B/C classification for their device, (2) that MISRA-C and watchdog are not optional for Class B/C, (3) that dynamic memory allocation is explicitly a risk factor, (4) that documentation (requirements, test results) is a deliverable, not optional.

---

## IEC 60601-1 — Medical Electrical Equipment

**What it is:** Safety standard for medical electrical equipment. Part 1 covers basic safety and essential performance. Subsections cover specific requirements.

**IEC 60601-1-8:** Alarm systems for medical electrical equipment. Governs medical alarms.

**Key alarm requirements from IEC 60601-1-8:**
- Alarms must have visual + auditory indicators for clinical settings
- Alarm priority: HIGH (life-threatening), MEDIUM (prompt action), LOW (awareness)
- Alarms cannot be permanently disabled
- Alarm silence is time-limited (must re-activate if condition persists)
- Alarm conditions must be distinguishable from each other

---

## IEC 61508 — Industrial Functional Safety

**What it is:** Generic functional safety standard for electrical/electronic/programmable systems. Parent standard from which ISO 26262 and IEC 62304 are derived.

**SIL — Safety Integrity Level:** SIL 1 to SIL 4.
- SIL 1: Probability of failure on demand (PFD) 10⁻¹ to 10⁻²
- SIL 4: PFD 10⁻⁴ to 10⁻⁵ (rare in software; usually hardware + redundancy)

**Relevance to students:** Industrial RTOS track — industrial machinery may require SIL 2 for safety functions. Watchdog, redundancy, and diagnostic coverage requirements derive from this standard.

---

## Communication Protocol Standards

| Standard | Protocol | Key fact |
|---|---|---|
| ISO 11898-1 | CAN physical layer | Defines differential signaling, 120Ω termination, bit timing |
| ISO 11898-2 | CAN high-speed (up to 1 Mbit/s) | Most common CAN physical layer standard |
| ISO 15765-2 | ISO-TP / CAN transport layer | Defines segmentation for CAN payloads > 8 bytes |
| ISO 14229 | UDS (Unified Diagnostic Services) | Defines OBD-II diagnostic services (0x10, 0x22, 0x2E, etc.) |
| J1979 | OBD-II PIDs | Defines Mode 01 PIDs (0x0C RPM, 0x0D speed, 0x05 coolant, etc.) |
| Modbus RTU | Serial industrial | CRC-16, device address, function codes 0x01–0x10 |
| I2C (UM10204) | NXP specification | Defines START/STOP, clock speeds (100k/400k/1M/3.4M), pull-up requirements |
| SPI | No formal standard | De facto standard: CPOL/CPHA modes 0–3 |

---

## Volatile in embedded C

`volatile` tells the compiler not to optimize away accesses to a variable. Required for:
- Variables modified in an ISR and read in main code (or vice versa)
- Memory-mapped peripheral registers
- Variables shared between threads (note: volatile alone does NOT provide atomicity — use synchronization primitives for that)

Absence of `volatile` on ISR-shared variables allows the compiler to keep the value in a register, never re-reading from memory. The main loop will never see ISR updates. This is defined behavior for the compiler and undefined behavior for the programmer.

MISRA-C Rule 8.6 (advisory): All variables shared between ISRs and non-ISR code must be declared `volatile`.
