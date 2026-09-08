**Robot integration — WPILib 2026.2.1**

The Java and C++ interfaces read this board's original Team Use CAN protocol. They compile against WPILib 2026.2.1 APIs. Host tests replace the transport boundary; an actual roboRIO integration test remains required.

For Java, copy `java/src/main/java/frc/robot/sensors/SensorCan.java` and `SensorCanCodec.java` into the matching package in a Java 17 robot project. Construct one `SensorCan` per physical board as a subsystem member, using the ID provisioned through UART. `status()`, `diagnostic()`, `counts12()`, `counts34()` and `identity()` return `Optional<Sample<...>>`. Missing, malformed or stale data returns empty. Close the object when disposing the subsystem.

For C++, copy the two headers from `cpp/include` into the robot project and construct `sensorcan::SensorCan` as a subsystem member. `ReadStatus()`, `ReadDiagnostic()`, `ReadCounts12()`, `ReadCounts34()` and `ReadIdentity()` return `std::optional<Sample<...>>`. The class uses the project's normal WPILib CAN library; no additional runtime library is required.

The intake examples in both languages assume channel 1 is logically TRUE when a game piece is present, with a battery-powered sensor requiring at least 10 V. They permit intake only when fresh status and diagnostics exist, configured/clock/ADC flags are healthy, battery power is enabled without a fault, switched battery output reports at least 11 V, and the piece is absent. The 11 V check is an example allowance for switch/wiring drop and diagnostic error; measure your actual sensor and adjust its policy deliberately. Neither example is a complete motor-control subsystem.

Reading data never enables sensor power or clears faults. `configureRuntime` / `ConfigureRuntime` sends one volatile configuration request; `clearFaults` / `ClearFaults` sends one explicit recovery attempt. Do not call either continuously from periodic code. Verify the resulting status/identity, and expose failures to the driver station. A constructor or successful packet write does not prove the board is present.

Status expires after 100 ms; counter/diagnostic packets after 350 ms; identity after 1500 ms. Counters are unsigned 32-bit totals and wrap. Java represents them as `long`; C++ uses `uint32_t`. Counter pairs arrive separately. Do not use these 1 kHz debounced inputs as high-speed encoders or rely on them as a safety interlock.

The Python service tool can also passively monitor a Linux SocketCAN interface already configured for 1 Mbit/s:

```sh
python host/sensor_can.py monitor --channel can0 --device 17 --seconds 30
```

Configure the CAN adapter using its own supported procedure. The monitor sends no commands and reports unavailable status after 100 ms without a valid frame. UART provisioning is described in [firmware/README.md](../firmware/README.md).

Run `bash scripts/test_drivers.sh` from the project root to compile and exercise Java, C++ and Python integrations using the installed toolchain. No LabVIEW VI is supplied; a LabVIEW implementation would need to implement the documented packets, freshness checks and fault policy, then be tested on the robot. This project does not claim complete ecosystem certification.
