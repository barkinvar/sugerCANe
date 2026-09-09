# Programming and unit acceptance fixture

Build a reusable fixture around the documented custom TC2050 contacts, ST-Link, a separately current-limited J1 supply, accessible rail test contacts, CAN adapter and three independently driven input fixtures. This document and scripts are ready for the pilot; no physical fixture or unit test has been performed.

Leave voltage caps absent for initial programming. Keep the SWD probe's voltage pin as target reference only. Program/verify the combined image and set boot write protection with [program_factory.tcl](../tools/program_factory.tcl), then power cycle and verify protection over CAN. Save the programmer log, factory image SHA-256, component lot and full MCU UID. The setup checks STM32F04x device ID 0x445, 32 KiB flash and WRP pages 0–7 (OpenOCD protection blocks 0–1, not 0–7), consistent with the [OpenOCD STM32 driver](https://github.com/openocd-org/openocd/blob/master/src/flash/nor/stm32f1x.c). Qualify the exact probe/OpenOCD version on the first unit.

Configure a unique ID through the service tool. Record internal 5 V, logic 3.3 V, protected sensor 5 V and regulated 12 V with a calibrated meter; acceptance windows are 4.8–5.3, 3.15–3.45, 4.65–5.45 and 11.4–12.6 V. These generous unit-screening windows do not replace rail regulation/load/temperature qualification. Power off before fitting selector caps. Exercise each input low and high using the approved bias and compatible test signal; observe fresh protocol-v4 status and count transitions. Verify telemetry after closing maintenance. Power cycle again and verify saved ID/inversion/debounce and all three input modes/active conditions.

Copy [fixture_measurements.template.json](../tools/fixture_measurements.template.json), enter measured voltages and set each check true only after actually observing it. Record live identity/protection plus those results:

```sh
python host/fixture_record.py --channel can0 --uid UID \
  --measurements measured-unit.json --operator NAME --lot LOT \
  --output unit-UID.json
```

Use `--bridge localhost:5810` for a robot tunnel. An incomplete/failed record exits nonzero. Existing output files are never overwritten. The JSON stores operator/lot/time/UID/settings and a hash of the supplied measurements; keep it with the programming log. It does not independently measure voltages or validate operator assertions.

Design qualification still needs 6/12/22 V input tests, both rails at load, shorts, temperatures, representative sensors/cables, vibration, actual flash power cuts, bus-off/controller disconnect and boot/interrupt timing. See [VALIDATION.md](VALIDATION.md). Complete the pilot before calling units production-ready or quoting a qualified manufacturing yield.

Exercise mixed software modes and verify floating detection without false counts using [INPUT_MODES.md](INPUT_MODES.md). Unsettled inputs must not appear as valid robot measurements.

Rev G adds mandatory recorded checks for the U9 exposed-pad joint, rails off in bootloader/reset, ADC readback against a calibrated meter, and each rail shorted then recovered through addressed CAN reset. During first-article qualification also remove MCU power while raw boost is present; verify Q2/Q3 holds the 12 V output off. Use controlled test equipment and load fixtures for these checks; do not count an unperformed test as passed.
