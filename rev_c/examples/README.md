# Rev C Lite robot integration

These drivers are for **protocol v2 / hardware 3 only**. Do not use the A/B/B-2 driver. Java classes are named `SensorCanLite` / `SensorCanLiteCodec`; C++ uses the `sensorcanlite` namespace. They compile against WPILib 2026.2.1. Python UART/SocketCAN tools are under `host/`.

Copy both Java files from `java/src/main/java/frc/robot/sensors/` into the matching package in a robot project. Construct the driver once, with the unique ID configured over UART:

```java
private final SensorCanLite sensor = new SensorCanLite(17);

// In periodic(): inspect a fresh sample; empty means unavailable.
var sample = sensor.status();
if (sample.isPresent()) {
    var s = sample.get().value();
    if (s.configured() && s.clockHealthy() && s.canHealthy()) {
        boolean signal1 = s.input(1);
        // Display/use this signal with the application's sensor-fault policy.
    }
}
```

C++: copy `cpp/include/SensorCanLite*.h`; see the compiled `cpp/ReadSensorExample.cpp`. Read methods return `std::optional`; Java returns `Optional`. A missing, stale or malformed frame is unavailable, not false. Read timeout is 100 ms for status, 350 ms for counts/diagnostics and 1500 ms for identity.

**A valid CAN status does not prove the sensor has power.** Rev C intentionally removed rail monitoring. An unpowered sensor or latched rail can look inactive. Applications that move actuators must account for sensor supply/wiring faults independently. These examples only acquire input signals.

Runtime inversion/debounce changes are explicit and volatile. After broadcast disable, call `resumeTelemetry()` / `ResumeTelemetry()` only as an explicit reviewed lifecycle action; never continuously from `periodic()`. No driver read sends packets or changes sensor power. Sensor power cannot be switched through this protocol.

```sh
# Provision using a mapped 3.3 V UART adapter; install pyserial first.
python host/sensor_can.py configure --port /dev/ttyUSB0 --device 17 --invert 1 --debounce 2
# Passive monitor on an already configured 1 Mbit/s SocketCAN interface; requires python-can.
python host/sensor_can.py monitor --channel can0 --device 17
```

`bash scripts/test_drivers.sh` compiles Java/C++ against cached, checksum-pinned WPILib dependencies and runs host tests. Fetch dependencies with `python tools/fetch_driver_dependencies.py`. Real roboRIO/CAN testing remains pending.
