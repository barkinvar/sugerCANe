package frc.robot.maintenance;
import edu.wpi.first.hal.CANData;
import edu.wpi.first.wpilibj.CAN;
import edu.wpi.first.wpilibj.DriverStation;
import java.io.IOException;
import java.util.Arrays;
import java.util.function.BooleanSupplier;
/** Explicit opt-in AND disabled state are checked on every transmission. */
public final class Wpilib2026 {
  private Wpilib2026() {}
  public static ServiceBridge start(BooleanSupplier maintenanceRequested) throws IOException {
    CAN can = new CAN(0,8,10);
    ServiceBridge.Transport transport = new ServiceBridge.Transport() {
      @Override public void send(byte[] request) { can.writePacket(request,0x300); }
      @Override public byte[] receive() {
        CANData data = new CANData();
        return can.readPacketNew(0x301,data) && data.length==8 ? Arrays.copyOf(data.data,8) : null;
      }
      @Override public void close() { can.close(); }
    };
    try { return new ServiceBridge(transport, () -> maintenanceRequested.getAsBoolean() && DriverStation.isDisabled(), 5810); }
    catch (IOException | RuntimeException error) { transport.close(); throw error; }
  }
}
