package frc.robot.sensors;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
public final class SensorCanLiteTest {
  private static int checks;
  private static void check(boolean v) { checks++; if (!v) throw new AssertionError("check "+checks); }
  private static byte[] hex(String s) { return java.util.HexFormat.of().parseHex(s); }
  private static void rejects(Runnable r) {
    try { r.run(); } catch (IllegalArgumentException expected) { checks++; return; }
    throw new AssertionError("accepted invalid input");
  }
  private static final class Fake implements SensorCanLite.Transport {
    final Map<Integer,SensorCanLite.Packet> frames=new HashMap<>();
    long now; int writes,api,closes; byte[] data;
    void put(int id,String s) { frames.put(id,new SensorCanLite.Packet(hex(s),now)); }
    public SensorCanLite.Packet read(int id,int timeout) {
      var p=frames.get(id);return p==null || now-p.timestampMillis()>timeout ? null:p;
    }
    public void write(int id,byte[] d) { writes++;api=id;data=d; }
    public void close() { closes++; }
  }
  public static void main(String[] args) {
    var s=SensorCanLiteCodec.status(hex("02fe0502031f0701"));
    check(s.input(1)&&!s.input(2)&&s.input(3)&&s.configured()&&s.canHealthy());
    rejects(()->s.input(4));rejects(()->s.input(0));
    check(!SensorCanLiteCodec.status(hex("02000000031f0f01")).canHealthy());
    for (int field:new int[]{0,2,3,4,5,6,7}) for(int v=0;v<256;v++) {
      byte[] d=hex("02000000031f0701");d[field]=(byte)v;
      boolean valid=field==0?v==2:field==4?v==3:field==5?v==31:field<4?v<8:v<16;
      if(valid)check(SensorCanLiteCodec.status(d)!=null);else rejects(()->SensorCanLiteCodec.status(d));
    }
    check(SensorCanLiteCodec.counts(hex("ffffffff00000080")).second()==2147483648L);
    rejects(()->SensorCanLiteCodec.count3(hex("0000000001000000")));
    check(SensorCanLiteCodec.count3(hex("ffffffff00000000")).first()==4294967295L);
    check(SensorCanLiteCodec.diagnostic(hex("ffffffff807f0703")).transmitQueueDrops()==4294967295L);
    rejects(()->SensorCanLiteCodec.diagnostic(hex("0000000000000800")));
    rejects(()->SensorCanLiteCodec.identity(hex("0200030002140207")));
    rejects(()->SensorCanLiteCodec.configuration(8,2));
    Fake f=new Fake();SensorCanLite b=new SensorCanLite(20,f);
    check(b.status().isEmpty());f.put(0x120,"02000502031f0701");check(b.status().isPresent());
    f.now=100;check(b.status().isPresent());f.now=101;check(b.status().isEmpty());
    f.put(0x120,"01000502031f0701");check(b.status().isEmpty());
    f.put(0x131,"0200030003150207");check(b.identity().isEmpty());
    f.put(0x131,"0200030003140207");check(b.identity().isPresent());
    f.put(0x122,"0000000001000000");check(b.count3().isEmpty());
    check(f.writes==0);
    b.configureRuntime(7,100);check(f.api==0x220&&Arrays.equals(f.data,hex("5343020764000000")));
    b.resumeTelemetry();check(f.writes==2&&f.api==0x221&&Arrays.equals(f.data,hex("5343020000000000")));
    b.close();b.close();check(f.closes==1);
    System.out.println("PASS: "+checks+" Lite Java assertions; WPILib 2026.2.1 compiled.");
  }
}
