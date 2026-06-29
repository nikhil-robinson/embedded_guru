# SPI — Serial Peripheral Interface

## What it is

SPI is a synchronous serial protocol using 4 wires: SCK (clock), MOSI (master out slave in), MISO (master in slave out), CS/NSS (chip select, one per slave). The master always drives SCK. Full-duplex — master and slave exchange bytes simultaneously every clock cycle.

## Wiring

```
MCU (master)           Peripheral (slave)
    SCK  ─────────────────  SCK
    MOSI ─────────────────  MOSI (SDI, DI, SI)
    MISO ─────────────────  MISO (SDO, DO, SO)
    CS   ─────────────────  CS (NSS, CE, SS)
                            CS is active-LOW by default
```

Multiple slaves: each slave gets its own CS pin. SCK/MOSI/MISO are shared. Only one CS is asserted at a time.

## SPI Modes (CPOL/CPHA)

| Mode | CPOL | CPHA | Clock idle | Sample on |
|---|---|---|---|---|
| 0 | 0 | 0 | LOW | Rising edge |
| 1 | 0 | 1 | LOW | Falling edge |
| 2 | 1 | 0 | HIGH | Falling edge |
| 3 | 1 | 1 | HIGH | Rising edge |

**Always check the peripheral datasheet** for which mode it requires. Most sensors use Mode 0 or Mode 3. Getting CPOL/CPHA wrong causes every byte to be corrupted — no error flag, just wrong data.

## STM32 SPI registers (F4 series)

| Register | Function |
|---|---|
| SPI_CR1 | CPOL, CPHA, BR[2:0] (baud rate divisor), MSTR (master mode), SPE (SPI enable), DFF (data frame 8/16-bit), LSBFIRST, SSI, SSM, RXONLY |
| SPI_CR2 | SSOE (NSS output enable), TXDMAEN, RXDMAEN, ERRIE, RXNEIE, TXEIE |
| SPI_SR | TXE (TX buffer empty), RXNE (RX buffer not empty), BSY (busy), OVR (overrun), MODF (mode fault) |
| SPI_DR | Data register — write to transmit, read to receive |

## Baud rate divisor (STM32)

BR[2:0] in SPI_CR1 divides the APB clock:

| BR[2:0] | Divisor |
|---|---|
| 000 | /2 |
| 001 | /4 |
| 010 | /8 |
| 011 | /16 |
| 100 | /32 |
| 101 | /64 |
| 110 | /128 |
| 111 | /256 |

SPI1 is on APB2 (84 MHz on F446). SPI2/SPI3 are on APB1 (42 MHz). Never exceed the slave device's max SCK speed from its datasheet.

## Init sequence (STM32 bare-metal, SPI1, Mode 0, 8-bit)

```c
// 1. Enable clocks
RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

// 2. GPIO: PA5=SCK, PA6=MISO, PA7=MOSI → AF5; PA4=CS → output
GPIOA->MODER |= (2<<(5*2)) | (2<<(6*2)) | (2<<(7*2));  // AF mode
GPIOA->MODER |= (1<<(4*2));                               // CS = output
GPIOA->AFR[0] |= (5<<(5*4)) | (5<<(6*4)) | (5<<(7*4)); // AF5
GPIOA->BSRR = (1<<4);  // CS HIGH (deasserted) initially

// 3. Configure SPI1
SPI1->CR1 = SPI_CR1_MSTR      // master mode
           | SPI_CR1_BR_1      // BR=010 → /8 → 10.5 MHz
           | SPI_CR1_SSM       // software NSS management
           | SPI_CR1_SSI;      // SSI=1 keeps MODF from firing
// CPOL=0, CPHA=0 → Mode 0 (left at reset value)

// 4. Enable SPI
SPI1->CR1 |= SPI_CR1_SPE;
```

## Transfer function (polling, 8-bit)

```c
uint8_t spi_transfer(uint8_t tx) {
    while (!(SPI1->SR & SPI_SR_TXE));   // wait for TX buffer empty
    SPI1->DR = tx;
    while (!(SPI1->SR & SPI_SR_RXNE));  // wait for RX data ready
    return SPI1->DR;
}
```

A multi-byte transfer:
```c
void spi_read_register(uint8_t reg, uint8_t *buf, size_t len) {
    GPIOA->BSRR = (1 << (4 + 16));  // CS LOW (assert)
    spi_transfer(reg | 0x80);        // send register address (read bit set)
    for (size_t i = 0; i < len; i++) {
        buf[i] = spi_transfer(0xFF); // send dummy, capture MISO
    }
    GPIOA->BSRR = (1 << 4);          // CS HIGH (deassert)
}
```

## Critical CS rules

1. Assert CS **before** the first SCK edge, deassert **after** the last SCK edge.
2. Always send the entire transaction (address + all data bytes) within one CS assertion. Deasserting mid-transaction resets the slave's internal state machine.
3. On mode fault (MODF flag): this fires if CS goes low while SSM=0 and SSI=0. Set SSM=1 (software NSS) to manage CS manually with a GPIO, or set SSM=0 + SSOE=1 for hardware NSS with single slave only.

## Common mistakes

**CS not asserted before transfer:** Slave ignores all SCK edges. No data returned. Most common SPI bug. Always assert CS first.

**Wrong SPI mode for sensor:** CPOL/CPHA wrong = every byte corrupted. No error flag, no exception, just wrong numbers. Check sensor datasheet and reconfigure if needed.

**Not waiting for BSY before deasserting CS:** After the last byte, SPI_SR BSY is still set while the last bit is being shifted out. Deasserting CS before BSY clears truncates the last byte. On STM32, check: `while (SPI1->SR & SPI_SR_BSY);` before raising CS.

**Sending dummy byte with 0x00 vs 0xFF:** When master needs to receive data, it must clock SCK by sending something. 0xFF is the conventional dummy byte for sensors — some sensors interpret a 0x00 command as a reset or write.

**MOSI/MISO swapped:** Extremely common. Probe with oscilloscope — MOSI should toggle with transmitted data, MISO should show incoming data.

**LSBFIRST when sensor expects MSBFIRST:** Default STM32 SPI is MSB first. Most sensors also expect MSB first. If a sensor expects LSB first, set LSBFIRST bit in CR1. Mismatched bit order gives inverted/shifted bytes.
