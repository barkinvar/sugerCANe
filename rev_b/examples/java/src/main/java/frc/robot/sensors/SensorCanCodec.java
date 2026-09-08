package frc.robot.sensors;

/** Wire format for the original FRC Sensor CAN v1 protocol. All integers are little endian. */
public final class SensorCanCodec {
  public static final int VERSION = 1;
  public static final int MANUFACTURER = 8;
  public static final int DEVICE_TYPE = 10;
  public static final int STATUS = 0x100;
  public static final int COUNTS_12 = 0x101;
  public static final int COUNTS_34 = 0x102;
  public static final int DIAGNOSTIC = 0x110;
  public static final int IDENTITY = 0x111;
  public static final int CONFIGURE = 0x200;
  public static final int CLEAR_FAULTS = 0x201;

  private SensorCanCodec() {}

  public record Status(int sequence, int inputs, int rawInputs, int enabledRails,
                       int latchedFaults, int flags, int resetFlags) {
    /** Channel is 1 through 4. Inputs include configured inversion and debounce. */
    public boolean input(int channel) {
      range(channel, 1, 4, "channel");
      return (inputs & (1 << (channel - 1))) != 0;
    }
    public boolean configured() { return (flags & 1) != 0; }
    public boolean clockHealthy() { return (flags & 2) != 0; }
    public boolean adcHealthy() { return (flags & 4) != 0; }
  }
  public record Counts(long first, long second) {}
  public record Diagnostic(int sensorBatteryMillivolts, int sensor5Millivolts,
                           int transmitQueueDrops, int transmitErrors, int receiveErrors) {}
  public record Identity(int major, int minor, int patch, int hardwareRevision,
                         int deviceId, int debounceMillis, int invertMask) {}

  public static int canId(int deviceId, int api) {
    range(deviceId, 0, 63, "device ID");
    range(api, 0, 1023, "API ID");
    return (DEVICE_TYPE << 24) | (MANUFACTURER << 16) | (api << 6) | deviceId;
  }
  public static Status status(byte[] data) {
    frame(data);
    require(u8(data, 0) == VERSION, "unsupported protocol version");
    require((u8(data, 2) | u8(data, 3)) < 16, "invalid input mask");
    require((u8(data, 4) | u8(data, 5)) < 4, "invalid rail mask");
    require(u8(data, 6) < 8 && u8(data, 7) < 16, "reserved status bits");
    return new Status(u8(data, 1), u8(data, 2), u8(data, 3), u8(data, 4),
                      u8(data, 5), u8(data, 6), u8(data, 7));
  }
  public static Counts counts(byte[] data) {
    frame(data);
    return new Counts(u32(data, 0), u32(data, 4));
  }
  public static Diagnostic diagnostic(byte[] data) {
    frame(data);
    return new Diagnostic(u16(data, 0), u16(data, 2), u16(data, 4), u8(data, 6), u8(data, 7));
  }
  public static Identity identity(byte[] data) {
    frame(data);
    require(u8(data, 0) == VERSION, "unsupported protocol version");
    range(u8(data, 5), 0, 63, "device ID");
    range(u8(data, 6), 1, 100, "debounce");
    range(u8(data, 7), 0, 15, "invert mask");
    return new Identity(u8(data, 1), u8(data, 2), u8(data, 3), u8(data, 4),
                        u8(data, 5), u8(data, 6), u8(data, 7));
  }
  /** Volatile configuration. Power bits: 1 = shared 5 V, 2 = shared battery output. */
  public static byte[] configuration(int invertMask, int debounceMillis, int railMask) {
    range(invertMask, 0, 15, "invert mask");
    range(debounceMillis, 1, 100, "debounce");
    range(railMask, 0, 3, "rail mask");
    return new byte[] {0x53, 0x43, VERSION, (byte) invertMask,
      (byte) debounceMillis, (byte) (debounceMillis >>> 8), (byte) railMask, 0};
  }
  /** One explicit attempt; selected rails must have been off for at least 100 ms. */
  public static byte[] clearFaults(int mask) {
    range(mask, 1, 3, "fault mask");
    return new byte[] {0x53, 0x43, VERSION, (byte) mask, 0, 0, 0, 0};
  }
  private static void frame(byte[] data) {
    require(data != null && data.length == 8, "expected exactly eight bytes");
  }
  private static int u8(byte[] d, int n) { return Byte.toUnsignedInt(d[n]); }
  private static int u16(byte[] d, int n) { return u8(d, n) | (u8(d, n + 1) << 8); }
  private static long u32(byte[] d, int n) {
    return Integer.toUnsignedLong(u16(d, n) | (u16(d, n + 2) << 16));
  }
  static void range(int value, int lo, int hi, String name) {
    require(value >= lo && value <= hi, name + " outside " + lo + ".." + hi);
  }
  private static void require(boolean condition, String message) {
    if (!condition) throw new IllegalArgumentException(message);
  }
}
