# Robot CAN maintenance bridge

Copy `src/frc/robot/maintenance/ServiceBridge.java` plus **one** year adapter into your robot project's matching package. WPILib 2026.2.1 uses `Wpilib2026.java` and Java 17. The separately compiled `wpilib2027/.../Wpilib2027.java` targets **2027.0.0-alpha-7**, Java 25 and the changed CAN/RobotState APIs. Existing 2026 sensor driver classes are not ported to 2027 by this adapter.

Create once in robot initialization, with a thread-safe opt-in flag that defaults false:

```java
private final java.util.concurrent.atomic.AtomicBoolean maintenanceRequested =
    new java.util.concurrent.atomic.AtomicBoolean(false);
// In robotInit(), catching IOException and reporting it visibly:
bridge = Wpilib2026.start(maintenanceRequested::get);
// 2027 instead: Wpilib2027.start(yourActualCANPort, maintenanceRequested::get);
```

Provide an explicit local maintenance action to set the flag while disabled. Keep outputs inhibited while that flag is true and refuse normal operation until maintenance ends and required sensors return healthy. The adapter independently rechecks disabled state before each write. Do not wire the flag to a permanently true supplier or enable it automatically from periodic. Clear it after service; close the bridge on shutdown. `isConnected()` and `lastError()` can be displayed on your dashboard.

Only SC12 APIs 0x300/0x301 are accessible; this is not a general CAN proxy. Bind is IPv4 localhost port 5810, single client, five-second inactivity timeout, maximum 200 request frames/s. A client gets a byte stream of eight-byte requests/responses, with no extra framing. Authentication comes from the SSH tunnel. Socket fragmentation is supported. Disconnect/timeout sends CLOSE while still authorized; revoking permission immediately stops writes and device leases expire naturally. Robot code remains running. Actual controller/HAL/CAN timing tests remain pending.

See the [complete setup and update instructions](../../docs/CAN_SERVICE.md). Compilation dependencies are SHA-256 pinned in `tools/driver_dependencies.json` and `tools/bridge2027_dependencies.json`; run `scripts/test_drivers.sh` and `CANDI_JDK25=/path/to/jdk25 bash scripts/test_bridge2027.sh` from the revision root.
