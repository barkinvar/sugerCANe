# Firmware 0.4.0 — Rev D SC12, protocol v3

Bare-metal STM32F042K6T6 firmware for three digital inputs. Build allocation is recorded by the current linker map/build report; stack depth has not been measured. The final two 1 KiB flash pages hold redundant 32-byte versioned configuration with CRC and commit-last writes.

From `rev_d/`:

```sh
source tools/env.sh
make -C firmware
bash scripts/test_firmware.sh
```

Outputs: `build/sensor_can.elf`, `.hex`, `.bin`, `.map`. No ADC, sensor rail GPIO control or per-input LED logic remains. The 8 MHz external crystal and PLL generate 48 MHz; bxCAN uses 16 time quanta with an 87.5% sample point at 1 Mbit/s. Auto bus-off recovery is enabled; automatic transmit retry is disabled.

Power through J1 from a bench supply. Use the [custom TC2050 wiring](../docs/WIRING.md): VTref sense→6, SWDIO→5, SWCLK→4, ground→7, optional reset→1. Leave probe power disconnected.

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c 'adapter speed 1000' \
  -c 'program firmware/build/sensor_can.elf verify reset exit'
```

This command has not been exercised on physical Rev D hardware. Verify MCU identity, supply and flash readback. Normal application programming should preserve the two configuration pages; full-chip erase removes them. Version-1/2 configuration is rejected.

UART: adapter TX→J8.2, RX→J8.3, ground→J8.8; 3.3 V, 115200 baud, 8N1; adapter power disconnected.

```sh
python host/sensor_can.py info --port /dev/ttyUSB0
python host/sensor_can.py configure --port /dev/ttyUSB0 \
  --device 17 --invert 1 --debounce 2
```

Device IDs 0–63 must be unique in this Team Use address space. Invert is a 3-bit mask; debounce is 1–100 ms. UART `SET id invert debounce_ms` persists and resets; CAN configuration is volatile. Unconfigured boards stay CAN-silent. **Hardware sensor power is enabled independently of firmware**, including during reset or programming; open power selectors disconnect individual ports.

The independent watchdog is serviced only after the full 1 ms foreground cycle. A >20 ms foreground delay, clock failure, hard fault or PVD low-voltage detection puts CAN into standby; the watchdog provides reset recovery. The single LED pulses approximately 100 ms per second when configured and healthy, or 100 ms per 200 ms for configuration/clock/CAN errors. Rail faults also trigger the fast fault indication. PA3 reads 12 V PG and PA4 reads 5 V FAULT_N, both with internal pullups. A fault clears qualification immediately; recovery needs 100 ms continuously good indications. Counts freeze and debounce is re-baselined during this interval.

Broadcast Disable ID 0 stops telemetry and aborts pending transmissions. Local sampling and hardware sensor power continue. An explicit `RESUME` UART command or CAN resume command re-enables telemetry; reads never do this automatically. See [protocol v3](../docs/CAN_PROTOCOL.md). Host tests cover firmware logic and mocked peripheral boundaries, not actual oscillator startup, electrical timing or STM32 peripheral behavior.
