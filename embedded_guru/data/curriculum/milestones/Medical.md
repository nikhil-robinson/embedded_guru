# Medical Track — Milestones

## Milestone 0: Datasheet Literacy (Universal Gate)

Same as IoT track. Register-level peripheral code required. No HAL shortcuts until M0 is demonstrated.

---

## Milestone 1: GPIO and Clock Tree

Same as IoT track M1. Timer-interrupt blink, debounced button, no delay(), no HAL.

---

## Milestone 2: UART and ADC Signal Acquisition

**Goal:** Sample an analog signal (simulated biosignal: ECG, temperature, SpO₂) using the MCU ADC and stream data over UART.

**Prerequisites:** M1

**Exit criteria:**
1. ADC initialized in continuous or scan mode, DMA used to fill sample buffer
2. Correct sampling rate configured via timer trigger (not free-running) — student calculates and verifies sample rate
3. Student explains Nyquist: for a 100 Hz ECG signal, why must the sample rate be ≥ 200 Hz?
4. Anti-aliasing consideration: student explains what happens to frequencies above sample_rate/2 if no hardware filter is present
5. Data streamed over UART at correct rate, not dropped

---

## Milestone 3: Sensor Interface — I2C or SPI (Biomedical)

**Goal:** Interface a medical-class sensor (MAX30102 SpO₂, DS18B20 temperature, or similar) at register level.

**Prerequisites:** M2

**Exit criteria:** Same as IoT M3 but with additional:
- Student explains sensor accuracy spec from datasheet (tolerance, ±% at body temperature range)
- Calibration procedure documented if applicable
- Signal conditioning or moving average filter applied to reduce noise — student explains filter tradeoff (smoothing vs latency)

---

## Milestone 4: Watchdog and Fault Handling

**Goal:** Implement IWDG with correct architecture. System resets cleanly on any hang and logs the reset reason.

**Prerequisites:** M3

**Critical note:** In the medical track, watchdog is a milestone, not an afterthought. IEC 62304 requires fault detection. The watchdog must be in place before any patient-safety-relevant feature is added.

**Exit criteria:**
1. IWDG initialized and kicked only from main loop (not from ISR, not from every sub-loop)
2. RCC_CSR checked at boot — reset reason logged ("IWDG reset" vs "Power-on reset" etc.)
3. Student can demonstrate: if main loop blocks (simulate by inserting `while(1){}` after kick), system resets within the watchdog timeout period
4. Timeout period is documented with rationale: "Maximum tolerable patient data gap is X seconds, so watchdog timeout is X/2 seconds"
5. No `malloc()` in the firmware — student explains IEC 62304 / MISRA-C prohibition on dynamic memory

---

## Milestone 5: Data Logging with Integrity Check

**Goal:** Log patient data to flash or SD card with integrity checks. Survive power loss mid-write.

**Prerequisites:** M4

**Exit criteria:**
1. CRC (CRC32 or CRC16-CCITT) computed over each log record before writing
2. CRC verified on read — corrupted records detected and flagged (not silently used)
3. Power-loss resilience: atomic writes using write-then-verify pattern, or dual-record scheme
4. Student explains what happens to the log if power is cut during a write and how their design handles it
5. Log includes: timestamp (RTC-backed), sensor values, CRC, reset reason since last boot

---

## Milestone 6: Alarm and Alert System

**Goal:** Implement threshold-based alarms with debounce, escalation, and silence timeout.

**Prerequisites:** M5

**Exit criteria:**
1. Alarm activates when signal exceeds threshold for ≥ N consecutive samples (debounce prevents false triggers from noise)
2. Alarm latches — cannot be silenced by signal returning to normal (requires explicit operator acknowledgment or timeout)
3. Alarm escalation: warning → critical at configurable escalation time
4. Silence timeout: if operator silences alarm, it re-activates after a defined period if condition persists
5. Student can cite IEC 60601-1-8 as the standard governing medical alarms (does not need to have read the full standard — awareness of its existence is sufficient)

---

## Milestone 7: IEC 62304 / Safety Awareness Audit

**Goal:** Apply basic software lifecycle awareness to the firmware written in M0–M6.

**Prerequisites:** M6

**Note:** This milestone is not about passing a certification — it is about understanding what production medical software requires.

**Exit criteria:**
1. Student identifies which software safety class their device falls into (Class A: no injury possible, Class B: non-serious injury possible, Class C: serious injury possible) and explains the reasoning
2. Student lists what IEC 62304 requires for Class B software development (software development plan, requirements, architecture, unit testing, integration testing — not necessarily all implemented, but known)
3. Student identifies ≥3 places in their own firmware where they violated a MISRA-C or IEC 62304 requirement and documents the risk (not the fix — awareness of the gap is the exit criterion)
4. Student explains why `volatile` is required for variables shared between ISRs and main code

---

## Track graduation criteria

- M0–M6 exits met
- A complete patient monitoring prototype: samples signal, alarms on threshold, logs data with integrity
- No dynamic memory allocation in the application loop
- IWDG armed and configured correctly
- Student has read: IEC 62304 scope and software class definitions (freely available in summaries; full standard is not required)
