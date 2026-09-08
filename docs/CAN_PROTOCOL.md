**FRC Sensor CAN protocol version 1**

The interface uses 1 Mbit/s Classical CAN with 29-bit extended data frames. It is an original Team Use protocol, with device type 10 (Miscellaneous) and manufacturer 8 (Team Use), following the [WPILib addressing layout](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html). It does not implement CTRE Phoenix or impersonate CTRE hardware. Coordinate IDs with any other team devices using this same type/manufacturer pair.

`identifier = (10 << 24) | (8 << 16) | (api << 6) | device_id`

`device_id` is 0–63, `api` is 0–1023. For example, device 17 status is `0x0A084011`. All team packets below have DLC 8. Multibyte integers are unsigned little-endian. Reserved bytes/bits must be zero. Invalid frame type, length, version, command magic, ranges or reserved bits are rejected. Receive filters reserve a separate FIFO for the standard FRC Broadcast Disable message.

| API | Direction | Period | Bytes 0 through 7 |
| --- | --- | --- | --- |
| 0x100 status | Board → robot | 10 ms | protocol=1, sequence, logical inputs, raw inputs, enabled rails, latched faults, health flags, reset flags |
| 0x101 counts 1/2 | Board → robot | 100 ms | channel 1 uint32, channel 2 uint32 |
| 0x102 counts 3/4 | Board → robot | 100 ms | channel 3 uint32, channel 4 uint32 |
| 0x110 diagnostics | Board → robot | 100 ms | switched battery output mV uint16, sensor 5 V mV uint16, TX queue drops uint16, TEC uint8, REC uint8 |
| 0x111 identity | Board → robot | 1000 ms | protocol=1, firmware major=0, minor=1, patch=0, hardware=1, device ID, debounce ms, inversion mask |
| 0x200 runtime configuration | Robot → board | On explicit change | 0x53, 0x43, 1, inversion mask, debounce low byte, debounce high byte, requested rails, 0 |
| 0x201 clear fault | Robot → board | On explicit request | 0x53, 0x43, 1, clear mask, 0, 0, 0, 0 |

Input bit 0 means channel 1, through bit 3 for channel 4. Raw inputs are comparator levels before inversion and debounce. Logical inputs are the stable, debounced states after XOR with the configured inversion mask. Rising-edge counters count changes to logical TRUE; they start at zero on boot and wrap modulo 2³². Counter-pair frames are separate snapshots, not a four-channel atomic sample. Runtime configuration reinitializes debounce state while preserving counts. Input LEDs show logical state.

Rail bit 0 means regulated 5 V; bit 1 means battery. An enabled bit reports the MCU's commanded switch-enable state, **not measured power-good**. A hardware switch can have shut down before software updates the status. Latched faults require manual recovery. The battery diagnostic measures SENSOR_VBAT after the battery switch. The 5 V diagnostic measures the shared switched 5 V rail. Both are measured on the PCB; cable/connector loss and a disconnected sensor remain outside that measurement. Firmware samples both every 1 ms and latches an enabled rail off below a measured 4.5 V after its 5 ms startup blanking interval. ADC failure latches both rails off. The battery switch also asserts its digital FAULT for healthy loads below 10–20 mA, so battery fault handling uses output voltage while the switch retains autonomous current-limit/latch protection.

Health flags: bit 0 configured, bit 1 clock healthy, bit 2 ADC healthy. Reset flags: bit 0 power-on, bit 1 reset pin, bit 2 independent watchdog, bit 3 software reset; several bits can be set. Diagnostic ADC readings are approximate monitoring values, not calibrated instrumentation. Ignore voltage readings if ADC health is false. TX queue drops count local mailbox submission failures, saturating at 65535; they do not count every unacknowledged or corrupted transmission. TEC and REC are controller error counters.

Debounce is 1–100 ms with 1 kHz sampling. The default service example uses 2 ms. Analog filtering and sample phase add latency; seven typical-model SPICE cases observed roughly 2–3.1 ms transition latency with this setting. No pulse-width, quadrature, encoder speed or minimum-pulse guarantee is established. The status sequence increments modulo 256 and is a freshness aid, not a transaction identifier.

Runtime configuration accepts inversion 0–15 and rails 0–3. It is volatile and does not clear a latched rail. To recover a fault: remove the cause, leave the rail off for at least 100 ms, explicitly request the desired rail state, then explicitly clear its fault bit. Clear masks are 1–3. Do not retry automatically in robotPeriodic. UART `SET` is the only normal persistent configuration operation and resets the board after a verified flash write.

**Timing and short pulses**

Status is a periodic sample, so a brief debounced pulse can occur between 10 ms transmissions. Rising-edge counters retain such events until reset but arrive every 100 ms and have no event timestamps. Local debounce latency also excludes CAN and robot-loop delays. See the [timing and pulse study](TIMING.md) before choosing a sensor geometry or event-handling strategy.

**Broadcast Disable and startup**

Extended data identifier **0x00000000**, with any DLC 0–8, is FRC Broadcast Disable. Firmware immediately commands both rails off, sets both latches and clears requested rails. Communication remains available. Recovery requires an explicit rail request and fault clear after the off-time requirement. Ordinary disabled-state heartbeat does not switch sensor power in this sensor-only design. This device has no actuator outputs.

With no valid flash configuration, CAN remains in standby and sensor rails remain off. Assign a unique ID through UART before connecting several unconfigured boards to a robot. A watchdog reset keeps both sensor rails latched off even if stored configuration requests them. Clock or low-voltage faults force safe shutdown. Automatic CAN bus-off recovery is enabled, but sensor data must still be treated as unavailable when stale.

**Robot-side rules**

Use a 100 ms status freshness limit; this is implemented in the supplied Java and C++ wrappers. Counter/diagnostic freshness is 350 ms and identity freshness is 1500 ms. Missing or invalid packets return no sample. Do not substitute a stale FALSE for a sensor failure. Verify configured, clock and ADC flags, the relevant rail enable/fault bits, and adequate sensor supply before acting. The supplied intake examples fail closed when their assumed 10 V sensor supply margin is absent.

There is no command acknowledgment packet, transaction ID, encryption or authentication. Read status and identity back after configuration. This is intended for a trusted, physically controlled robot CAN bus. Periodic traffic is 131 frames/s; a conservative 160 bits/frame estimate gives about 2.1% bus load per board. Team-controlled command rates should remain low.
