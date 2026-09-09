# CAN setup and firmware updates

Rev H firmware **0.9.0**, bootloader **1.1.0**, service protocol **1**. Normal sensor messages remain protocol **4**, hardware **8**. Implemented and software-tested; actual STM32/robot-controller, power-cut and vibration qualification is pending. This is our own service protocol, not GrappleHook-compatible firmware.

## First installation and recovery

Install [factory.hex](../firmware/build/factory.hex) once through SWD using [program_factory.tcl](../tools/program_factory.tcl). This combines the protected bootloader, relocated application and image manifest. Rev H requires its own factory image and fresh configuration. D/D2 hardware cannot gain the new bias circuit through firmware. The script preserves the two configuration pages and refuses an unexpected device/flash size or an already protected bootloader. Its hardware execution is a pilot qualification gate.

From `current`, with J8 wired per the custom mapping and a separately powered, current-limited board:

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -f tools/program_factory.tcl
```

Power cycle afterward and verify `boot_protected: true` using the tool. Write protection covers flash pages 0–7 (OpenOCD protection blocks 0–1). Updating requires those blocks locked and application/configuration blocks writable. The script does not change readout protection or mass-erase configuration. Do not program `sensor_can.elf` or `.hex` alone as an initial install: these are relocated application-only files without the boot-valid manifest. Do not upload `factory.hex` over CAN.

Normal CAN updates use [application.sc12](../firmware/build/application.sc12). If interrupted, retry the complete file: there is no old-image rollback or cross-session resume. Invalid images remain in the bootloader. A normal boot gives a 500 ms discovery opportunity; an explicit boot request stays there, and three successive watchdog resets before two healthy application seconds also request recovery. `run` exits a valid bootloader image. SWD remains the recovery path for bootloader/option-byte damage or a nonfunctional CAN connection.

## Laptop and robot use

Use Python 3.10+; the robot tunnel transport needs only the standard library. SocketCAN additionally needs `python-can`; configure the adapter for classical CAN at 1 Mbit/s. Tk is required only for the desktop window (`python3-tk` on many Linux distributions).

The robot bridge runs in a background thread alongside robot code. Copy `ServiceBridge.java` and the adapter for your WPILib year from [examples/bridge](../examples/bridge/README.md). It listens only on `127.0.0.1:5810`; access it over an authenticated SSH tunnel. The 2026 adapter requires an explicit maintenance-request flag **and** Driver Station disabled state for every transmission. The 2027 alpha-7 adapter uses `RobotState` and an explicit `CANPort`, compiled separately with JDK 25. Choose a classical-CAN-compatible bus; this MCU cannot transmit CAN FD.

Keep the robot disabled, mechanically secure it and keep outputs inhibited in your robot code throughout maintenance. The bridge rejects or disconnects when permission/disabled state is lost; it cannot prevent someone enabling the robot at the Driver Station. No robot program is stopped or redeployed by this tool. Do not expose this unauthenticated TCP framing directly on a network. The sensor protocol itself has no authentication; CRC detects corruption, not a malicious uploader.

Example using a roboRIO reached over USB; use your controller's actual address/account:

```sh
ssh -N -L 5810:127.0.0.1:5810 lvuser@172.22.11.2
python host/can_service.py --bridge localhost:5810 discover
python host/service_gui.py
```

Copy the desired 24-hex-digit UID from discovery. Replace `UID` below with it:

```sh
python host/can_service.py --bridge localhost:5810 blink --uid UID
python host/can_service.py --bridge localhost:5810 configure \
  --uid UID --device 17 --invert 0 --debounce 2 --modes npn,pnp,push-pull
python host/can_service.py --bridge localhost:5810 update \
  --uid UID --file firmware/build/application.sc12
