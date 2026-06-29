# FreeRTOS — Real-Time Operating System Concepts

## What it is

FreeRTOS is a real-time kernel for embedded MCUs. It provides preemptive multitasking: multiple tasks run concurrently, the scheduler switches between them based on priority and time slices. Key primitives: tasks, queues, semaphores, mutexes, timers, event groups.

## Core abstractions

### Tasks
A task is a C function that runs in its own stack. It looks like an infinite loop:
```c
void my_task(void *param) {
    while (1) {
        do_work();
        vTaskDelay(pdMS_TO_TICKS(100));  // yield for 100ms
    }
}
```
Create with `xTaskCreate()`. Each task gets a priority (higher number = higher priority in FreeRTOS convention). Tasks must never return — they must call `vTaskDelete(NULL)` or loop forever.

### Scheduler
The scheduler is preemptive by default. A higher-priority task that becomes ready immediately preempts a lower-priority running task. Tasks at the same priority share time via round-robin. The tick rate is set by `configTICK_RATE_HZ` (typically 1000 Hz = 1ms tick).

### Queues
Queues pass data between tasks safely:
```c
QueueHandle_t q = xQueueCreate(10, sizeof(uint32_t));
xQueueSend(q, &value, portMAX_DELAY);    // from producer task
xQueueReceive(q, &value, portMAX_DELAY); // from consumer task
```
Queues are the correct way to pass data from an ISR to a task:
```c
// In ISR:
BaseType_t higher_prio_woken = pdFALSE;
xQueueSendFromISR(q, &value, &higher_prio_woken);
portYIELD_FROM_ISR(higher_prio_woken);
```
The `portYIELD_FROM_ISR` call is mandatory — if a higher-priority task was woken, the context switch must happen at ISR exit, not after an arbitrary delay.

### Semaphores
Binary semaphore: signaling between tasks or ISR→task. Use `xSemaphoreGiveFromISR()` in ISR, `xSemaphoreTake()` in task.

Counting semaphore: counting events (e.g., 5 items available).

### Mutexes
A mutex protects a shared resource. Only one task can hold it at a time:
```c
MutexHandle_t m = xSemaphoreCreateMutex();
xSemaphoreTake(m, portMAX_DELAY);
// critical section
xSemaphoreGive(m);
```
**Never use a mutex from an ISR** — use a semaphore instead. Mutexes have priority inheritance; semaphores do not.

### Priority inversion and priority inheritance
If a low-priority task holds a mutex and a high-priority task is waiting for it, and a medium-priority task preempts the low-priority task — the high-priority task is blocked by the medium one indirectly. FreeRTOS mutexes implement priority inheritance: the low-priority task temporarily runs at the high-priority task's level to finish the critical section faster.

### Software timers
One-shot or periodic callbacks that run from the Timer daemon task:
```c
TimerHandle_t t = xTimerCreate("t", pdMS_TO_TICKS(500), pdTRUE, 0, timer_cb);
xTimerStart(t, 0);
```
Timer callbacks run in the timer daemon context — keep them short. Do not block inside a timer callback.

## STM32 FreeRTOS init sequence

```c
// In main(), before vTaskStartScheduler():
xTaskCreate(task_a, "TaskA", 256, NULL, 2, NULL);
xTaskCreate(task_b, "TaskB", 256, NULL, 1, NULL);
vTaskStartScheduler();
// Never reaches here — scheduler takes over
```

After `vTaskStartScheduler()`, main() never returns. The scheduler calls the highest-priority ready task.

## Stack sizing

`configMINIMAL_STACK_SIZE` is typically 128 words (512 bytes on 32-bit MCU). Set stack size to fit local variables + printf depth + nested function calls. Stack overflow → silent corruption or hardfault. Enable stack overflow checking during development: `configCHECK_FOR_STACK_OVERFLOW = 2` and implement `vApplicationStackOverflowHook()`.

## Heap

FreeRTOS provides five heap implementations: heap_1 (no free), heap_2 (fragmentation possible), heap_3 (thread-safe wrapper for malloc/free), heap_4 (best fit, coalescing), heap_5 (multiple memory regions). **heap_4 is the standard choice** for most bare-metal STM32 applications.

`configTOTAL_HEAP_SIZE` must be large enough for all task stacks + kernel objects created before `pvPortMalloc` is ever called. Run `xPortGetFreeHeapSize()` at runtime to check.

## Common mistakes

**Blocking in an ISR:** Calling `xQueueSend()` instead of `xQueueSendFromISR()`, or calling `vTaskDelay()` from an ISR. Both corrupt scheduler state. ISR functions are named `*FromISR()` for a reason.

**Forgetting portYIELD_FROM_ISR:** After `xQueueSendFromISR()` or `xSemaphoreGiveFromISR()`, if `higher_prio_woken = pdTRUE`, the context switch must happen at ISR exit. Forgetting this means the woken task may not run until the next tick — defeating the point of the ISR wakeup.

**Mutex from ISR:** ISR must use semaphores, not mutexes. `xSemaphoreTakeFromISR()` exists; `xSemaphoreTakeMutexFromISR()` does not.

**vTaskDelay() in ms arithmetic:** `vTaskDelay(100)` = 100 ticks, not 100ms. Always use `pdMS_TO_TICKS(100)` which divides by the tick rate correctly. At configTICK_RATE_HZ=1000, these happen to be equal — but at 100Hz tick rate, `vTaskDelay(100)` = 1 second.

**Shared globals without protection:** Two tasks modifying a shared variable without a mutex → race condition. On Cortex-M, a 32-bit read-modify-write is not atomic. Use mutexes or `taskENTER_CRITICAL()` / `taskEXIT_CRITICAL()`.

**Watchdog from a task:** Feeding the watchdog from a task that might be preempted or delayed means the watchdog gets fed even when the rest of the system is hung. Use the FreeRTOS task watchdog (esp_task_wdt on ESP32, or a dedicated watchdog task on STM32) that monitors multiple tasks. Never feed the watchdog unconditionally.

**Stack too small:** Default minimal stack is often insufficient for tasks that call printf or deep library functions. Printf alone can consume 400+ bytes of stack. Always add 30–50% headroom over your calculated minimum. Enable stack overflow hooks during development.

**Creating tasks after vTaskStartScheduler:** You can create tasks after the scheduler starts, but you must be inside a task to do so. Never call xTaskCreate() from an ISR.
