package frc.robot.sensors;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
public final class SensorCan12Test {
  private static int checks;
  private static void check(boolean v) { checks++; if (!v) throw new AssertionError("check "+checks); }
  private static byte[] hex(String s) { return java.util.HexFormat.of().parseHex(s); }
  private static void rejects(Runnable r) {
    try { r.run(); } catch (IllegalArgumentException expected) { checks++; return; }
    throw new AssertionError("accepted invalid input");
  }
  private static final class Fake implements SensorCan12.Transport {
    final Map<Integer,SensorCan12.Packet> frames=new HashMap<>();
    long now; int writes,api,closes; byte[] data;
    void put(int id,String s) { frames.put(id,new SensorCan12.Packet(hex(s),now)); }
    public SensorCan12.Packet read(int id,int timeout) {
      var p=frames.get(id);return p==null || now-p.timestampMillis()>timeout ? null:p;
    }
    public void write(int id,byte[] d) { writes++;api=id;data=d; }
    public void close() { closes++; }
  }
  public static void main(String[] args) {
    var s=SensorCan12Codec.status(hex("04fe0502037f7701"));
    check(s.input(1)&&!s.input(2)&&s.input(3)&&s.configured()&&s.canHealthy());
    rejects(()->s.input(4));rejects(()->s.input(0));
    check(!SensorCan12Codec.status(hex("04000000037f7f01")).canHealthy());
    for (int field:new int[]{0,2,3,4,5,6,7}) for(int v=0;v<256;v++) {
      byte[] d=hex("04000000037f7701");d[field]=(byte)v;
      boolean valid=field==0?v==4:field==4?v==3:field==5?v==127:field<4?v<8:field==6?v<128:v<16;
      if(valid)check(SensorCan12Codec.status(d)!=null);else rejects(()->SensorCan12Codec.status(d));
    }
    check(SensorCan12Codec.counts(hex("ffffffff00000080")).second()==2147483648L);
    rejects(()->SensorCan12Codec.count3(hex("0000000001000000")));
    check(SensorCan12Codec.count3(hex("ffffffff00000000")).first()==4294967295L);
    check(SensorCan12Codec.diagnostic(hex("ffffffff807f0703")).transmitQueueDrops()==4294967295L);
    rejects(()->SensorCan12Codec.diagnostic(hex("0000000000000800")));
    rejects(()->SensorCan12Codec.identity(hex("0300040003140207")));
    rejects(()->SensorCan12Codec.configuration(8,2));
    Fake f=new Fake();SensorCan12 b=new SensorCan12(20,f);
    check(b.status().isEmpty());f.put(0x120,"04000502037f7701");check(b.status().isPresent());
    f.now=100;check(b.status().isPresent());f.now=101;check(b.status().isEmpty());
    f.put(0x120,"01000502033f3701");check(b.status().isEmpty());
    f.put(0x131,"0400070006150207");check(b.identity().isEmpty());
    f.put(0x131,"0400070006140207");check(b.identity().isPresent());
    f.put(0x122,"0000000001000000");check(b.count3().isEmpty());
    check(f.writes==0);
    f.put(0x120,"04000502037f7701");check(b.input(1).orElse(false));
    for (int flag : new int[]{0,1,2,4,8,16,32,64}) {
      byte[] d=hex("04000502037f7701");d[6]=(byte)(119^flag);
      f.frames.put(0x120,new SensorCan12.Packet(d,f.now));
      if(flag==0)check(b.input(1).isPresent());else check(b.input(1).isEmpty());
    }
    f.now+=101;check(b.input(1).isEmpty());
    var modes=new SensorCan12Codec.InputMode[]{SensorCan12Codec.InputMode.PULL_HIGH,SensorCan12Codec.InputMode.PULL_LOW,SensorCan12Codec.InputMode.FLOAT_DETECT};
    var active=new SensorCan12Codec.ActiveWhen[]{SensorCan12Codec.ActiveWhen.LOW,SensorCan12Codec.ActiveWhen.HIGH,SensorCan12Codec.ActiveWhen.DRIVEN};
    b.configureInputsRuntime(modes,active);check(f.api==0x222&&Arrays.equals(f.data,hex("53430400d1020100")));
    f.put(0x132,"04070401d1020100");check(b.inputState().orElseThrow().value().level(3)==SensorCan12Codec.InputLevel.FLOATING);
    f.put(0x132,"04070404d1020100");check(b.inputState().isEmpty());
    b.configureRuntime(7,100);check(f.api==0x220&&Arrays.equals(f.data,hex("5343040764000000")));
    b.resumeTelemetry();check(f.writes==3&&f.api==0x221&&Arrays.equals(f.data,hex("5343040000000000")));
    b.close();b.close();check(f.closes==1);
    System.out.println("PASS: "+checks+" 12 V Java assertions; WPILib 2026.2.1 compiled.");
  }
}
