# Common Embedded Firmware Mistakes

## Hardware mistakes

### I2C — 1-ohm pull-up resistor
**Mistake:** Using 1 Ω (or any very low resistance) as pull-up resistors on SDA/SCL to make the signal "stronger" or "faster."  
**Why wrong:** I2C is open-drain. The pull-up resistor is the only path to logic HIGH. Current = VCC / R. At 3.3V and 1 Ω: 3.3 A. STM32 GPIO max sink current is 25 mA. This is 130× over spec. Consequences: excessive current draw, GPIO damage risk, bus contention when open-drain transistor fights the resistor, line may never reach valid HIGH logic level.  
**Correct:** 2.2 kΩ–10 kΩ at 3.3V/100kHz. 4.7 kΩ is the standard starting point. Pull-up value is derived from I2C spec rise time constraint: R ≤ t_rise / C_bus.

### CAN bus — no termination resistor
**Mistake:** Wiring CAN_H and CAN_L between nodes without 120 Ω termination resistors at each physical end.  
**Why wrong:** CAN is a transmission line. Without termination, signal reflections corrupt frames. Works at short bench distances by coincidence. Fails in vehicles or with cables > 1m.  
**Correct:** 120 Ω between CAN_H and CAN_L at each of the two physical ends of the bus.

### CAN bus — no transceiver
**Mistake:** Connecting MCU CANTX/CANRX pins directly to CAN bus wires.  
**Why wrong:** MCU outputs digital signals (0V/3.3V single-ended). CAN bus is differential (CAN_H ≈ 3.5V, CAN_L ≈ 1.5V on dominant). The MCU cannot drive the differential signal and cannot decode it. Will not communicate and may damage devices.  
**Correct:** Use CAN transceiver between MCU and bus. SN65HVD230 for 3.3V MCUs. MCP2551 for 5V systems.

### SDA/SCL swapped
**Mistake:** Connecting SDA to the SCL pin and vice versa.  
**Why wrong:** Will not communicate. The bus may appear stuck (BUSY flag). No error message — the peripheral just produces no output.  
**Debugging:** Check wiring against MCU datasheet pinout AND sensor datasheet. Use oscilloscope or logic analyzer — SCL should show a clock pattern; SDA should show data transitions.

---

## Firmware mistakes

### malloc in safety-critical or long-running firmware
**Mistake:** Using malloc()/free() in embedded firmware, justifying it with "we always free properly."  
**Why wrong:** Heap fragmentation is a time-dependent failure mode. A fresh firmware image may run for hours on a bench. After days of allocating and freeing varying sizes, heap becomes fragmented — a valid allocation fails despite total free memory appearing sufficient. In safety-critical systems, this failure mode is non-deterministic and untestable on a bench.  
**Correct:** Static allocation. Size all buffers at compile time. MISRA-C 2012 Rule 21.3 prohibits dynamic memory functions in safety-critical code. For Medical domain: IEC 62304 compliance requires deterministic behavior — dynamic allocation is a known non-deterministic failure mode.  
**Exception:** Bare initialization code before RTOS start, or non-critical features like logging, may use dynamic allocation if the system is not safety-critical and the allocation happens once (no free).

### No watchdog in a medical device
**Mistake:** Omitting watchdog because "the processor is reliable" or "our device isn't life-critical."  
**Why wrong:** A patient monitor displaying stale temperature data because the main loop stalled IS a patient safety risk. A missed fever or missed hypothermia from frozen data can lead to incorrect clinical decisions. IEC 62304 and IEC 60601-1 safety standards require watchdog or equivalent fault detection for medical devices. A processor that never glitches on a bench will glitch at 3am in a hospital from an unexpected EMI event or a software bug triggered by an unusual input sequence.  
**Correct:** Always arm the watchdog. Feed it only on the correct path through the main loop (never unconditionally, never from an ISR that runs regardless of the main loop state). STM32 IWDG (Independent Watchdog, LSI clock) is the correct choice — it runs even if the main system clock fails, which WWDG cannot guarantee.