```

Direct SocketCAN uses `--channel can0`. Other commands: `info`, `run`, `rate --milliseconds 10|20|50`. Settings persist after save/reset; status period resets to 10 ms. Existing driver timeout is 100 ms. Traffic is 231/131/71 frames/s at 10/20/50 ms; verify bus jitter physically.

Discovery resolves the complete STM32 96-bit UID independently of assigned CAN IDs, including blank and duplicate-ID devices. Blink confirms physical selection. Before a change, the tool reads back all three UID words. ID conflict checks cover **responding SC12 devices only**; a powered-off board or another Team Use product can still have a conflicting address. Use one maintenance client per CAN network. The service APIs must be reserved against other Team Use devices.

Opening a session suppresses normal telemetry on all participating SC12 boards, and freezes/rebaselines input counts. Application rail supervision continues during maintenance; the bootloader keeps both rails disabled. Drivers may retain their last sample until its normal freshness timeout; robot code must treat maintenance as unavailable immediately. Close/lease expiry restores normal sampling/telemetry unless Broadcast Disable previously latched it off. Broadcast Disable cancels maintenance and pending transmissions; explicit resume remains necessary for that latch. Never interpret a missing sample as a false input.

## Wire protocol

Classical CAN, extended identifiers, eight data bytes, no RTR. Request ID `0x0A08C000`, response ID `0x0A08C040` (Team Use 8, miscellaneous type 10, APIs 0x300/0x301, address 0). Payload: opcode byte, sequence byte, nonzero little-endian session token (16 bits), little-endian value (32 bits). Response opcode OR 0x80 means success; OR 0xC0 means error. Echo sequence/token and validate the expected value. Errors 1–5 mean argument, state/offset, flash, image, and missing boot protection. No reply means an unmatched session/selection or transport failure.

| Operation | Value / result |
|---|---|
| OPEN 0x01 | Magic 0x314D4353; broadcast ACKs are identical; five-second lease |
| PREFIX0/1/2 0x02–04 | Three raw UID words; no ACK; each change clears selection |
| PROBE 0x05 | Prefix length 0–96, MSB first within each UID byte; matching nodes reply 1; only 96 selects |
| CLOSE 0x06 | End session, no ACK |
| INFO 0x10 | Index 0 flags/versions, 1 settings, 2 mode version, 3 upload offset, 4 capacity, 5 image validity, 6–8 UID words, 9 persistent input configuration, 10 rail millivolts, 11 rail states |
| BLINK 0x11 | Zero; three-second identify LED |
| SAVE 0x12 | ID/invert/debounce/reserved bytes; reserved must be zero; explicit save then reset |
| BOOT / RUN 0x13/14 | Zero; enter bootloader / run verified application |
| RATE 0x15 | 10, 20 or 50 ms; volatile status period |
| INPUTS 0x16 | Stage validated per-input configuration; commit with SAVE; cleared on new selection/session |
| POWER 0x17 | Application only, selected UID: mask 1=12 V, 2=5 V, 3=both; disable then restart requested rails |
| SIZE / CRC 0x20/21 | Padded application length and CRC32; bootloader only |
| BEGIN 0x22 | Product/layout tag 0x53433138; invalidate/read back manifest before application writes |
| OFFSET / DATA 0x23/24 | Byte offset then four image bytes; ACK next offset after flash readback |
| FINISH 0x25 | Zero; validate complete flash CRC/vectors, commit manifest last, ACK image CRC |

INFO index 0 packs service version in bits 0–7, bootloader mode in bit 8, configured in bit 9, boot protection in bit 10, application minor 9 in bits 16–23, and hardware 8 in bits 24–31. Index 1 packs ID/invert/debounce/status-period as bytes; unconfigured ID is 255. Index 2 is major/minor/patch in bits 16/8/0. Index 5 returns 0 or 1.

INFO index 10 packs measured 12 V millivolts in bits 0–15 and 5 V millivolts in bits 16–31. Index 11 packs enabled/good/latched/pending masks in bytes 0/1/2/3; mask bit 0 is 12 V and bit 1 is 5 V. Bootloader replies do not imply powered rails. Millivolt data is ADC-based and needs physical calibration verification.

After removing a sensor-power fault, restart only the required rail:

```sh
python host/can_service.py --bridge localhost:5810 power-reset --uid UID --rail 12v
```

`--rail 5v` and `--rail both` are also supported. The desktop tool exposes **Reset power fault** and displays both voltages. Reset is explicit; the application does not repeatedly retry a short. Firmware uses 10/60 ms off-to-enable delays and requalifies the rail before reporting usable inputs. A persistent fault latches off again. The outputs have no active discharge, so this clears protection without guaranteeing a complete power cycle of every sensor.

Host discovery walks binary UID prefixes; matching responders send identical presence frames. Prefix frames are paced; UID readback guards selection before writes. Queries retry four times, probes twice; default pacing is at least 6 ms between requests and a 300 ms ACK timeout. Binary discovery can take seconds per device; intermittent connectivity can omit a node, so repeat discovery before commissioning. Uploads send OFFSET and DATA for each four-byte word, bounding throughput and working around flash stalls. Only the immediately previous exact request is cached; offset/data logic also accepts an identical last word without rewriting it. Gaps, changed duplicate words and stale sessions are rejected.

## Image and memory layout

| Region | Address / size |
|---|---|
| Write-protected bootloader | 0x08000000 / 8 KiB |
| Application | 0x08002000 / 21 KiB |
| Image manifest | 0x08007400 / 1 KiB |
| Configuration A/B | 0x08007800 / 0x08007C00, 1 KiB each |
| Reserved SRAM | First 256 bytes: 192-byte vector table, validated recovery cookie |

Both linkers reserve at least 1 KiB stack, excluding static data; runtime stack high-water measurement remains pending. The Cortex-M0 application copies vectors to SRAM and remaps them; bootloader handoff clears pending interrupts, stops SysTick/CAN and returns clocks to HSI. [Compiled-register tests](../reports/firmware-arm-registers.json) check vector copying, GPIO/CAN and configuration writes against peripheral models; they do not emulate analog effects or real interrupt timing.

The update file uses `<8s6I`: `SC12UPD1`, format 1, hardware 8, application address, padded length, CRC32, packed version, then image bytes. Length is 192–21504 bytes and a multiple of four. Initial SP must be aligned and within application SRAM, and Thumb reset PC inside application executable bounds. Manifest words are magic 0x49324353, size, CRC, product tag, CRC of the first four words, and final commit 0xC035A19E. Boot verifies manifest, vectors and full application CRC. No update command can write bootloader, configuration or option-byte regions.

## Evidence and remaining gates

Tests execute the actual portable C engine with simulated flash, including 2,148 halfword erase/program power-cut positions on a two-page image, retries, corrupt files, wrong sizes, gaps, stale sessions, duplicate IDs and running-version verification. Compiled ARM tests exercise register intent and 34 configuration halfword interruption cases. Real TCP tests cover fragmentation and permission revocation with mock CAN. The Python uploader/GUI, bridge and firmware need end-to-end testing on real hardware before robot use. See [qualification](VALIDATION.md) and [unit programming/test fixture](FIXTURE.md).

The `--modes` option and GUI persist independent input modes and active conditions using INFO 9 / INPUTS 0x16. Omitted modes preserve the existing persistent word; a runtime 0x222 change is not implicitly saved. SAVE commits ID, inversion, debounce and staged input settings together. See [input modes](INPUT_MODES.md).
