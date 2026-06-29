# Industrial/RTOS Track — Milestones

## Milestone 0: Datasheet Literacy (Universal Gate)

Same as IoT track. Register-level peripheral code required before any RTOS work begins.

---

## Milestone 1: GPIO and Clock Tree

Same as IoT track M1. Timer-interrupt blink, debounced button, no delay(), no HAL.

---

## Milestone 2: UART and Interrupt-Driven I/O

Same as IoT track M2. Interrupt-driven receive with ring buffer, ORE handled, BRR calculation verified.

---

## Milestone 3: FreeRTOS Basics — Tasks and Queues

**Goal:** Migrate a bare-metal superloop to a multi-task FreeRTOS application.

**Prerequisites:** M2

**Exit criteria:**
1. At least 3 tasks: sensor_task (reads sensor), processing_task (filters data), output_task (drives actuator or UART)
2. Data passed between tasks via queues — no global variables shared between tasks
3. Task priorities assigned with rationale: student explains which tasks must be higher priority and why
4. `vTaskDelay(pdMS_TO_TICKS(N))` used correctly — not `vTaskDelay(N)` with wrong unit assumption
5. Stack overflow detection enabled: `configCHECK_FOR_STACK_OVERFLOW = 2`, hook implemented
6. `xPortGetFreeHeapSize()` called at startup and logged — student explains what the number means

**Probe:** Ask "what happens if processing_task blocks on a mutex and sensor_task is preempted — does data get lost?" Student should explain queue depth as the buffer, and what happens when the queue fills.

---

## Milestone 4: Mutexes, Semaphores, and Shared Peripherals

**Goal:** Correctly protect a shared peripheral (UART, SPI bus) accessed from multiple tasks.

**Prerequisites:** M3

**Exit criteria:**
1. UART logging protected by a mutex — two tasks can log without interleaved output
2. Student correctly uses `xSemaphoreGive/TakeFromISR()` (not `xSemaphoreGive/Take()`) in ISR context
3. `portYIELD_FROM_ISR(higher_prio_woken)` called after ISR-side semaphore give
4. Student explains: what is priority inversion, what is priority inheritance, why FreeRTOS mutex (not binary semaphore) protects against it
5. No blocking calls inside timer callbacks — student identifies and corrects any such patterns

---

## Milestone 5: DMA and High-Throughput I/O

**Goal:** Implement DMA-based ADC sampling or SPI communication integrated with FreeRTOS task notification.

**Prerequisites:** M4

**Exit criteria:**
1. DMA transfer complete interrupt triggers a FreeRTOS task notification (not a semaphore) using `vTaskNotifyGiveFromISR()`
2. Receiving task calls `ulTaskNotifyTake()` to block until DMA completes
3. Student verifies DMA request mapping against reference manual (correct stream + channel for the peripheral)
4. Interrupt flags cleared before re-enabling DMA stream
5. On STM32H7 or F7 with D-cache: `SCB_CleanDCache_by_Addr()` called before DMA transmit and `SCB_InvalidateDCache_by_Addr()` called after receive — or student documents why cache invalidation is not needed for their specific MCU

---

## Milestone 6: Watchdog with Multi-Task Health Monitoring

**Goal:** Implement IWDG with a supervisor task that monitors health of all application tasks.

**Prerequisites:** M5

**This is a required milestone in the industrial track.** Industrial equipment must recover from software faults without human intervention. A machine that freezes during production causes line stoppages.

**Exit criteria:**
1. IWDG initialized with timeout proportional to worst-case task cycle time × safety margin
2. A `watchdog_supervisor_task` runs at highest priority, periodically checks task heartbeat flags from each application task
3. Only the supervisor task kicks the IWDG — never application tasks, never ISRs
4. Each application task sets its own heartbeat flag within each cycle
5. Supervisor detects if any task has missed its heartbeat flag in the last N supervisor cycles and logs the fault before allowing IWDG reset
6. Student demonstrates: if one task is artificially hung, the system resets within 2× watchdog timeout

---

## Milestone 7: Modbus RTU or Industrial Protocol

**Goal:** Implement Modbus RTU master or slave over RS-485.

**Prerequisites:** M6

**Exit criteria:**
1. RS-485 half-duplex driver enable (DE/RE pins) correctly managed: assert before first byte, deassert after last byte physically leaves wire (wait for UART TC, not TXE)
2. Modbus RTU frame constructed correctly: device address, function code, data, CRC-16 (polynomial 0xA001, LSB first)
3. Inter-frame silence (3.5 character times at the configured baud rate) detected for frame delineation
4. Function codes 0x03 (Read Holding Registers) and 0x06 (Write Single Register) implemented
5. Student explains what a Modbus exception response is and handles NACKs
6. CRC verified on receive — frames with bad CRC silently discarded (not acted upon)

---

## Milestone 8: System Integration and Fault Recovery

**Goal:** The complete application runs for 72 hours without hang, recovers from induced faults.

**Prerequisites:** M7

**Exit criteria:**
1. 72-hour soak test run (or documented stress test at accelerated rate if time-constrained)
2. Induced faults tested and documented: sensor disconnection, Modbus master timeout, DMA error, task stack overflow
3. System recovers from each induced fault within documented time (no indefinite hang)
4. Fault log persisted to non-volatile memory with fault type, timestamp, and task that triggered the reset
5. Student documents the worst-case task execution time (WCET) for their highest-priority task

---

## Track graduation criteria

- M0–M7 exits met (M8 is strongly recommended but may be deferred for student with hard deadline)
- Multi-task FreeRTOS application with: sensor input, processing, output, logging, watchdog supervisor, Modbus or other industrial protocol
- No global variables shared between tasks without synchronization
- No blocking calls in ISRs or timer callbacks
- Stack overflow detection enabled in development build
- Student can explain FreeRTOS scheduler preemption, priority inheritance, and queue behavior under load
