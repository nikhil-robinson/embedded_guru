# Watchdog Timers

## What they are

A watchdog timer is a hardware countdown timer. If the CPU fails to "kick" (refresh/feed) it before it expires, it resets the system. Purpose: detect and recover from software lockups, infinite loops, deadlocks, or stack overflows — anything that prevents normal execution.

## Two types on STM32

### IWDG — Independent Watchdog
- Clock source: internal LSI oscillator (~32 kHz, independent of main clock)
- Runs even if main system clock fails
- Once armed, cannot be disabled by software (only power cycle)
- Timeout range: ~0.1 ms to ~26 seconds (depending on prescaler and reload value)
- Reset is visible: IWDG flag in RCC_CSR

**IWDG is the correct watchdog for all production use.** Its independence from the main clock is what makes it reliable for the cases that matter — a software fault that kills the system clock still gets detected.

### WWDG — Window Watchdog
- Clock source: APB1 bus clock (same clock that can fail)
- Adds a "window": if you refresh too early AND too late, it resets
- Use case: detecting tasks that run too fast (stuck in tight loop feeding watchdog) as well as too slow
- Less commonly needed for general firmware

## IWDG registers (STM32)

| Register | Function |
|---|---|
| IWDG_KR | Key register — write 0xCCCC to start, 0xAAAA to refresh (kick), 0x5555 to unlock PR/RLR |
| IWDG_PR | Prescaler — /4 to /256, sets tick rate from LSI |
| IWDG_RLR | Reload value — 0–4095, counts down from this value |
| IWDG_SR | Status — PVU (prescaler update), RVU (reload update) |

## IWDG init (STM32 bare-metal)

```c
void watchdog_init(uint32_t timeout_ms) {
    // 1. Unlock PR and RLR registers
    IWDG->KR = 0x5555;

    // 2. Set prescaler: /64 gives tick = 64/32000 = 2ms per tick
    IWDG->PR = IWDG_PR_PR_2;  // /64

    // 3. Set reload: timeout_ms / 2ms per tick
    IWDG->RLR = (timeout_ms / 2) & 0xFFF;

    // 4. Wait for registers to update (required before start)
    while (IWDG->SR & (IWDG_SR_PVU | IWDG_SR_RVU));

    // 5. Start IWDG
    IWDG->KR = 0xCCCC;
}

void watchdog_kick(void) {
    IWDG->KR = 0xAAAA;  // reload counter — must happen before timeout
}
```

## Correct kick placement

The watchdog kick must be placed at the **end of one full cycle through the main loop** — after all tasks have had a chance to run:

```c
int main(void) {
    watchdog_init(2000);  // 2 second timeout
    // ... init peripherals ...
    while (1) {
        read_sensors();
        process_data();
        update_outputs();
        watchdog_kick();  // only here, at the bottom of the main loop
    }
}
```

**Never put watchdog_kick() inside a peripheral read loop, a retry loop, or any sub-loop.** If the sub-loop stalls, the watchdog still gets kicked and no reset occurs.

**With FreeRTOS:** Do not use a single task to kick the watchdog. Use a dedicated watchdog supervisor task at the highest priority that monitors health of all other tasks (task heartbeat flags) before kicking the hardware watchdog. On ESP32 IDF, use `esp_task_wdt_add()` for each critical task.

## Medical device rule

IEC 62304 and IEC 60601-1 require watchdog or equivalent fault detection in any medical software device. "The processor is reliable" is not an acceptable justification. A watchdog must be present and must be configured to reset the system within the system's defined safety response time. A patient monitor that freezes on stale data is a patient safety hazard.

## Common mistakes

**Kicking from an ISR:** An ISR fires even when the main loop is hung. Kicking the watchdog from a periodic ISR defeats its purpose entirely. The hung system looks healthy to the watchdog.

**Kicking too frequently:** Kicking at the top of the main loop rather than the bottom means even if the loop gets stuck on the first function call, the watchdog was already refreshed and won't fire until the next full timeout cycle.

**Timeout too long:** If your system must respond to a hardware fault within 500ms for safety reasons, a 5-second watchdog timeout is useless. Set the timeout to the maximum tolerable reset latency for your system, not to the "safe" long value that never fires during testing.

**WWDG instead of IWDG:** WWDG runs on APB1. If the main clock tree fails, WWDG stops running and will never reset the system. For detecting clock failures, only IWDG (on its own LSI oscillator) works.

**Not checking RCC_CSR for watchdog reset source:** After a reset, check if it was a watchdog reset — helps distinguish deliberate resets from fault resets during debugging.
