# DMA — Direct Memory Access

## What it is

DMA transfers data between memory and peripherals (or memory-to-memory) without CPU involvement. The DMA controller reads/writes on the bus autonomously while the CPU runs other code or sleeps. Used for: high-speed peripheral receive/transmit (UART, SPI, I2C, ADC), audio buffers, large memory moves.

## Why it matters

Without DMA, the CPU must service every byte in an ISR or polling loop. At 1 Mbit/s SPI with 8-bit frames: 125,000 interrupts/second. At 90 MHz CPU clock, that leaves only 720 cycles between interrupts. DMA transfers these bytes autonomously — the CPU gets one interrupt when the whole buffer is full.

## STM32 DMA architecture (F4 series)

Two DMA controllers: DMA1 and DMA2. Each has 8 streams. Each stream handles one transfer at a time. Each stream has 8 channel selects — you must pick the correct channel for the peripheral you're connecting.

**Always consult the DMA request mapping table in the reference manual.** Connecting SPI1_TX to the wrong channel silently produces nothing. The table is in the DMA chapter (Table 42 in RM0390 for STM32F446).

Common mappings (STM32F446):
| Peripheral | DMA | Stream | Channel |
|---|---|---|---|
| USART1_TX | DMA2 | Stream 7 | Channel 4 |
| USART1_RX | DMA2 | Stream 2 | Channel 4 |
| SPI1_TX | DMA2 | Stream 3 | Channel 3 |
| SPI1_RX | DMA2 | Stream 0 | Channel 3 |
| SPI2_TX | DMA1 | Stream 4 | Channel 0 |
| SPI2_RX | DMA1 | Stream 3 | Channel 0 |
| I2C1_TX | DMA1 | Stream 6 | Channel 1 |
| I2C1_RX | DMA1 | Stream 0 | Channel 1 |
| ADC1 | DMA2 | Stream 0 | Channel 0 |

## DMA registers (STM32 F4)

| Register | Function |
|---|---|
| DMA_SxCR | Stream control — EN (enable), DIR (direction: P→M or M→P), CIRC (circular mode), MINC (memory increment), PINC (peripheral increment), MSIZE/PSIZE (8/16/32-bit), PL (priority), CHSEL (channel), TCIE (transfer complete interrupt enable), HTIE (half-transfer interrupt enable), TEIE (transfer error interrupt enable) |
| DMA_SxNDTR | Number of data items to transfer (bytes if MSIZE=8-bit) |
| DMA_SxPAR | Peripheral address (e.g., &USART1->DR) |
| DMA_SxM0AR | Memory address 0 (source or destination buffer) |
| DMA_SxM1AR | Memory address 1 (for double-buffer mode) |
| DMA_LISR / HISR | Interrupt status — TCIFx, HTIFx, TEIFx, DMEIFx, FEIFx (Streams 0–3 in LISR, 4–7 in HISR) |
| DMA_LIFCR / HIFCR | Clear interrupt flags — must clear before re-enabling stream |

## DMA init sequence (USART1 RX, polling for complete)

```c
// 1. Enable DMA2 clock
RCC->AHB1ENR |= RCC_AHB1ENR_DMA2EN;

// 2. Disable stream before configuring (always required)
DMA2_Stream2->CR &= ~DMA_SxCR_EN;
while (DMA2_Stream2->CR & DMA_SxCR_EN);  // wait for disable

// 3. Clear interrupt flags for Stream 2 (in LISR)
DMA2->LIFCR = DMA_LIFCR_CTCIF2 | DMA_LIFCR_CHTIF2 |
              DMA_LIFCR_CTEIF2 | DMA_LIFCR_CDMEIF2 | DMA_LIFCR_CFEIF2;

// 4. Configure stream
DMA2_Stream2->CR  = (4 << DMA_SxCR_CHSEL_Pos)  // Channel 4 = USART1_RX
                  | DMA_SxCR_MINC               // memory increment
                  | DMA_SxCR_TCIE;              // transfer complete interrupt
DMA2_Stream2->PAR  = (uint32_t)&USART1->DR;
DMA2_Stream2->M0AR = (uint32_t)rx_buffer;
DMA2_Stream2->NDTR = BUFFER_SIZE;

// 5. Enable DMA in USART
USART1->CR3 |= USART_CR3_DMAR;

// 6. Enable stream
DMA2_Stream2->CR |= DMA_SxCR_EN;
```

## Transfer complete interrupt

```c
void DMA2_Stream2_IRQHandler(void) {
    if (DMA2->LISR & DMA_LISR_TCIF2) {
        DMA2->LIFCR = DMA_LIFCR_CTCIF2;  // clear flag first
        process_rx_buffer();
        // Restart DMA for next transfer if not using circular mode:
        DMA2_Stream2->CR &= ~DMA_SxCR_EN;
        while (DMA2_Stream2->CR & DMA_SxCR_EN);
        DMA2_Stream2->NDTR = BUFFER_SIZE;
        DMA2_Stream2->CR |= DMA_SxCR_EN;
    }
}
```

## Circular mode

Set `DMA_SxCR_CIRC` — DMA wraps NDTR back to the original count after completion and restarts automatically. Use half-transfer interrupt (`HTIE`) and transfer-complete interrupt (`TCIE`) to double-buffer: process the first half while DMA fills the second, then process the second half while DMA fills the first. Used for audio, ADC continuous sampling.

## Common mistakes

**Wrong DMA channel:** Each peripheral maps to a specific DMA stream+channel combination. Using the correct stream with the wrong channel → nothing happens, no error. Always verify against the DMA request table in the reference manual.

**Not clearing interrupt flags before re-enabling:** Restarting a DMA stream without clearing TCIF/TEIF causes the interrupt to fire immediately on re-enable, corrupting the transfer. Always clear flags in LIFCR/HIFCR before re-arming.

**Not waiting for EN=0 after disabling:** After clearing the EN bit, the DMA stream takes 1–2 AHB cycles to actually disable. Immediately reconfiguring registers (PAR, M0AR, NDTR) while still enabled corrupts the next transfer. Always poll `while (DMA_SxCR & EN)` after clearing EN.

**Cache coherency (Cortex-M7 / STM32H7):** On Cortex-M7 with D-cache enabled (STM32H7, STM32F7 optionally), DMA accesses physical memory, CPU accesses cache. If CPU writes a buffer and DMA reads it, the DMA may read stale data from RAM while the cache has the new value. Must call `SCB_CleanDCache_by_Addr()` before DMA transmit and `SCB_InvalidateDCache_by_Addr()` before reading DMA receive buffer. **This is the #1 cause of intermittent DMA failures on H7/F7.**

**Buffer not word-aligned:** DMA with 32-bit transfers requires 4-byte aligned memory address. Misaligned buffer → DMA address error (DMEIF flag), silent failure.

**Peripheral not enabled for DMA:** Must set TXDMAEN or RXDMAEN in the peripheral's own register (e.g., USART_CR3 DMAR/DMAT, SPI_CR2 RXDMAEN/TXDMAEN). Setting up DMA without enabling it in the peripheral → DMA never gets a request signal → nothing transfers.
