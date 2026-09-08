package frc.robot.sensors;

/** Wire format for the original FRC Sensor CAN v2 12 V protocol. All integers are little endian. */
public final class SensorCan12Codec {
  public static final int VERSION = 3;
  public static final int MANUFACTURER = 8;
  public static final int DEVICE_TYPE = 10;
  public static final int STATUS = 0x120;
  public static final int COUNTS_12 = 0x121;
  public static final int COUNTS_3 = 0x122;
  public static final int DIAGNOSTIC = 0x130;
  public static final int IDENTITY = 0x131;
  public static final int CONFIGURE = 0x220;
  public static final int RESUME = 0x221;

  private SensorCan12Codec() {}

  public record Status(int sequence, int inputs, int rawInputs, int channels,
                       int capabilities, int flags, int resetFlags) {
    /** Channel is 1 through 3. Inputs include configured inversion and debounce. */
    public boolean input(int channel) {
      range(channel, 1, 3, "channel");
      return (inputs & (1 << (channel - 1))) != 0;
    }
    public boolean rail12Good() { return (flags & 16) != 0; }
    public boolean rail5NoFault() { return (flags & 32) != 0; }
    public boolean powerHealthy() { return rail12Good() && rail5NoFault(); }
    public boolean usable() { return configured() && clockHealthy() && canHealthy() && powerHealthy(); }
    public boolean configured() { return (flags & 1) != 0; }
    public boolean clockHealthy() { return (flags & 2) != 0; }
    public boolean canHealthy() { return (flags & 4) != 0 && (flags & 8) == 0; }
  }
  public record Counts(long first, long second) {}
  public record Diagnostic(long transmitQueueDrops, int transmitErrors, int receiveErrors, int lastErrorCode, int flags) {}
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
    require((u8(data, 2) | u8(data, 3)) < 8, "invalid input mask");
    require(u8(data, 4) == 3 && u8(data, 5) == 63, "invalid channel/capability count");
    require(u8(data, 6) < 64 && u8(data, 7) < 16, "reserved status bits");
    return new Status(u8(data, 1), u8(data, 2), u8(data, 3), u8(data, 4),
                      u8(data, 5), u8(data, 6), u8(data, 7));
  }
  public static Counts counts(byte[] data) {
    frame(data);
    return new Counts(u32(data, 0), u32(data, 4));
  }
  public static Counts count3(byte[] data) {
    Counts c = counts(data);
    require(c.second() == 0, "reserved fourth counter");
    return c;
  }
  public static Diagnostic diagnostic(byte[] data) {
    frame(data);
    require(u8(data, 6) < 8 && u8(data, 7) < 4, "reserved diagnostic bits");
    return new Diagnostic(u32(data, 0), u8(data, 4), u8(data, 5), u8(data, 6), u8(data, 7));
  }
  public static Identity identity(byte[] data) {
    frame(data);
    require(u8(data, 0) == VERSION, "unsupported protocol version");
    require(u8(data, 4) == 4, "not Rev D hardware");
    range(u8(data, 5), 0, 63, "device ID");
    range(u8(data, 6), 1, 100, "debounce");
    range(u8(data, 7), 0, 7, "invert mask");
    return new Identity(u8(data, 1), u8(data, 2), u8(data, 3), u8(data, 4),
                        u8(data, 5), u8(data, 6), u8(data, 7));
  }
  /** Volatile configuration; hardware sensor power is independent. */
  public static byte[] configuration(int invertMask, int debounceMillis) {
    range(invertMask, 0, 7, "invert mask");
    range(debounceMillis, 1, 100, "debounce");
    return new byte[] {0x53, 0x43, VERSION, (byte) invertMask, (byte) debounceMillis, 0, 0, 0};
  }
  /** Explicit command only, after investigating a broadcast disable. */
  public static byte[] resume() { return new byte[] {0x53, 0x43, VERSION, 0, 0, 0, 0, 0}; }
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
