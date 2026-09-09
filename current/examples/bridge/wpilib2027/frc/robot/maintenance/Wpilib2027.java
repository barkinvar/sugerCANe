package frc.robot.maintenance;
import org.wpilib.hardware.hal.can.CANReceiveMessage;
import org.wpilib.hardware.bus.CAN;
import org.wpilib.hardware.bus.CANPort;
import org.wpilib.driverstation.RobotState;
import java.io.IOException;
import java.util.Arrays;
import java.util.function.BooleanSupplier;
/** WPILib 2027 alpha-7; select the actual classical-CAN bus explicitly. */
public final class Wpilib2027 {
  private Wpilib2027() {}
  public static ServiceBridge start(CANPort port, BooleanSupplier maintenanceRequested) throws IOException {
    CAN can = new CAN(port,0,8,10);
    ServiceBridge.Transport transport = new ServiceBridge.Transport() {
      @Override public void send(byte[] request) { can.writePacket(0x300,request,8,0); }
      @Override public byte[] receive() {
        CANReceiveMessage data = new CANReceiveMessage();
        return can.readPacketNew(0x301,data) && data.length==8 && data.flags==0 ? Arrays.copyOf(data.data,8) : null;
      }
      @Override public void close() { can.close(); }
    };
    try { return new ServiceBridge(transport, () -> maintenanceRequested.getAsBoolean() && RobotState.isDisabled(), 5810); }
    catch (IOException | RuntimeException error) { transport.close(); throw error; }
  }
}
