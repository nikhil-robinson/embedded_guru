# CAN Bus — Controller Area Network

## What it is

CAN (Controller Area Network) is a differential serial protocol designed for vehicle ECU communication. Developed by Bosch in 1983. Governed by ISO 11898. Two-wire bus: CAN_H and CAN_L. No clock line. No master — all nodes are peers. Broadcast bus: every frame is received by every node.

**CAN is NOT like I2C.** Key differences:
- I2C uses pull-up lines (single-ended). CAN uses differential signaling (CAN_H and CAN_L as a pair).
- I2C has a master and addressed slaves. CAN has no master — any node can transmit.
- I2C has a clock line. CAN is asynchronous — uses bit stuffing for synchronization.
- I2C uses 4.7 kΩ pull-ups. CAN uses 120 Ω termination resistors (one at each end of the bus).
- I2C requires an ACK from the addressed device. CAN uses a distributed ACK from all receivers.

## Physical layer

**Differential signaling:** CAN_H − CAN_L voltage determines bit value.
- Dominant bit (logic 0): CAN_H ≈ 3.5V, CAN_L ≈ 1.5V → differential = 2V
- Recessive bit (logic 1): CAN_H = CAN_L ≈ 2.5V → differential ≈ 0V

**Termination:** 120 Ω resistors at each physical end of the bus. Without termination: signal reflections corrupt frames. Maximum bus length at 1 Mbit/s: ~40 meters.

**CAN transceiver required:** The MCU CAN controller (bxCAN on STM32) outputs digital CANTX/CANRX signals. These are NOT directly connected to the bus. A CAN transceiver converts digital signals to differential CAN_H/CAN_L and back.
- Common transceivers: SN65HVD230 (3.3V), MCP2551 (5V), TJA1050 (5V)
- SN65HVD230 is recommended for 3.3V MCUs (STM32, etc.) — no level shifter needed.

## Arbitration — how CAN handles multiple simultaneous transmissions

CAN uses CSMA/CA — Carrier Sense Multiple Access with Collision Avoidance.

**Bitwise arbitration:** When multiple nodes transmit simultaneously, they compare their transmitted bit to the actual bus state bit by bit. A dominant bit (0) overwrites a recessive bit (1) on the bus. A node transmitting a recessive bit that sees a dominant bit on the bus knows it has lost arbitration and stops transmitting immediately.

**Lower CAN ID wins:** Since a 0 bit dominates a 1 bit, the node transmitting the lower identifier wins arbitration automatically. No collision occurs — the losing node backs off silently and retries. The winning message is transmitted without interruption.

**This is NOT CSMA/CD (Ethernet):** Ethernet detects collisions and all transmitters stop and retry randomly. CAN resolves conflicts deterministically — the highest-priority message always wins with no data loss.

## Frame format (CAN 2.0A standard frame)

| Field | Bits | Description |
|---|---|---|
| SOF | 1 | Start of frame — dominant bit |
| Identifier | 11 | CAN ID (arbitration priority — lower = higher priority) |
| RTR | 1 | Remote Transmission Request (0 = data frame, 1 = remote frame) |
| IDE | 1 | Identifier Extension (0 = standard 11-bit) |
| r0 | 1 | Reserved |
| DLC | 4 | Data Length Code — 0 to 8 bytes |
| Data | 0–64 | Payload (0–8 bytes for CAN 2.0, up to 64 bytes for CAN FD) |
| CRC | 15+1 | Cyclic Redundancy Check + delimiter |
| ACK | 2 | ACK slot + delimiter (any receiver that received frame correctly pulls slot dominant) |
| EOF | 7 | End of frame — 7 recessive bits |

**Extended frame (CAN 2.0B):** Uses 29-bit identifier instead of 11-bit. IDE bit set to 1.

## OBD-II PIDs

OBD-II (On-Board Diagnostics) uses CAN at 500 kbit/s in modern vehicles.

Request frame: CAN ID 0x7DF (broadcast to all ECUs), DLC=8, data=[0x02, 0x01, PID, 0x00, 0x00, 0x00, 0x00, 0x00]
- Byte 0: 0x02 (2 additional bytes follow)
- Byte 1: 0x01 (service 01 — current data)
- Byte 2: PID number

