# Rev F robot drivers and host utility

Java 17 and C++ examples target WPILib 2026.2.1. Rev F uses protocol **4**, hardware **6** and firmware **0.7.0**. Use the matching `SensorCan12` and `SensorCan12Codec` files; older revisions are rejected. Provision a unique device ID through CAN service or UART.

Choose each sensor's 5 V / 12 V supply using the physical jumper before operation; the drivers do not select port voltage. See the [Rev F setup guide](../README.md) and [wiring](../docs/WIRING.md).

CAN discovery, persistent settings and firmware updates are provided by the new [service tools](../docs/CAN_SERVICE.md). The [robot bridge](bridge/README.md) has separately compiled 2026 and 2027 alpha-7 adapters. Sensor driver classes below remain pinned to 2026.2.1; the 2027 bridge does not port the normal drivers. Physical end-to-end CAN testing is pending.

```java
private final SensorCan12 sensorBoard = new SensorCan12(17);
// In periodic(): absent means unavailable or a reported fault.
var detected = sensorBoard.input(1);
if (detected.isPresent()) {
  boolean sensorActive = detected.get();
  // Use a reviewed subsystem policy for this observation.
}
```

C++: `sensorcan12::SensorCan12 board{17};` then `board.ReadInput(1)` returns `std::optional<bool>`. Construct the driver once; an empty result must not silently become a valid “no object” observation. The helper requires fresh status, configured identity state, healthy clock/CAN and both qualified power indications. Raw `status()` / `ReadStatus()` remains available to diagnose faults. Counts are frozen during power faults and wrap at 2^32; compare/reset policy in the robot application.

Reads do not transmit or resume telemetry. `configureRuntime` / `ConfigureRuntime` sends volatile input inversion/debounce; it does not set persistent ID. `resumeTelemetry` / `ResumeTelemetry` is an explicit action after investigating broadcast disable, not a periodic automatic retry. Status timeout is 100 ms; count/diagnostic timeout 350 ms; identity timeout 1500 ms.

The Python [host tool](../host/sensor_can.py) supports UART `info`, `configure`, `resume` and passive CAN `monitor`. UART uses 3.3 V levels at 115200 8N1; disconnect adapter power. CAN monitor requires a suitable external CAN interface; a UART adapter is not a CAN interface. Run the following from `current/`:

```sh
source tools/env.sh
python host/sensor_can.py configure --port /dev/ttyUSB0 --device 17 --invert 1 --debounce 2
python host/sensor_can.py monitor --interface socketcan --channel can0 --device 17
bash scripts/test_drivers.sh
```

Tests cover codec boundaries, all reserved status bits, stale/malformed responses, fault rejection, unsigned counts and explicit-only writes. The C++ example compiles against the actual pinned WPILib headers; Java compiles against pinned WPILib jars. Hardware bus behavior and competition acceptance remain open qualification steps. See [protocol](../docs/CAN_PROTOCOL.md), [wiring](../docs/WIRING.md), and [validation](../docs/VALIDATION.md).

## Independent input modes

Use the desktop service tool to persist per-input settings. Runtime Java example (volatile; verify `inputState()` readback):

```java
sensor.configureInputsRuntime(
    new SensorCan12Codec.InputMode[] {
        SensorCan12Codec.InputMode.PULL_HIGH,
        SensorCan12Codec.InputMode.PULL_LOW,
        SensorCan12Codec.InputMode.OFF},
    new SensorCan12Codec.ActiveWhen[] {
        SensorCan12Codec.ActiveWhen.LOW,
        SensorCan12Codec.ActiveWhen.HIGH,
        SensorCan12Codec.ActiveWhen.HIGH});
```

C++ exposes `ConfigureInputsRuntime` with `std::array<InputMode,3>` and `std::array<ActiveWhen,3>`, and `ReadInputState()` for classification/configuration. `input()` / `ReadInput()` require fresh, healthy status and all inputs settled. Level helpers return UNKNOWN when the channel valid bit is clear. See [mode behavior and electrical limits](../docs/INPUT_MODES.md).
