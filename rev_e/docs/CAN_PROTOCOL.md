# Rev E SC12 protocol v4

1 Mbit/s classic CAN, extended 29-bit identifiers, 8-byte telemetry. This is an original Team Use protocol, not CTRE Phoenix. Device type=10 (Miscellaneous), manufacturer=8 (Team Use), unique device ID=0–63. Address = `(10 << 24) | (8 << 16) | (API << 6) | device`.

The APIs differ from A/B/B-2; Rev C shares these API numbers but uses protocol v2, which Rev E drivers reject. The version and capability checks prevent drivers from interpreting the wrong revision’s payload. Provision each board by full-UID CAN service or 3.3 V UART. An unconfigured board suppresses telemetry but answers service requests; its sensor power hardware is still enabled.

All multibyte fields are little endian. Masks use bits 0–2 for inputs 1–3. Unsupported versions, reserved bits, wrong lengths or stale frames must be reported as unavailable.

| API | Period | Eight-byte payload |
|---|---|---|
| 0x120 status | 10 ms | version=4, sequence, debounced input mask, raw mask, channels=3, capabilities=0x7F, flags, reset flags |
| 0x121 counts 1/2 | 100 ms | two uint32 rising-edge totals |
| 0x122 count 3 | 100 ms | uint32 total, uint32 reserved=0 |
| 0x130 diagnostics | 100 ms | uint32 transmit drops, TEC byte, REC byte, LEC byte, CAN flags byte |
| 0x132 input state | Same as status | version=4, valid mask, floating mask, classified HIGH mask, uint32 input configuration |
| 0x131 identity | 1000 ms | 4, firmware major=0, minor=6, patch=0, hardware=5, device ID, debounce ms, inversion mask |

Status flags: configured=1, clock healthy=2, CAN initialized=4, bus-off=8, qualified 12 V power-good=16, qualified 5 V no-fault=32, all input classifications settled=64. Reset flags: power-on=1, pin reset=2, watchdog=4, software=8. Capabilities bits 0–4 indicate edge counts, runtime configuration, UART persistence, standalone hardware power and broadcast disable. Bit 5 indicates rail-health reporting capability; bit 6 indicates software bias/classification. Capabilities are static; flags bits 4/5 carry live qualified indications. The raw mask is the classified HIGH mask, excluding float probe transitions; check the valid mask in 0x132 before interpreting it. The debounced mask applies the active-state condition, inversion and debounce. Sequence is an unsigned byte and wraps. Counters wrap at 2^32 and clear on reset; runtime configuration preserves totals.

Diagnostic LEC is the STM32 three-bit last-error code (0–7); CAN flags are bus-off=1 and error-passive=2. There is no calibrated sensor voltage/current telemetry. The 12 V PG signal has the converter’s typical threshold and tolerances; 5 V no-fault is an overcurrent-switch indication, not proof of voltage. Raw masks remain diagnostic data during faults.

A bad rail indication clears its flag at the next 1 ms sample; restoration needs 100 consecutive good samples. During faults and recovery, firmware re-baselines input debounce and freezes edge totals, preventing supply collapse/recovery from adding counts. All ports require both rail indications because sensor-power cap positions are not readable. Java/C++ input helpers also require fresh telemetry, configuration, clock health and CAN health and all classifications settled. They cannot detect every failed/disconnected sensor or open cable.

| Command API | Payload | Effect |
|---|---|---|
| 0x220 runtime input config | `53 43 04 invert debounce_lo debounce_hi 00 00` | invert 0–7; debounce 1–100 ms; volatile, does not change ID |
| 0x222 runtime bias | `53 43 04 00` + uint32 configuration | Volatile, re-baselines input classification; read back 0x132 |
| 0x221 resume telemetry | `53 43 04 00 00 00 00 00` | Explicitly resume after broadcast disable |

Extended arbitration ID **0** is the FRC broadcast disable. Firmware stops telemetry and aborts pending transmit mailboxes immediately on processing it. Sampling and standalone sensor power continue; there are no actuator outputs. Resume requires the explicit command above, UART `RESUME`, or reset. Drivers never resume from a read loop. Integrate explicit resume with a reviewed robot lifecycle policy; this implementation still requires robot-bus testing and does not establish competition approval. See [WPILib CAN addressing](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html).

Read timeouts: status 100 ms, counters/diagnostics 350 ms, identity 1500 ms. Counters 1/2 and 3 are separate snapshots. Sampling is 1 kHz; debounce requires a continuously stable logical state for the selected interval. This is not a high-speed pulse counter or encoder.

UART: 115200 baud, 8N1, 3.3 V logic. Commands `INFO`, `HELP`, `SET id invert debounce_ms`, `RESUME`. `SET` saves a version-4 redundant CRC-protected record and resets. The old four-argument command and earlier flash records are rejected; provision Rev E explicitly. No power-control command exists.

## Service extension in firmware 0.6.0

Rev E changes normal telemetry to protocol 4; use only the matching drivers. APIs 0x300/0x301 at address 0 are reserved for [CAN service](CAN_SERVICE.md). Opening maintenance pauses telemetry/counting on participating SC12 nodes; treat samples as unavailable immediately in robot code. Status period can be 10/20/50 ms until reset.

## Per-input configuration word

Bits 0–2, 3–5 and 6–8 select channels 1–3 mode: 0=OFF, 1=PULL_HIGH, 2=PULL_LOW, 3=FLOAT_DETECT, 4=BUS_KEEPER. Bits 9–11, 12–14 and 15–17 select each active condition: 0=HIGH, 1=LOW, 2=DRIVEN, 3=FLOATING, 4=NOT_HIGH, 5=NOT_LOW. Bits 18–31 must be zero; other enum values are invalid. Default word zero means push-pull/HIGH on all channels.

Input state 0x132: a cleared valid bit means UNKNOWN regardless of the retained high/floating bit. For a valid channel, floating takes its own state, high means HIGH, otherwise LOW. High/floating masks never overlap. Validity/classification precedes active-state mapping, inversion and debounce. See [mode timing and electrical limits](INPUT_MODES.md).

At the default 10 ms period, telemetry is 231 frames/s; 20/50 ms give 131/71 frames/s. Status and input state are separate snapshots. Read timeouts are 100 ms for both; 350 ms for counts/diagnostics and 1500 ms for identity. Runtime configuration does not reset counters or persist to flash. Measurements settle after a mode change before further edges are counted.