Response: CAN ID 0x7E8 (from engine ECU), DLC=8, data=[0x04, 0x41, PID, A, B, ...]
- Byte 0: number of additional bytes
- Byte 1: 0x41 (0x40 + service 01)
- Byte 2: PID echoed
- Bytes 3+: data (formula depends on PID)

**Common OBD-II PIDs:**

| PID | Name | Formula | Units |
|---|---|---|---|
| 0x0C | Engine RPM | (256×A + B) / 4 | RPM |
| 0x0D | Vehicle speed | A | km/h |
| 0x11 | Throttle position | A × 100/255 | % |
| 0x05 | Coolant temperature | A − 40 | °C |
| 0x04 | Calculated engine load | A × 100/255 | % |
| 0x0F | Intake air temperature | A − 40 | °C |

## bxCAN on STM32F4 (base address 0x40006400)

**Mailboxes:** 3 transmit mailboxes, 2 receive FIFOs (FIFO0, FIFO1).

**Hardware acceptance filters:** 14 filter banks, each configurable as mask or list mode, 11-bit or 29-bit. Filters run in hardware before the CPU sees any frame — only matching IDs reach the FIFO. This is why software filtering is wrong for embedded CAN: software filter requires CPU to wake up, read the frame, check the ID, and discard — wastes CPU cycles and can cause missed frames at high bus load.

**Key initialization sequence:**
1. Enable CAN1 clock: RCC_APB1ENR bit 25
2. Enter initialization mode: CAN_MCR bit INRQ=1, wait for INAK=1 in CAN_MSR
3. Set bit timing: CAN_BTR register (prescaler + seg1 + seg2 + SJW)
4. Configure filters: CAN_FMR, CAN_FM1R, CAN_FS1R, CAN_FA1R, CAN_FxR1/FxR2
5. Exit initialization mode: CAN_MCR INRQ=0, wait for INAK=0

**Bit timing example for 500 kbit/s at 45 MHz APB1 clock:**
- Prescaler = 5, Seg1 = 8, Seg2 = 9, SJW = 1
- Bit time = (1+8+9) × (5/45MHz) = 18 × 111ns ≈ 2µs → 500 kbit/s

## DBC files

DBC (Database CAN) files describe the signal layout within CAN frames. Each signal has a name, start bit, length, factor, offset, and unit. Used with tools like CANdb++ (Vector), SavvyCAN, or python-can with cantools.

Example signal definition:
```
SG_ EngineSpeed : 16|16@1+ (0.25,0) [0|16383.75] "rpm" ECM
```
Means: signal EngineSpeed, starts at bit 16, 16 bits long, little-endian unsigned, factor=0.25, offset=0, range 0–16383.75 rpm, sent by ECM.

## UDS — Unified Diagnostic Services (ISO 14229)

UDS is a diagnostic protocol running over CAN (and other buses). Uses CAN IDs 0x7E0–0x7EF for request, 0x7E8–0x7EF for response (typical).

**Service 0x22 — ReadDataByIdentifier:** Request by 2-byte Data Identifier (DID). Response: 0x62 + DID + data.

Request: [0x03, 0x22, DID_high, DID_low]
Response: [length, 0x62, DID_high, DID_low, data...]

Negative response: [0x03, 0x7F, service_id, NRC] where NRC is the Negative Response Code (0x11 = serviceNotSupported, 0x31 = requestOutOfRange, etc.)

## Common mistakes

**No termination resistor:** Bus works at short distances on a bench but fails in a car or with longer cables. Always use 120 Ω at each end.

**Software filtering instead of hardware filters:** Do not read all frames and discard in software. Configure bxCAN hardware filters — only target IDs reach the FIFO.

**Wrong transceiver voltage:** Using MCP2551 (5V) directly with a 3.3V MCU without level shifting. Use SN65HVD230 for 3.3V systems.

**CANTX/CANRX without transceiver:** Connecting MCU CAN pins directly to the bus. The digital signal levels (0/3.3V) are not CAN bus levels (differential 0/2V). Will not work and may damage transceivers on the bus.

**Bit timing miscalculation:** Using wrong APB1 clock frequency for bit time calculation. Verify APB1 clock in SystemCoreClock / clock divider chain before calculating BTR register values.
