# Rev C Lite protocol v2

1 Mbit/s classic CAN, extended 29-bit identifiers, 8-byte telemetry. This is an original Team Use protocol, not CTRE Phoenix. Device type=10 (Miscellaneous), manufacturer=8 (Team Use), unique device ID=0–63. Address = `(10 << 24) | (8 << 16) | (API << 6) | device`.

The APIs differ from A/B/B-2 to prevent their rail-monitoring drivers from interpreting Lite frames. Provision each board over 3.3 V UART before connecting multiple boards. An unconfigured board remains CAN-silent; its sensor power hardware is still enabled.

All multibyte fields are little endian. Masks use bits 0–2 for inputs 1–3. Unsupported versions, reserved bits, wrong lengths or stale frames must be reported as unavailable.

| API | Period | Eight-byte payload |
|---|---|---|
| 0x120 status | 10 ms | version=2, sequence, debounced input mask, raw mask, channels=3, capabilities=0x1F, flags, reset flags |
| 0x121 counts 1/2 | 100 ms | two uint32 rising-edge totals |
| 0x122 count 3 | 100 ms | uint32 total, uint32 reserved=0 |
| 0x130 diagnostics | 100 ms | uint32 transmit drops, TEC byte, REC byte, LEC byte, CAN flags byte |
| 0x131 identity | 1000 ms | 2, firmware major=0, minor=3, patch=0, hardware=3, device ID, debounce ms, inversion mask |

Status flags: configured=1, clock healthy=2, CAN initialized=4, bus-off=8. Reset flags: power-on=1, pin reset=2, watchdog=4, software=8. Capabilities bits 0–4 indicate edge counts, runtime configuration, UART persistence, standalone hardware power and broadcast disable. They are **not live power health**. The raw mask is the uninverted sampled comparator state. The debounced mask applies configured logical inversion and debounce. Sequence is an unsigned byte and wraps. Counters wrap at 2^32 and clear on reset; runtime configuration preserves totals.

Diagnostic LEC is the STM32 three-bit last-error code (0–7); CAN flags are bus-off=1 and error-passive=2. There is no sensor voltage, current or rail-fault telemetry. An absent sensor supply can appear as an ordinary input state.

| Command API | Payload | Effect |
|---|---|---|
| 0x220 runtime input config | `53 43 02 invert debounce_lo debounce_hi 00 00` | invert 0–7; debounce 1–100 ms; volatile, does not change ID |
| 0x221 resume telemetry | `53 43 02 00 00 00 00 00` | Explicitly resume after broadcast disable |

Extended arbitration ID **0** is the FRC broadcast disable. Firmware stops telemetry and aborts pending transmit mailboxes immediately on processing it. Sampling and standalone sensor power continue; there are no actuator outputs. Resume requires the explicit command above, UART `RESUME`, or reset. Drivers never resume from a read loop. Integrate explicit resume with a reviewed robot lifecycle policy; this implementation still requires robot-bus testing and does not establish competition approval. See [WPILib CAN addressing](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html).

Read timeouts: status 100 ms, counters/diagnostics 350 ms, identity 1500 ms. Counters 1/2 and 3 are separate snapshots. Sampling is 1 kHz; debounce requires a continuously stable logical state for the selected interval. This is not a high-speed pulse counter or encoder.

UART: 115200 baud, 8N1, 3.3 V logic. Commands `INFO`, `HELP`, `SET id invert debounce_ms`, `RESUME`. `SET` saves a version-2 redundant CRC-protected record and resets. The old four-argument command and old flash record are rejected. No power-control command exists.
