package frc.robot.sensors;

import edu.wpi.first.hal.CANData;
import edu.wpi.first.wpilibj.CAN;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;

/**
 * WPILib 2026 / Java 17 driver. Copy this and SensorCanLiteCodec into a robot project.
 * Reads never transmit or resume telemetry. A missing/malformed/old frame returns Optional.empty().
 * Calls are intended from the robot's main periodic thread.
 */
public final class SensorCanLite implements AutoCloseable {
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
      SensorCanLiteCodec.range(id, 0, 63, "device ID");
      can = new CAN(id, SensorCanLiteCodec.MANUFACTURER, SensorCanLiteCodec.DEVICE_TYPE);
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

  public SensorCanLite(int deviceId) { this(deviceId, new WpilibTransport(deviceId)); }
  SensorCanLite(int deviceId, Transport transport) {
    SensorCanLiteCodec.range(deviceId, 0, 63, "device ID");
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
  public Optional<Sample<SensorCanLiteCodec.Status>> status() {
    return read(SensorCanLiteCodec.STATUS, STATUS_TIMEOUT_MS, SensorCanLiteCodec::status);
  }
  /** Counts are unsigned 32-bit rising-edge totals since boot; pairs are sampled separately. */
  public Optional<Sample<SensorCanLiteCodec.Counts>> counts12() {
    return read(SensorCanLiteCodec.COUNTS_12, COUNTS_TIMEOUT_MS, SensorCanLiteCodec::counts);
  }
  public Optional<Sample<SensorCanLiteCodec.Counts>> count3() {
    return read(SensorCanLiteCodec.COUNTS_3, COUNTS_TIMEOUT_MS, SensorCanLiteCodec::count3);
  }
  public Optional<Sample<SensorCanLiteCodec.Diagnostic>> diagnostic() {
    return read(SensorCanLiteCodec.DIAGNOSTIC, DIAGNOSTIC_TIMEOUT_MS, SensorCanLiteCodec::diagnostic);
  }
  public Optional<Sample<SensorCanLiteCodec.Identity>> identity() {
    return read(SensorCanLiteCodec.IDENTITY, IDENTITY_TIMEOUT_MS, SensorCanLiteCodec::identity)
      .filter(sample -> sample.value().deviceId() == deviceId);
  }
  /** Sends once. Verify resulting status/identity; this does not persist through a reset. */
  public void configureRuntime(int invertMask, int debounceMillis) {
    ensureOpen();
    transport.write(SensorCanLiteCodec.CONFIGURE,
                    SensorCanLiteCodec.configuration(invertMask, debounceMillis));
  }
  /** Manual action only, after the cause is removed. Do not call repeatedly from periodic(). */
  public void resumeTelemetry() {
    ensureOpen();
    transport.write(SensorCanLiteCodec.RESUME, SensorCanLiteCodec.resume());
  }
  private void ensureOpen() {
    if (closed) throw new IllegalStateException("SensorCanLite is closed");
  }
  @Override public void close() {
    if (!closed) { closed = true; transport.close(); }
  }
}
