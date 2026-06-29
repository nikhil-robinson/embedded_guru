# Embedded Development Boards

## STM32 Nucleo-F446RE

**MCU:** STM32F446RE  
**Vendor:** STMicroelectronics  
**Architecture:** ARM Cortex-M4, 180 MHz  
**Reference manual:** RM0390  
**is_microcontroller:** true  
**Price:** ~$15 USD  
**Recommended for domains:** Automotive, Medical, Industrial  
**Recommended for levels:** L2, L3  

**Peripherals present:**
- bxCAN (CAN 2.0A/B, 1Mbit/s) — bare metal capable, not SocketCAN
- I2C1, I2C2, I2C3 (up to 400kHz Fast Mode)
- SPI1, SPI2, SPI3, SPI4, SPI5, SPI6
- UART1, UART2, UART3, UART4, UART5, USART6
- 16-bit and 32-bit timers (TIM1–TIM14)
- DMA1, DMA2 (16 streams total)
- IWDG (Independent Watchdog, LSI-clocked — runs even if main clock fails)
- WWDG (Window Watchdog, APB1-clocked)
- ADC1, ADC2, ADC3 (12-bit, up to 2.4 MSPS)
- USB OTG FS/HS
- SDIO (SD card interface)
- GPIO: up to 51 I/O pins on Nucleo-64

**Peripherals NOT present:**
- FDCAN (has bxCAN instead — different register map, no CAN FD support)
- Ethernet MAC (not on F446RE; use F407/F429 for Ethernet)
- Hardware floating point: FPU present (Cortex-M4F)

**Key constraint for Automotive domain:** bxCAN peripheral requires external CAN transceiver (SN65HVD230 or MCP2551) — the MCU only provides the digital CAN controller, not the differential bus driver.

---

## STM32 Nucleo-F411RE

**MCU:** STM32F411RE  
**Vendor:** STMicroelectronics  
**Architecture:** ARM Cortex-M4, 100 MHz  
**Reference manual:** RM0383  
**is_microcontroller:** true  
**Price:** ~$15 USD  
**Recommended for domains:** Medical, IoT  
**Recommended for levels:** L2, L3  

**Peripherals present:**
- I2C1, I2C2, I2C3
- SPI1, SPI2, SPI3, SPI4, SPI5
- UART1, UART2, UART6
- Timers (TIM1–TIM11)
- DMA1, DMA2
- IWDG, WWDG
- ADC1 (12-bit)
- USB OTG FS
- GPIO: up to 50 I/O

**Peripherals NOT present:**
- CAN — no CAN peripheral at all. Cannot be used for Automotive CAN assignments without external CAN controller (MCP2515 over SPI).
- SDIO — no hardware SD card interface

---

## STM32 Nucleo-G0B1RE

**MCU:** STM32G0B1RE  
**Vendor:** STMicroelectronics  
**Architecture:** ARM Cortex-M0+, 64 MHz  
**Reference manual:** RM0444  
**is_microcontroller:** true  
**Price:** ~$15 USD  
**Recommended for domains:** Automotive, Industrial  
**Recommended for levels:** L2, L3  

**Peripherals present:**
- FDCAN1, FDCAN2 (CAN FD up to 5Mbit/s, also CAN 2.0 compatible)
- I2C1, I2C2, I2C3
- SPI1, SPI2, SPI3
- UART1–UART6, LPUART1, LPUART2
- Timers TIM1–TIM17
- DMA1, DMA2
- IWDG, WWDG
- ADC (12-bit)
- USB Type-C PD

**Note:** FDCAN register map is different from bxCAN (F4 series). Students moving from F446RE to G0B1RE must re-learn the CAN peripheral registers.

---

## ESP32-DevKitC

**MCU:** ESP32 (Xtensa LX6 dual-core, 240 MHz)  
**Vendor:** Espressif  
**Architecture:** Xtensa LX6, dual-core  
**is_microcontroller:** true  
**Price:** ~$5–10 USD  
**Recommended for domains:** IoT  
**Recommended for levels:** L1, L2  

**Peripherals present:**
- WiFi 802.11 b/g/n (built-in)
- Bluetooth 4.2 + BLE (built-in)
- I2C (2 controllers, any GPIO pins via GPIO matrix)
- SPI (4 controllers: SPI0, SPI1 internal flash; SPI2/SPI3 user-accessible)
- UART0 (USB serial), UART1, UART2
- Timers (hardware)
- DMA (dedicated per peripheral)
- RTC watchdog + task watchdog
- ADC1, ADC2 (12-bit, SAR)
- DAC (2 channels, 8-bit)
- 34 GPIO pins
- FreeRTOS: pre-integrated in ESP-IDF (FreeRTOS with SMP extensions for dual-core)

**Peripherals NOT present:**
- CAN: No hardware CAN controller. CAN not possible without external CAN controller (MCP2515 over SPI) — unsuitable for Automotive milestones 3+.

**Important note for Industrial/RTOS domain:** ESP32 runs FreeRTOS but it is a dual-core SMP variant. xQueueSendFromISR, portYIELD_FROM_ISR are available, but task pinning (xTaskCreatePinnedToCore) and esp_task_wdt (ESP-IDF watchdog API) differ from single-core STM32 FreeRTOS. Students must account for SMP-specific race conditions not present on single-core MCUs.

---

## Raspberry Pi 4 Model B

