# Firmware 0.8.0 — Rev G SC12, protocol v4

Bare-metal STM32F042K6T6 firmware for three digital inputs. Build allocation is recorded by the current linker map/build report; stack depth has not been measured. The final two 1 KiB flash pages hold redundant 32-byte versioned configuration with CRC and commit-last writes.

Rev G uses **hardware identity 7** and **protocol 4**. It has a separate image tag and configuration magic so D2 images/settings are rejected. Use the matching drivers and [software input modes](../docs/INPUT_MODES.md). The separate power caps select sensor voltage.

**CAN service is implemented, physically unqualified:** full-UID discovery, identify LED, persistent ID/inversion/debounce and verified uploads. See [CAN setup/update](../docs/CAN_SERVICE.md), [robot bridge](../examples/bridge/README.md) and [qualification plan](../docs/VALIDATION.md).

From `current/`:

```sh
source tools/env.sh
make -C firmware
bash scripts/test_firmware.sh
```

Outputs: `build/factory.hex` for initial SWD installation; `build/application.sc12` for CAN updates; separate bootloader/application ELF, BIN and MAP files. `sensor_can.hex`/ELF are application-only at 0x08002000. Flash: 8 KiB bootloader, 21 KiB app, 1 KiB manifest, 2 KiB configuration. Both linkers reserve the first 256 SRAM bytes and a 1 KiB minimum stack. The MCU controls six input-bias gates and two sensor-rail enables, and reads divided 5 V/12 V supplies through ADC channels 8/9. Per-input LEDs are not fitted. The 8 MHz external crystal and PLL generate 48 MHz; bxCAN uses 16 time quanta with an 87.5% sample point at 1 Mbit/s. Auto bus-off recovery is enabled; automatic transmit retry is disabled.

Power through J1 from a bench supply. Use the [custom TC2050 wiring](../docs/WIRING.md): VTref sense→6, SWDIO→5, SWCLK→4, ground→7, optional reset→1. Leave probe power disconnected.

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c 'adapter speed 1000' \
  -f tools/program_factory.tcl
```

This command has not been exercised on physical Rev G hardware. Verify MCU identity, supply and flash readback. Normal application programming should preserve the two configuration pages; full-chip erase removes them. Version-1/2 configuration is rejected.

UART: adapter TX→J8.2, RX→J8.3, ground→J8.8; 3.3 V, 115200 baud, 8N1; adapter power disconnected.

```sh
python host/sensor_can.py info --port /dev/ttyUSB0
python host/sensor_can.py configure --port /dev/ttyUSB0 \
  --device 17 --invert 1 --debounce 2
```

Device IDs 0–63 must be unique in this Team Use address space. Invert is a 3-bit mask; debounce is 1–100 ms. UART `SET id invert debounce_ms` and UID-targeted CAN service save persist and reset. Legacy CAN runtime configuration remains volatile. Unconfigured boards accept discovery/service but suppress normal telemetry. Power-cycle after initial SWD programming and verify boot protection before CAN updates. **Both sensor rails default off during reset/programming and remain off in the bootloader.** The application enables 5 V after 10 ms and 12 V after 60 ms; hardware current limiting remains independent of software. On Rev G, leave the caps off JP101/JP201/JP301 to disconnect port power during initial bring-up; configure them only with input power disconnected. Input bias is electronic; CAN termination remains a solder setting. See [assembly](../docs/ASSEMBLY.md).

The independent watchdog is serviced only after the full 1 ms foreground cycle. A >20 ms foreground delay, clock failure, hard fault or PVD low-voltage detection puts CAN into standby; the watchdog provides reset recovery. The single LED pulses approximately 100 ms per second when configured and healthy, or 100 ms per 200 ms for configuration/clock/CAN errors. Rail faults also trigger the fast fault indication. PA3/PA4 read active-low 12 V/5 V fault outputs with internal pullups. PB0/PB1 measure divided 5 V/12 V with the calibrated internal reference. PA15 enables 5 V; PB7 enables the Q3/Q2 12 V stage. PB5/PB6/PB4 drive input pull-downs 1/2/3. A qualified fault disables the rail until explicit CAN reset or a board restart. ADC failure disables both rails. Startup allows 200 ms, then an undervoltage persisting 20 ms latches off; overvoltage or asserted switch fault trips immediately. Healthy rails need 100 ms continuous qualification before counts resume. See `src/power.c` for exact thresholds and unit tests.


Measured health bands are 11.1–12.9 V and 4.55–5.50 V; low-voltage latch thresholds are 10.8 V and 4.4 V. These bands include ADC/reference/divider error and are separate from the calibrated-meter acceptance limits. Overvoltage trips remain 13.0 V and 5.6 V. The [electrical report](../reports/electrical/electrical_checks.json) records the measurement-error budget.

Broadcast Disable ID 0 stops telemetry and aborts pending transmissions. Local sampling and application-managed sensor power continue. An explicit `RESUME` UART command or CAN resume command re-enables telemetry; reads never do this automatically. See [protocol v4](../docs/CAN_PROTOCOL.md). Host tests cover firmware logic and mocked peripheral boundaries, not actual oscillator startup, electrical timing or STM32 peripheral behavior.
