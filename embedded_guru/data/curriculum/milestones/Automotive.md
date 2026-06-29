# Automotive/CAN Track — Milestones

## Milestone 0: Datasheet Literacy (Universal Gate)

Same as IoT track. See IoT.md M0 definition. Students must produce register-level peripheral code before any CAN work begins.

---

## Milestone 1: GPIO and Clock Tree

Same as IoT track M1. LED blink via timer interrupt, button with debounce, no delay(), no HAL.

---

## Milestone 2: UART Logging Setup

**Goal:** Reliable UART debugging channel before touching CAN.

CAN debugging is impossible without a reliable way to print state. Student must have interrupt-driven UART TX before starting CAN work.

**Exit criteria:** Same as IoT M2 but emphasis on: printf-style logging to serial terminal works reliably under interrupt load. No character drops at 115200 baud when CAN ISR fires.

---

## Milestone 3: CAN Physical Layer Understanding

**Goal:** Correctly wire a CAN bus segment on a bench with transceiver and termination.

**Prerequisites:** M0 (datasheet literacy), M2 (UART debug channel working)

**Exit criteria:**
1. Transceiver (SN65HVD230 for 3.3V MCU) wired correctly: MCU CANTX → TXD pin, CANRX ← RXD pin, power and ground
2. 120 Ω termination resistor present between CAN_H and CAN_L at each physical end of the bus
3. Student can explain on oscilloscope: what the dominant and recessive states look like (CAN_H ≈ 3.5V, CAN_L ≈ 1.5V for dominant)
4. Student explains what happens without termination: signal reflections at frequencies ≥ what bus length/cable speed limits
5. Two-node loopback test passes (send from MCU, receive back, verify ID and data byte match)

**Critical probe:** Ask "do you have termination resistors?" before accepting any CAN milestone. An unterminated bench setup works by coincidence at short distances. It is not a valid embedded engineering practice.

---

## Milestone 4: bxCAN Transmit and Receive

**Goal:** Transmit a CAN frame and receive a response using STM32 bxCAN in loopback mode, then over a real bus.

**Prerequisites:** M3

**Exit criteria:**
1. bxCAN initialized: CAN_MCR initialization sequence (INRQ, SLEEP bits), baud rate prescaler calculated for target bit rate (e.g., 500 kbit/s)
2. Time quanta breakdown documented: prescaler, BS1, BS2, SJW — student can explain why they chose each value
3. Hardware acceptance filter configured (not receive-all): CAN_FxR1, FA1R, FM1R, FS1R registers set correctly for one specific ID
4. Transmit a standard frame (11-bit ID) and receive it back in loopback mode
5. Transmit and receive over actual two-node bus with transceiver (not just loopback)
6. Student can read CAN_ESR (error status register) and explain what TEC and REC counters indicate

**Baud rate probe:** Ask them to show the baud rate calculation. Acceptable answer: "I set prescaler=X, BS1=Y, BS2=Z. With APB1 at 42MHz, this gives: 42MHz / (prescaler × (1 + BS1 + BS2)) = 500kbit/s." If they say "I copied values from a tutorial," M4 is not passed.

---

## Milestone 5: OBD-II / Vehicle Data Logging

**Goal:** Log real vehicle data using OBD-II PIDs over CAN.

**Prerequisites:** M4

**Exit criteria:**
1. OBD-II request frame correctly constructed: ID 0x7DF, DLC 8, data [0x02, 0x01, PID, 0x00×5]
2. Response frame parsed: ID 0x7E8, data[3] is the value byte for Mode 1 single-byte PIDs
3. At least 3 PIDs logged: RPM (0x0C), speed (0x0D), coolant temp (0x05)
4. RPM conversion applied: raw value / 4 = RPM
5. Data logged to SD card or sent over UART with timestamp
6. Student explains what happens when the vehicle ECU does not support a requested PID (no response → timeout handling required)

---

## Milestone 6: DBC File and Signal Decoding

**Goal:** Parse proprietary CAN signals using a DBC file.

**Prerequisites:** M5

**Exit criteria:**
1. Student can read a DBC file format entry and extract: message ID, signal name, start bit, length, scale, offset, unit
2. Implementation extracts at least one signal from a raw CAN frame using the DBC definitions
3. Student explains bit ordering (Motorola/big-endian vs Intel/little-endian in DBC) and verifies their extraction against known good data
4. (Optional stretch) Outputs decoded signals in CSV or JSON for offline analysis

---

## Milestone 7: UDS Diagnostic Session

**Goal:** Communicate with an ECU using ISO 14229 UDS protocol.

**Prerequisites:** M6

**Exit criteria:**
1. UDS service 0x10 (DiagnosticSessionControl) sent and response parsed
2. UDS service 0x22 (ReadDataByIdentifier) with a known DID returns expected data
3. Student can explain: what a negative response code (NRC) means and handle NRC 0x78 (requestCorrectlyReceived-ResponsePending)
4. ISO-TP (ISO 15765-2) segmentation implemented for multi-frame messages (single frame vs first frame vs consecutive frame)

---

## Track graduation criteria

- M0–M6 exits met
- A complete CAN application: reads vehicle data (real or simulated), decodes signals, logs to storage
- Student can explain CAN bus arbitration (CSMA/CA, bitwise dominance, lower ID wins)
- Student has read and can cite: bxCAN chapter in STM32 reference manual, ISO 11898-1 physical layer basics (does not need the full standard, but the key electrical specs)
