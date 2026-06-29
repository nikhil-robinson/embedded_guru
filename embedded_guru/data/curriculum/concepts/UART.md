# UART — Universal Asynchronous Receiver/Transmitter

## What it is

UART transmits bytes serially, one bit at a time, using two wires: TX and RX. Asynchronous — no shared clock. Both sides must be pre-configured to the same baud rate.

## Electrical

- Logic levels: 3.3V or 5V (match MCU and device — never connect 5V TX to 3.3V RX without level shifting)
- Crossing: MCU TX → device RX, MCU RX → device TX (always crossed)
- RS-232 uses negative-logic ±12V — not directly compatible with MCU GPIO. Requires MAX232 or similar converter.
- USB-UART bridges: CH340, CP2102, FTDI — convert USB to MCU-compatible logic UART

## Frame format

Each byte is wrapped in a frame:
```
[IDLE HIGH] [START BIT = 0] [D0 D1 D2 D3 D4 D5 D6 D7] [PARITY optional] [STOP BIT = 1 (or 2)]
```
- Start bit: always 0 (LOW)
- Data bits: LSB first by default
- Stop bit: always 1 (HIGH). Line returns to IDLE (HIGH) after stop bit.
- Parity: optional, rarely used in embedded (adds overhead, doesn't correct)

## Baud rate

Common standard baud rates: 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600

At 115200 baud: each bit = 8.68 µs. A full 8N1 byte takes 10 bit-times = 86.8 µs.

Baud rate error: UART is tolerant of up to ~3–5% baud rate mismatch. Beyond that, byte framing breaks. MCU internal oscillators are typically accurate to ±1–2%. Crystal oscillators are accurate to ±50ppm. If UART is corrupted, check: (1) baud rate both sides, (2) clock source, (3) TX/RX not crossed.

## STM32 USART registers (F4 series)

| Register | Function |
|---|---|
| USART_SR | Status register — TXE (TX buffer empty), TC (TX complete), RXNE (RX not empty), ORE (overrun), FE (framing error) |
| USART_DR | Data register — write to transmit, read to receive |
| USART_BRR | Baud rate register — USARTDIV value = f_CLK / (16 × baud) for 16× oversampling |
| USART_CR1 | Control — UE (USART enable), TE (TX enable), RE (RX enable), RXNEIE (RX interrupt enable), TXEIE (TX buffer empty interrupt), PCE (parity enable), M (word length) |
| USART_CR2 | STOP bits field (bits 13:12) — 00=1 stop, 10=2 stop |
| USART_CR3 | DMA enable (DMAT, DMAR), hardware flow control (CTSE, RTSE) |

## Init sequence (STM32 bare-metal)

```c
// 1. Enable GPIO and USART clocks
RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
RCC->APB2ENR |= RCC_APB2ENR_USART1EN;  // USART1 is on APB2

// 2. Configure GPIO pins to AF (alternate function) mode
// PA9 = USART1_TX, PA10 = USART1_RX (AF7)
GPIOA->MODER  |= (2 << (9*2)) | (2 << (10*2));   // AF mode
GPIOA->AFR[1] |= (7 << ((9-8)*4)) | (7 << ((10-8)*4));  // AF7

// 3. Set baud rate (115200 at 84 MHz APB2 clock)
// BRR = 84000000 / 115200 = 729 → 0x2D9
USART1->BRR = 0x2D9;

// 4. Enable TX and RX, then enable USART
USART1->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
```

## Polling transmit

```c
void uart_send_byte(uint8_t b) {
    while (!(USART1->SR & USART_SR_TXE));  // wait for TX buffer empty
    USART1->DR = b;
}
```

**Do not check TC (transmission complete) for every byte** — TXE means the shift register accepted the byte, which is correct for back-to-back transmission. Check TC only when you need to know the last byte physically left the wire (e.g., before disabling RS-485 driver).

## Polling receive

```c
uint8_t uart_recv_byte(void) {
    while (!(USART1->SR & USART_SR_RXNE));  // wait for data
    return (uint8_t)USART1->DR;
}
```

Always check for ORE (overrun error) in production code — if a new byte arrives before you read DR, the old byte is lost and ORE is set. Reading DR clears RXNE.

## Interrupt-driven receive (correct pattern)

```c
// In ISR:
void USART1_IRQHandler(void) {
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t b = USART1->DR;  // reading DR clears RXNE
        ring_buffer_push(&rx_buf, b);
    }
    if (USART1->SR & USART_SR_ORE) {
        (void)USART1->DR;  // clear ORE by reading DR
    }
}
```

## DMA transmit (correct pattern)

Configure DMA stream to transfer from buffer to USART1->DR, enable USART_CR3_DMAT. Check TC on DMA stream completion, not USART TC per byte.

## Common mistakes

**Wrong baud rate calculation:** BRR formula differs by oversampling setting (CR1 OVER8 bit). Default is 16× oversampling. BRR = f_CLK / (16 × baud). If OVER8=1: BRR formula changes. Verify with oscilloscope measuring a known byte.

**USART clock on wrong bus:** USART1 and USART6 are on APB2 (up to 84 MHz on F4). USART2, USART3, UART4, UART5 are on APB1 (up to 42 MHz on F4). Using the wrong bus clock frequency gives wrong baud rate silently.

**Not clearing ORE:** In some STM32 variants, if ORE is set and not cleared, the RXNE interrupt will immediately re-fire and the ISR loops indefinitely. Always handle ORE.

**Forgetting to enable peripheral clock before configuring GPIO alternate function:** GPIO AF selection takes effect only after the peripheral clock is running. If USART clock is not enabled, UART pins will not behave as expected.

**TX not enabled:** Setting RE (receive enable) but forgetting TE (transmit enable), or vice versa.
