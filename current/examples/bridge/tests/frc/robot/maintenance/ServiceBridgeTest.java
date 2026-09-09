package frc.robot.maintenance;
import java.net.Socket;
import java.util.Arrays;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
public final class ServiceBridgeTest {
  private ServiceBridgeTest() {}
  private static void check(boolean ok) { if (!ok) throw new AssertionError(); }
  public static void main(String[] args) throws Exception {
    AtomicBoolean allowed = new AtomicBoolean(false);
    AtomicInteger sends = new AtomicInteger();
    ConcurrentLinkedQueue<byte[]> replies = new ConcurrentLinkedQueue<>();
    ServiceBridge.Transport transport = new ServiceBridge.Transport() {
      @Override public void send(byte[] request) { sends.incrementAndGet(); replies.add(request); }
      @Override public byte[] receive() { return replies.poll(); }
      @Override public void close() {}
    };
    try (ServiceBridge bridge = new ServiceBridge(transport,allowed::get,0)) {
      try (Socket socket = new Socket("127.0.0.1",bridge.port())) {
        socket.setSoTimeout(1000);socket.getOutputStream().write(new byte[8]);check(socket.getInputStream().read()==-1);
      }
      check(sends.get()==0);allowed.set(true);
      try (Socket socket = new Socket("127.0.0.1",bridge.port())) {
        socket.setSoTimeout(1000);byte[] frame={1,9,1,0,83,67,77,49};
        socket.getOutputStream().write(frame,0,3);Thread.sleep(20);check(sends.get()==0);
        socket.getOutputStream().write(frame,3,5);check(Arrays.equals(frame,socket.getInputStream().readNBytes(8)));
        check(sends.get()==1);allowed.set(false);Thread.sleep(30);
        check(socket.getInputStream().read()==-1);check(sends.get()==1);
      }
    }
    System.out.println("bridge: real TCP fragmentation, opt-in rejection and permission revocation passed (mock CAN)");
  }
}
