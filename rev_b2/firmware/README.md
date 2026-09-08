# Firmware 0.2.0 — hardware revision B

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Bare-metal STM32F042K6 firmware for three inputs. The fourth protocol channel is reserved and always zero. Two final 1 KiB flash pages hold redundant CRC-protected configuration. The image uses 7,148 bytes of flash and 1,832 bytes of RAM including reserved stack; these are linker allocations, not measured stack depth.

From `rev_b2/`:

```sh
source tools/env.sh
make -C firmware
bash scripts/test_firmware.sh
```

The build produces `firmware/build/sensor_can.elf`, `.hex`, and `.bin`. Host tests simulate peripheral boundaries; they do not qualify real STM32 registers or wiring.

Power J1 from a current-limited bench supply. Use the custom TC2050 adapter in [WIRING.md](../docs/WIRING.md): probe VTref sense→J8.6, SWDIO→5, SWCLK→4, ground→7, optional reset→1. Leave probe power disconnected. The mechanical footprint is standard TC2050-IDC-NL; the electrical mapping is custom.

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c 'adapter speed 1000' \
  -c 'program firmware/build/sensor_can.elf verify reset exit'
```

This has not been exercised on physical Rev B/B-2 hardware. Verify target identity, voltage and flash readback. Normal application updates preserve configuration; a full-chip erase removes it.

For UART, connect a 3.3 V adapter's TX→J8.2, RX→J8.3, ground→J8.8 or 10. Leave adapter power disconnected. UART is 115200 baud, 8N1.

```sh
python host/sensor_can.py info --port /dev/ttyUSB0
python host/sensor_can.py configure --port /dev/ttyUSB0 \
  --device 17 --invert 1 --debounce 2 --rails 0
```

Device IDs are 0–63 and must be unique for this Team Use protocol. Rev B/B-2 inversion masks are 0–7; bit 0 is sensor 1. Debounce is 1–100 ms. Rail masks: 0=off, 1=5 V, 2=VBAT, 3=both. Voltage selection is physical. UART `SET id invert debounce_ms rails` disables rails, writes configuration, and resets. A stored nonzero rail mask enables those rails after ordinary startup; provision rails=0 until wiring is verified. Avoid repeated persistent writes from robot code.

Unconfigured boards keep both rails off and CAN in standby. Valid configuration enables the original 1 Mbit/s, 29-bit Team Use protocol. Inputs are sampled at 1 kHz; counters report debounced logical rising edges. Input LEDs show logical state. This is not an encoder, IO-Link or analog-input device.

Hardware pulldowns establish off defaults. Clock failure, hard fault, PVD low voltage and a foreground stall longer than 20 ms force rails off; the independent watchdog provides reset recovery. Enabled rails below a measured 4.5 V latch off after startup blanking. Battery light-load FAULT is distinguished using output voltage. Broadcast Disable turns both rails off and clears the requested rail state. Recovery needs an explicit rail request and fault clear after the off-time requirement. Do not continuously retry faults.

CAN initialization failure can leave deliberately configured sensor power requested while communication is unavailable. Robot code must check fresh status, diagnostics and the sensor's supply requirements. Reading data never enables power. See [CAN_PROTOCOL.md](../docs/CAN_PROTOCOL.md) for packets and recovery policy.
