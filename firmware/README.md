**Firmware 0.1.0 for revision A**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

This is a small bare-metal STM32F042K6 firmware, built with Arm GNU Toolchain 13.2.Rel1. ST CMSIS device files and Arm CMSIS headers are included with their licenses. The final two 1 KiB flash pages are reserved for redundant configuration records; the application linker permits 30 KiB of code and 6 KiB of RAM.

From the repository root:

```sh
source tools/env.sh
make -C firmware
bash scripts/test_firmware.sh
```

`firmware/build/sensor_can.elf`, `.hex` and `.bin` are the programming artifacts. The checked image occupies 7132 bytes of flash and 1832 bytes of reserved RAM, including a 1 KiB stack reservation. RAM figures do not establish measured worst-case stack depth. Host tests exercise the actual application and portable logic, but do not execute the STM32 peripheral registers.

**Program and provision**

Use an ST-Link compatible SWD probe with its target-power output disconnected. Power the board from a current-limited bench supply at J1. Wire the custom J8 header as listed in [WIRING.md](../docs/WIRING.md) and the exact [programmer mapping](../docs/ACCESSORIES.md): VTref→1, SWDIO→2, GND→3, SWCLK→4 and NRST→10 if available. Do not plug a standard 10-pin Cortex cable into this header.

With OpenOCD 0.12 and an ST-Link probe, the intended command is:

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c 'adapter speed 1000' \
  -c 'program firmware/build/sensor_can.elf verify reset exit'
```

This command has not been exercised against a physical board. Confirm probe detection, target voltage, device identity and flash verification before relying on it. A normal application update should preserve the two configuration pages. A full-chip erase removes configuration and returns the firmware to its unconfigured behavior. Do not change readout protection or option bytes for ordinary bring-up.

Attach a **3.3 V logic** USB-UART adapter: adapter RX→J8.6, TX→J8.8, GND→J8.5 or 9. Leave its power lead disconnected. UART is 115200 baud, 8 data bits, no parity, one stop bit. Install `pyserial` for the host service tool.

```sh
python host/sensor_can.py info --port /dev/ttyUSB0
# Example: device 17, channel 1 active-low, 2 ms debounce, all sensor power OFF.
python host/sensor_can.py configure --port /dev/ttyUSB0 \
  --device 17 --invert 1 --debounce 2 --rails 0
```

The tool sends `SET`, waits for reset, then verifies persistent values through `INFO`. Device IDs are 0–63 and must be unique for this protocol. Inversion is a four-bit channel mask. Debounce is 1–100 ms. Rail masks are 0=off, 1=5 V, 2=battery, 3=both. A stored nonzero rail mask enables those rails automatically after an ordinary startup, so use rails=0 until wiring is verified. A watchdog reset overrides this with latched-off rails.

Once power and sensor checks pass, provision the desired rail mask explicitly, or keep the persistent setting off and request power through robot code. In a terminal, supported commands are `HELP`, `INFO`, `SET id invert debounce_ms rails`, and `CLEAR mask`, each followed by newline. `SET` disables rails, writes a CRC-protected record with its commit marker last, and resets. Two alternating pages retain the previous valid record if a write is interrupted. Flash endurance is finite: do not write persistent settings repeatedly from robot code.

After removing an overload and waiting at least 100 ms with the rail off:

```sh
python host/sensor_can.py clear --port /dev/ttyUSB0 --mask 2
```

This is a single recovery attempt. If a Broadcast Disable cleared the requested rail state, first request the desired rails through runtime configuration or a deliberate new persistent `SET`. Never continuously clear faults. The INFO response reports configuration, requested/enabled rails and fault state; a successful command is not proof of voltage at the sensor.

**Behavior and diagnostics**

With invalid or erased configuration, sensor power is off and the CAN transceiver stays in standby. Input processing and service UART still run. The 8 MHz crystal drives a 48 MHz PLL; CAN uses a 3×16 time-quanta arrangement for 1 Mbit/s and 87.5% sample point. A 1 kHz scheduler samples inputs, a configurable debounce filters state, and bounded queues prevent UART/CAN traffic from blocking indefinitely.

Hardware enable pulldowns and CAN standby pull-up establish reset defaults. Clock-security NMI, hard fault, low-voltage PVD and a foreground delay exceeding 20 ms force sensor power off. The independent watchdog then resets the device. Firmware enables the highest PVD level, whose falling threshold is nominally 2.78 V with a 2.66–2.90 V datasheet range. This protects logic operation; it does not keep a 10 V sensor working during battery sag. Sensor supply health remains an application responsibility.

The green status LED is a firmware heartbeat when CAN initialization succeeds; **it is not proof of an acknowledged or healthy CAN bus**. Red indicates unconfigured state, a clock/CAN initialization failure, ADC failure or latched sensor fault. Four green input LEDs indicate logical, debounced channel states. Review CAN diagnostics and stale-data handling even if the green LED flashes.

ADC calibration includes the STM32F042 erratum's delay before enabling conversion. VREFINT factory calibration compensates nominal VDD variation. ADC readings update every 1 ms; CAN diagnostic packets transmit every 100 ms. Both readings measure switched sensor outputs. Below a measured 4.5 V, an enabled rail latches off after the 5 ms startup blanking interval; ADC failure latches both rails. TPS1H200A can assert digital FAULT at a healthy 10–20 mA or lighter load, so firmware does not treat that ambiguous battery FAULT alone as an overload. Its hardware current-limit/latch remains active. Voltage readings are monitoring estimates and require physical calibration/accuracy checks.

The full packet layout, Broadcast Disable response and recovery semantics are in [CAN_PROTOCOL.md](../docs/CAN_PROTOCOL.md). No wireless, USB, bootloader update protocol, CTRE protocol or actuator control is implemented.

**Peripheral errata review**

The [STM32F042 errata](https://www.st.com/resource/en/errata_sheet/es0243-stm32f042x4x6-device-errata-stmicroelectronics.pdf) were compared with the configured peripherals; the source-hashed review is in `reports/firmware-errata-review.json`. The ADC enable delay is present and CAN time-triggered mode is unused. The documented noisy-UART limitation remains a hardware concern; use short bench service wiring and verify configuration readback.

**Stack review**

The build emits GCC `.su` frame reports. `python scripts/audit_firmware_stack.py` combines these with the linked direct-call graph and inspected library prologues. The checked build estimates 212 bytes for the deepest foreground chain, plus a deliberately conservative 220 bytes counting all enabled/fault exception frames together. The 432-byte total fits the 1024-byte minimum linker reservation; 5336 bytes actually remain above static data. This static screen does not replace a hardware high-water-mark test or detect memory corruption. It rejects unreviewed indirect runtime calls, recursive call graphs and dynamic compiler stack frames. The emitted firmware binary is unchanged by stack-report generation.

**Compiled ARM register-model tests**

`python firmware/tests/test_arm_registers.py` executes the linked Cortex-M0 functions with Unicorn 2.1.4. Explicit synthetic register models provide readiness flags, ADC samples, CAN FIFO contents, UART buffering, flash erasure and GPIO set/reset effects. Thirteen check groups cover actual pin mux/modes, rail/fault/LED mappings, clock/PVD/watchdog setup, CAN filters/mailboxes, ADC scaling, UART overflow, and flash persistence including 34 modeled interruptions after halfword writes. This reaches the production `board.c` machine code that the host application tests replace with a fake board interface. It does not emulate STM32 peripheral timing, analog behavior, interrupt preemption, CAN arbitration or real flash brownout behavior. The physical bring-up tests remain required.
