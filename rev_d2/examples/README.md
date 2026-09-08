# Rev D robot drivers and host utility

Java 17 and C++ examples target WPILib 2026.2.1. Rev D uses protocol **3**, firmware **0.4.0**, hardware **4**. Rev C Lite frames and the earlier four-input protocols are rejected. Copy the relevant `SensorCan12` and `SensorCan12Codec` files into a robot project, then set the same unique device ID provisioned over UART.

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

The Python [host tool](../host/sensor_can.py) supports UART `info`, `configure`, `resume` and passive CAN `monitor`. UART uses 3.3 V levels at 115200 8N1; disconnect adapter power. CAN monitor requires a suitable external CAN interface; a UART adapter is not a CAN interface.

```sh
source tools/env.sh
python host/sensor_can.py configure --port /dev/ttyUSB0 --device 17 --invert 1 --debounce 2
python host/sensor_can.py monitor --interface socketcan --channel can0 --device 17
bash scripts/test_drivers.sh
```

Tests cover codec boundaries, all reserved status bits, stale/malformed responses, fault rejection, unsigned counts and explicit-only writes. The C++ example compiles against the actual pinned WPILib headers; Java compiles against pinned WPILib jars. Hardware bus behavior and competition acceptance remain open qualification steps. See [protocol](../docs/CAN_PROTOCOL.md), [wiring](../docs/WIRING.md), and [validation](../docs/VALIDATION.md).
