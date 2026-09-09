package frc.robot.maintenance;

import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.Arrays;
import java.util.Objects;
import java.util.function.BooleanSupplier;

/** Fixed SC12 maintenance frames only. Bind localhost and access through SSH. */
public final class ServiceBridge implements AutoCloseable {
  public interface Transport extends AutoCloseable {
    void send(byte[] request);
    byte[] receive();
    @Override void close();
  }
  private final Transport transport;
  private final BooleanSupplier allowed;
  private final ServerSocket server;
  private final Thread worker;
  private volatile boolean closed;
  private volatile boolean connected;
  private volatile Socket active;
  private volatile String lastError = "";

  public ServiceBridge(Transport transport, BooleanSupplier allowed, int port) throws IOException {
    this.transport = Objects.requireNonNull(transport);
    this.allowed = Objects.requireNonNull(allowed);
    server = new ServerSocket(port, 1, InetAddress.getByName("127.0.0.1"));
    server.setSoTimeout(100);
    worker = new Thread(this::serve, "SC12-maintenance");
    worker.setDaemon(true);
    worker.start();
  }
  public boolean isConnected() { return connected; }
  public String lastError() { return lastError; }
  public int port() { return server.getLocalPort(); }
  private void serve() {
    try {
      while (!closed) {
        try (Socket socket = server.accept()) {
          active = socket;
          if (!allowed.getAsBoolean()) continue;
          connected = true;
          socket.setTcpNoDelay(true);
          socket.setSoTimeout(5);
          session(socket);
        } catch (SocketTimeoutException timeout) {
          // Poll the close flag while no client is attached.
        } catch (IOException | RuntimeException error) {
          if (!closed) lastError = error.toString();
        } finally {
          active = null;
          connected = false;
        }
      }
    } finally { transport.close(); }
  }
  private void session(Socket socket) throws IOException {
    byte[] request = new byte[8];
    int used = 0;
    int token = 0;
    long lastRequest = System.nanoTime(), lastSend = 0;
    try {
      while (!closed && allowed.getAsBoolean() && System.nanoTime()-lastRequest < 5_000_000_000L) {
        try {
          int n = socket.getInputStream().read(request, used, 8-used);
          if (n < 0) return;
          used += n;
        } catch (SocketTimeoutException timeout) { /* Drain CAN below. */ }
        if (used == 8) {
          long remaining = 5_000_000L-(System.nanoTime()-lastSend);
          if (remaining > 0) {
            try { Thread.sleep(remaining/1_000_000L, (int)(remaining%1_000_000L)); }
            catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); return; }
          }
          if (closed || !allowed.getAsBoolean()) return;
          // Only opcodes used by this protocol; arbitrary CAN IDs are never exposed.
          int op = request[0]&255;
          if (!((op>=1 && op<=6) || (op>=0x10 && op<=0x15) || (op>=0x20 && op<=0x25)))
            throw new IOException("Unsupported SC12 service opcode");
          token = (request[2]&255)|((request[3]&255)<<8);
          transport.send(Arrays.copyOf(request,8));
          lastSend = lastRequest = System.nanoTime();
          used = 0;
        }
        byte[] reply = transport.receive();
        if (reply != null && reply.length == 8) socket.getOutputStream().write(reply);
      }
    } finally {
      // End quiet mode promptly after EOF/timeout. Never transmit after permission is revoked.
      if (!closed && allowed.getAsBoolean() && token != 0)
        transport.send(new byte[]{6,0,(byte)token,(byte)(token>>8),0,0,0,0});
    }
  }
  @Override public void close() throws IOException {
    closed = true;
    server.close();
    Socket socket = active;
    if (socket != null) socket.close();
    worker.interrupt();
    try { worker.join(1000); }
    catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); }
  }
}
