package frc.robot.sensors;

import edu.wpi.first.hal.CANData;
import edu.wpi.first.wpilibj.CAN;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;

/**
 * WPILib 2026 / Java 17 driver. Copy this and SensorCan12Codec into a robot project.
 * Reads never transmit or resume telemetry. A missing/malformed/old frame returns Optional.empty().
 * Calls are intended from the robot's main periodic thread.
 */
public final class SensorCan12 implements AutoCloseable {
  public static final int STATUS_TIMEOUT_MS = 100;
  public static final int COUNTS_TIMEOUT_MS = 350;
  public static final int DIAGNOSTIC_TIMEOUT_MS = 350;
  public static final int IDENTITY_TIMEOUT_MS = 1500;

  public record Sample<T>(T value, long canTimestampMillis) {}
  record Packet(byte[] data, long timestampMillis) {}
  interface Transport extends AutoCloseable {
    /** Return null when no frame exists within timeout; do not return cached stale data. */
    Packet read(int api, int timeoutMillis);
    void write(int api, byte[] data);
    @Override void close();
  }
  private static final class WpilibTransport implements Transport {
    private final CAN can;
    WpilibTransport(int id) {
      SensorCan12Codec.range(id, 0, 63, "device ID");
      can = new CAN(id, SensorCan12Codec.MANUFACTURER, SensorCan12Codec.DEVICE_TYPE);
    }
    @Override public Packet read(int api, int timeoutMillis) {
      CANData data = new CANData();
      if (!can.readPacketTimeout(api, timeoutMillis, data)) return null;
      if (data.length != 8) return null;
      return new Packet(Arrays.copyOf(data.data, 8), data.timestamp);
    }
    @Override public void write(int api, byte[] data) { can.writePacket(data, api); }
    @Override public void close() { can.close(); }
  }
  private final Transport transport;
  private final int deviceId;
  private boolean closed;

  public SensorCan12(int deviceId) { this(deviceId, new WpilibTransport(deviceId)); }
  SensorCan12(int deviceId, Transport transport) {
    SensorCan12Codec.range(deviceId, 0, 63, "device ID");
    this.deviceId = deviceId;
    this.transport = Objects.requireNonNull(transport);
  }
  private <T> Optional<Sample<T>> read(int api, int timeout, Function<byte[], T> decoder) {
    ensureOpen();
    Packet packet = transport.read(api, timeout);
    if (packet == null) return Optional.empty();
    try {
      return Optional.of(new Sample<>(decoder.apply(packet.data()), packet.timestampMillis()));
    } catch (IllegalArgumentException invalidFrame) {
      return Optional.empty();
    }
  }
  public Optional<Sample<SensorCan12Codec.InputState>> inputState() {
    return read(SensorCan12Codec.INPUT_STATE, STATUS_TIMEOUT_MS, SensorCan12Codec::inputState);
  }
  /** Volatile; verify inputState(). Use desktop service to persist settings. */
  public void configureInputsRuntime(SensorCan12Codec.InputMode[] modes, SensorCan12Codec.ActiveWhen[] active) {
    ensureOpen(); transport.write(SensorCan12Codec.INPUT_CONFIG, SensorCan12Codec.inputConfiguration(modes,active));
  }
  public Optional<Sample<SensorCan12Codec.Status>> status() {
    return read(SensorCan12Codec.STATUS, STATUS_TIMEOUT_MS, SensorCan12Codec::status);
  }
  /** Empty on stale telemetry or any reported rail, clock, CAN or configuration fault. */
  public Optional<Boolean> input(int channel) {
    SensorCan12Codec.range(channel, 1, 3, "channel");
    return status().filter(s -> s.value().usable()).map(s -> s.value().input(channel));
  }
  /** Counts are unsigned 32-bit rising-edge totals since boot; pairs are sampled separately. */
  public Optional<Sample<SensorCan12Codec.Counts>> counts12() {
    return read(SensorCan12Codec.COUNTS_12, COUNTS_TIMEOUT_MS, SensorCan12Codec::counts);
  }
  public Optional<Sample<SensorCan12Codec.Counts>> count3() {
    return read(SensorCan12Codec.COUNTS_3, COUNTS_TIMEOUT_MS, SensorCan12Codec::count3);
  }
  public Optional<Sample<SensorCan12Codec.Diagnostic>> diagnostic() {
    return read(SensorCan12Codec.DIAGNOSTIC, DIAGNOSTIC_TIMEOUT_MS, SensorCan12Codec::diagnostic);
  }
  public Optional<Sample<SensorCan12Codec.Identity>> identity() {
    return read(SensorCan12Codec.IDENTITY, IDENTITY_TIMEOUT_MS, SensorCan12Codec::identity)
      .filter(sample -> sample.value().deviceId() == deviceId);
  }
  /** Sends once. Verify resulting status/identity; this does not persist through a reset. */
  public void configureRuntime(int invertMask, int debounceMillis) {
    ensureOpen();
    transport.write(SensorCan12Codec.CONFIGURE,
                    SensorCan12Codec.configuration(invertMask, debounceMillis));
  }
  /** Manual action only, after the cause is removed. Do not call repeatedly from periodic(). */
  public void resumeTelemetry() {
    ensureOpen();
    transport.write(SensorCan12Codec.RESUME, SensorCan12Codec.resume());
  }
  private void ensureOpen() {
    if (closed) throw new IllegalStateException("SensorCan12 is closed");
  }
  @Override public void close() {
    if (!closed) { closed = true; transport.close(); }
  }
}
