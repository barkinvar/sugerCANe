package frc.robot.sensors;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

/** Host-only tests. The fake transport does not load native HAL or require a roboRIO. */
public final class SensorCanTest {
  private static long checks;
  private static void check(boolean value) {
    checks++;
    if (!value) throw new AssertionError("check " + checks);
  }
  private static void rejects(Runnable action) {
    boolean rejected = false;
    try { action.run(); } catch (IllegalArgumentException expected) { rejected = true; }
    check(rejected);
  }
  private static byte[] hex(String text) {
    return java.util.HexFormat.of().parseHex(text);
  }
  private static final class FakeTransport implements SensorCan.Transport {
    final Map<Integer, SensorCan.Packet> frames = new HashMap<>();
    long now;
    int writes, closes, lastApi;
    byte[] lastData;
    void put(int api, byte[] data) { frames.put(api, new SensorCan.Packet(data, now)); }
    @Override public SensorCan.Packet read(int api, int timeout) {
      var packet = frames.get(api);
      return packet == null || now - packet.timestampMillis() > timeout ? null : packet;
    }
    @Override public void write(int api, byte[] data) { writes++; lastApi = api; lastData = data; }
    @Override public void close() { closes++; }
  }
  public static void main(String[] args) {
    for (int id = 0; id < 64; id++) {
      for (int api = 0; api < 1024; api++) {
        int address = SensorCanCodec.canId(id, api);
        check((address & 63) == id && ((address >>> 6) & 1023) == api);
        check((address & 0x1fff0000) == 0x0a080000);
      }
    }
    rejects(() -> SensorCanCodec.canId(-1, 0));
    rejects(() -> SensorCanCodec.canId(64, 0));
    rejects(() -> SensorCanCodec.canId(0, 1024));
    var status = SensorCanCodec.status(hex("01fe0a0501020705"));
    check(status.sequence() == 254 && status.inputs() == 10 && status.rawInputs() == 5);
    check(status.enabledRails() == 1 && status.latchedFaults() == 2 && status.resetFlags() == 5);
    check(status.configured() && status.clockHealthy() && status.adcHealthy());
    check(!status.input(1) && status.input(2) && !status.input(3) && status.input(4));
    rejects(() -> status.input(0));
    rejects(() -> status.input(5));
    rejects(() -> SensorCanCodec.status(null));
    for (int length = 0; length < 16; length++) {
      if (length != 8) {
        byte[] bad = new byte[length];
        rejects(() -> SensorCanCodec.status(bad));
        rejects(() -> SensorCanCodec.counts(bad));
      }
    }
    for (int field : new int[] {0, 2, 3, 4, 5, 6, 7}) {
      for (int value = 0; value < 256; value++) {
        byte[] data = hex("0100000000000701");
        data[field] = (byte) value;
        boolean valid = field == 0 ? value == 1 : value < (field < 4 ? 16 : field < 6 ? 4 : field == 6 ? 8 : 16);
        if (valid) check(SensorCanCodec.status(data) != null);
        else rejects(() -> SensorCanCodec.status(data));
      }
    }
    var counts = SensorCanCodec.counts(hex("ffffffff00000080"));
    check(counts.first() == 4294967295L && counts.second() == 2147483648L);
    var diag = SensorCanCodec.diagnostic(hex("e02e8813ffff807f"));
    check(diag.sensorBatteryMillivolts() == 12000 && diag.sensor5Millivolts() == 5000);
    check(diag.transmitQueueDrops() == 65535 && diag.transmitErrors() == 128 && diag.receiveErrors() == 127);
    var identity = SensorCanCodec.identity(hex("010001000114020f"));
    check(identity.deviceId() == 20 && identity.debounceMillis() == 2 && identity.invertMask() == 15);
    check(Arrays.equals(SensorCanCodec.configuration(10, 100, 3), hex("5343010a64000300")));
    check(Arrays.equals(SensorCanCodec.clearFaults(3), hex("5343010300000000")));
    rejects(() -> SensorCanCodec.configuration(16, 2, 0));
    rejects(() -> SensorCanCodec.configuration(0, 0, 0));
    rejects(() -> SensorCanCodec.configuration(0, 101, 0));
    rejects(() -> SensorCanCodec.configuration(0, 2, 4));
    rejects(() -> SensorCanCodec.clearFaults(0));
    rejects(() -> SensorCanCodec.clearFaults(4));
    Random random = new Random(20260907);
    for (int n = 0; n < 100000; n++) {
      int a = random.nextInt(), b = random.nextInt();
      byte[] data = new byte[8];
      for (int i = 0; i < 4; i++) { data[i] = (byte) (a >>> (8 * i)); data[i + 4] = (byte) (b >>> (8 * i)); }
      var value = SensorCanCodec.counts(data);
      check(value.first() == Integer.toUnsignedLong(a) && value.second() == Integer.toUnsignedLong(b));
    }
    FakeTransport fake = new FakeTransport();
    SensorCan sensor = new SensorCan(20, fake);
    check(sensor.status().isEmpty());
    fake.put(SensorCanCodec.STATUS, hex("0100030302000701"));
    check(sensor.status().orElseThrow().value().input(1));
    fake.now = 100;
    check(sensor.status().isPresent());
    fake.now = 101;
    check(sensor.status().isEmpty());
    fake.put(SensorCanCodec.STATUS, hex("0200030302000701"));
    check(sensor.status().isEmpty());
    fake.put(SensorCanCodec.IDENTITY, hex("010001000115020f"));
    check(sensor.identity().isEmpty()); // The payload ID must match the selected CAN device.
    fake.put(SensorCanCodec.IDENTITY, hex("010001000114020f"));
    check(sensor.identity().isPresent());
    check(fake.writes == 0); // Read methods must never enable power or retry a latched rail.
    sensor.configureRuntime(10, 100, 3);
    check(fake.writes == 1 && fake.lastApi == 0x200 && Arrays.equals(fake.lastData, hex("5343010a64000300")));
    sensor.clearFaults(3);
    check(fake.writes == 2 && fake.lastApi == 0x201 && Arrays.equals(fake.lastData, hex("5343010300000000")));
    sensor.close(); sensor.close();
    check(fake.closes == 1);
    boolean closed = false;
    try { sensor.status(); } catch (IllegalStateException expected) { closed = true; }
    check(closed);
    System.out.println("PASS: " + checks + " Java protocol/driver assertions; WPILib transport compiled against 2026.2.1.");
  }
}
