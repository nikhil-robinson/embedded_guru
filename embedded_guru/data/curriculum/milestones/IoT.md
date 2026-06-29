# IoT Track — Milestones

## Milestone 0: Datasheet Literacy (Universal Gate)

**Goal:** Read a datasheet and configure a peripheral from it without guidance.

**Exit criteria (all required):**
1. Student loads the correct peripheral's register description from the reference manual (not library docs)
2. Student configures at least one peripheral (GPIO, UART, SPI, or I2C) from scratch using register names from the datasheet
3. Student can explain why each bit they set is set (no cargo-cult register values)
4. Student produces a wiring diagram or pinout annotation referencing the actual pin names from the hardware manual

**M0 cannot be skipped.** An L3 student may demonstrate M0 verbally in session 1 but still needs to submit code artifact with test output.

---

## Milestone 1: GPIO and Clock Tree

**Goal:** Blink an LED and control a button without any HAL library. Understand the RCC clock tree.

**Prerequisites:** M0

**Exit criteria:**
1. LED blinks at a deterministic rate using a hardware timer interrupt (not delay())
2. Button press detected with software debounce (not `if (GPIO_IDR & PIN) {return;}`)
3. Student can explain: (a) what RCC_AHB1ENR bit does, (b) why the GPIO won't toggle before that bit is set, (c) what MODER register does
4. Code compiles without HAL includes (bare register access only)

**Common L1 trap:** Using `HAL_GPIO_TogglePin()` and claiming milestone. Verify: read their code, ask them to point to the register write that sets the output.

---

## Milestone 2: UART Communication

**Goal:** Send structured data over UART from MCU to host computer.

**Prerequisites:** M1

**Exit criteria:**
1. UART configured at correct baud rate for the clock source (student verifies BRR calculation)
2. Interrupt-driven receive with ring buffer — not polling-only
3. ORE (overrun) and FE (framing error) handled (even if only logged)
4. Student can explain what happens if TXE is not checked before writing DR
5. Data from a sensor (or simulated sensor value) printed to terminal with timestamp

**Common mistake to probe:** Ask "what is the baud rate of your UART and how did you calculate BRR?" If they say "I copied the value from a tutorial," they have not met the exit criterion.

---

## Milestone 3: I2C Sensor Integration

**Goal:** Read a real sensor (temperature, humidity, IMU, etc.) over I2C using register-level driver.

**Prerequisites:** M2

**Exit criteria:**
1. I2C initialized with correct pull-up resistors (student verifies on oscilloscope or logic analyzer — or can calculate the correct value)
2. Sensor read sequence implemented from sensor datasheet (not from a library): START → address → register → repeated START → data → STOP
3. BTF (byte transfer finished) and ADDR flags checked correctly
4. Student can explain what a repeated START is and why it is different from STOP+START for this sensor
5. Raw register value converted to calibrated output (e.g., raw ADC → °C using sensor's conversion formula)

---

## Milestone 4: SPI Display or High-Speed Peripheral

**Goal:** Drive a display (SSD1306, ILI9341) or high-speed sensor (IMU, ADC) over SPI.

**Prerequisites:** M3

**Exit criteria:**
1. SPI mode (CPOL/CPHA) verified against peripheral datasheet
2. CS pin explicitly asserted before and deasserted after complete transaction (not per-byte)
3. DMA or interrupt-driven transfer for large data blocks (not polling per byte for display updates)
4. Student can explain: what happens if CS is deasserted mid-transaction for this specific peripheral

---

## Milestone 5: MQTT/WiFi Cloud Publishing (IoT-specific)

**Goal:** Publish sensor data to an MQTT broker or cloud endpoint over WiFi.

**Prerequisites:** M4 (or M3 with a WiFi-capable board like ESP32)

**Exit criteria:**
1. WiFi connected and reconnected automatically on disconnect
2. MQTT topic hierarchy makes sense for the use case (not just `/test`)
3. Data published at controlled interval — not as fast as possible (rate limiting, no busy loop)
4. JSON or structured payload (not raw ASCII number)
5. Student demonstrates reception of published data on a broker or dashboard

**Security check:** Ask: "Is the MQTT broker authenticated? Is the traffic encrypted (TLS)?" For a hobbyist project, answer can be "no, but I know the risk." For a production system, TLS and authentication are required.

---

## Milestone 6: OTA Firmware Update

**Goal:** Update MCU firmware over the air without physical access.

**Prerequisites:** M5

**Exit criteria:**
1. Bootloader partition or dual-bank flash scheme understood and documented
2. Firmware integrity check (CRC or SHA) before writing to flash
3. Rollback mechanism if new firmware fails to boot (verified by deliberately failing the boot)
4. Student documents the update protocol and what happens at each failure point

---

## Track graduation criteria

- All M0–M5 exits met
- A complete IoT device that reads ≥1 sensor, publishes over network, and has a documented failure mode (what happens when WiFi drops, when sensor reads fail)
- Student has read and can cite the relevant sections of the MCU reference manual without prompting