### Polling before peripheral ready
**Mistake:** Reading a peripheral register immediately after configuring it, without checking the ready/busy status.  
**Why wrong:** Peripherals have startup times. Reading ADC before conversion complete, reading I2C data before BTF is set, or checking UART TX before TXE is set will return stale or incorrect data. No assertion failure — silent data corruption.  
**Correct:** Always check the relevant status bit (TXE, RXNE, BTF, EOC, BUSY) before accessing data. Use timeout loops in production code — polling forever will hang the system if hardware fails.

### Enabling peripheral before clock
**Mistake:** Writing to peripheral registers (I2C_CR1, SPI_CR1, etc.) before enabling the peripheral clock in the RCC register.  
**Why wrong:** Peripheral registers are not accessible before the clock is enabled. Write is silently ignored. Register reads back 0. Peripheral never initializes. This is the most common cause of "my peripheral setup code doesn't work" on STM32.  
**Correct:** First enable the peripheral clock (e.g. RCC_APB1ENR bit for I2C1), then configure the peripheral. Always. Without exception.

### Kicking watchdog from an ISR
**Mistake:** Refreshing the watchdog timer from a periodic interrupt service routine (ISR), rather than from the main application loop.  
**Why wrong:** An ISR will fire even if the main application loop is completely stuck (infinite loop, deadlock, stack overflow hang). Feeding the watchdog from an ISR means a completely hung main loop still refreshes the watchdog — the whole point of the watchdog (detecting main loop stalls) is defeated.  
**Correct:** Feed the watchdog only from the main application loop, at the natural end of each full processing cycle. If using FreeRTOS, use the task watchdog (esp_task_wdt on ESP32, or a dedicated watchdog task on STM32 FreeRTOS) that monitors task execution, not a plain ISR.

### Using delay() anywhere in embedded firmware
**Mistake:** Using `delay()`, `HAL_Delay()`, `vTaskDelay()` for timing-critical operations (PWM, sensor sampling intervals, communication timing).  
**Why wrong:** Software delays block the CPU. During a delay, the CPU cannot service interrupts (in the case of bare delay loops), cannot run other tasks (RTOS), and cannot handle time-critical events. Delay-based code is also inaccurate — interrupt latency changes the actual delay duration.  
**Correct:** Use hardware timers with interrupts or callbacks for timing. Configure a timer ISR to fire at the required rate. Use RTOS tick + task sleep for periodic tasks. Never use delay() for real-time requirements.

### SPI — CS not asserted before transfer
**Mistake:** Starting SPI data transfer without asserting the chip select (CS/NSS) pin for the target device first.  
**Why wrong:** CS selects which slave device responds. Without CS asserted, the slave will not clock in data or respond. On some devices, a partial CS assertion at the wrong time corrupts the internal state machine.  
**Correct:** Assert CS (drive LOW for active-low), complete the full transaction (multiple bytes if needed), then deassert CS. Use hardware NSS management carefully — software NSS is clearer for most use cases.

### CAN — software filtering instead of hardware acceptance filters
**Mistake:** Receiving all CAN frames and discarding unwanted IDs in software.  
**Why wrong:** At high bus load (heavy vehicle CAN, 1000+ frames/second), the CPU spends constant cycles reading and discarding frames. Interrupt latency increases, other tasks are starved. The hardware acceptance filter runs in the CAN controller before the CPU is involved — only matching IDs reach the FIFO and trigger an interrupt.  
**Correct:** Configure bxCAN hardware filters (CAN_FxR1/FxR2, FA1R, FM1R, FS1R) to pass only the IDs the application cares about.

---

## Assessment signals

**When a student says "I use Arduino" — probe:**  
"Have you ever configured a peripheral from registers in the ATmega328P datasheet, without using the Arduino library?"  
A student who only used `Wire.begin()` and `Wire.read()` has not done register-level I2C. This does not mean they cannot learn — it means they are L1, not L2.

**When a student says "I've written C for embedded" — probe:**  
"Tell me about an ISR you've written. What caused the interrupt, and how did you clear the interrupt flag?"  
A student who has written C for PC or coursework but never dealt with ISRs, peripheral registers, or hardware timing is L1 for embedded purposes even with years of C experience.

**When a student says "CAN is like I2C" or "CAN uses pull-up resistors" — correct immediately:**  
CAN is differential, I2C is single-ended open-drain. CAN uses 120 Ω termination, I2C uses 4.7 kΩ pull-ups. CAN has no master, I2C has a master. These are fundamentally different protocols with different electrical characteristics.