**MCU/SoC:** BCM2711 (ARM Cortex-A72 quad-core, 1.5–1.8 GHz)  
**Vendor:** Raspberry Pi Foundation  
**Architecture:** ARM Cortex-A72 (64-bit application processor)  
**is_microcontroller:** FALSE — this is a Linux single-board computer, not a microcontroller  
**Price:** ~$35–80 USD  

**CRITICAL: Not suitable for bare-metal embedded development.**  
The RPi4 runs Linux (Raspberry Pi OS). All peripheral access goes through Linux kernel drivers and userspace APIs. There is no direct register access in the same sense as a microcontroller. GPIO through /dev/mem or libgpiod. I2C through /dev/i2c-*. SPI through /dev/spidev*.

**Peripherals present (via Linux):**
- I2C via SocketCAN — NOT bare-metal CAN controller
- SPI (via Linux SPI driver)
- I2C (via Linux I2C driver)
- UART (via Linux tty driver)
- GPIO (via libgpiod or /dev/mem — NOT register-level bare metal)

**Peripherals NOT present:**
- Bare-metal CAN: RPi4 has no hardware CAN controller. Any CAN on RPi4 uses MCP2515 over SPI + SocketCAN in Linux kernel. This is Linux socket programming, not embedded CAN firmware. Cannot be used for Automotive milestones 3+.
- IWDG/watchdog: Software watchdog via Linux — not hardware watchdog as in STM32.

**When a student mentions RPi4 for Automotive CAN:** Flag immediately. Recommend STM32 Nucleo-F446RE or G0B1RE instead. RPi4 CAN is SocketCAN over Linux — an entirely different skill set from bxCAN register programming.

**When a student mentions RPi4 for bare-metal embedded:** Flag immediately. RPi4 is suitable for Linux systems programming, Python GPIO scripts, or as a host PC. It is not suitable for bare-metal register access, ISR programming, or hardware timer configuration in the microcontroller sense.

---

## Arduino Uno (ATmega328P)

**MCU:** ATmega328P  
**Vendor:** Arduino / Microchip  
**Architecture:** AVR 8-bit, 16 MHz  
**Reference manual:** ATmega328P datasheet (Microchip)  
**is_microcontroller:** true  
**Price:** ~$5–25 USD  

**Peripherals present:**
- I2C (TWI — Two Wire Interface) — 1 channel
- SPI — 1 channel
- UART — 1 channel (shared with USB via ATmega16U2)
- Timers: Timer0 (8-bit), Timer1 (16-bit), Timer2 (8-bit)
- Watchdog Timer (WDT)
- ADC (10-bit, 6 channels)
- GPIO: 14 digital, 6 analog

**Peripherals NOT present:**
- CAN: No CAN peripheral. Cannot do Automotive milestones 3+ without MCP2515.
- DMA: No DMA. All transfers are CPU-driven.
- FreeRTOS: Possible but very limited RAM (2KB SRAM). Not recommended for Industrial/RTOS track.

**Assessment note:** Students who say "I've used Arduino" often mean the Arduino IDE + library ecosystem, not register-level AVR programming. Ask: "Have you ever looked at the ATmega328P datasheet and configured a peripheral from registers?" A student who has only used digitalWrite() and analogRead() has L1 skills regardless of how long they've been using Arduino.

---

## Raspberry Pi Pico (RP2040)

**MCU:** RP2040  
**Vendor:** Raspberry Pi Foundation  
**Architecture:** ARM Cortex-M0+ dual-core, 133 MHz  
**Reference manual:** RP2040 Datasheet (Raspberry Pi)  
**is_microcontroller:** TRUE — bare-metal capable, no Linux  
**Price:** ~$4 USD  
**Recommended for domains:** IoT, Industrial  
**Recommended for levels:** L0, L1, L2  

**Peripherals present:**
- I2C0, I2C1
- SPI0, SPI1
- UART0, UART1
- 8 PIO state machines (programmable I/O — can emulate almost any serial protocol)
- DMA (12 channels)
- Watchdog
- ADC (12-bit, 4 external channels + 1 temperature sensor)
- 30 GPIO pins
- PWM
- FreeRTOS: supported (FreeRTOS RP2040 port)

**Peripherals NOT present:**
- CAN: No hardware CAN. Can emulate CAN-like protocols via PIO but not ISO 11898 compliant.
- WiFi/BLE: Not on base Pico. Available on Pico W variant (CYW43439 chip).

---

## STM32F103 Blue Pill (generic)

**MCU:** STM32F103C8T6  
**Vendor:** STMicroelectronics (clone boards widely available)  
**Architecture:** ARM Cortex-M3, 72 MHz  
**Reference manual:** RM0008  
**is_microcontroller:** true  
**Price:** ~$2–5 USD  

**Peripherals present:**
- bxCAN (CAN 2.0A/B) — bare metal capable, requires transceiver
- I2C1, I2C2
- SPI1, SPI2
- UART1, UART2, UART3
- Timers TIM1–TIM4
- DMA1 (7 channels)
- IWDG, WWDG
- ADC1, ADC2 (12-bit)
- USB 2.0 FS (full speed device)

**Warning:** Clone Blue Pill boards often have non-genuine STM32 chips. Some use CKS32 or CS32 MCUs with slightly different register behavior. Logic analyzer verification is important when debugging peripheral timing.
