from pathlib import Path
import json,pcbnew as p
R=Path(__file__).resolve().parents[1];f=R/'hardware/FRC_Sensor_CAN.kicad_pcb';b=p.LoadBoard(str(f));j=b.FindFootprintByReference('J8');starts={}
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for pad in j.Pads():
 if not pad.GetNumber():continue
 x,y=p.ToMM(pad.GetPosition());ex=28.7 if x<31 else 33.8
 t=p.PCB_TRACK(b);t.SetStart(pad.GetPosition());t.SetEnd(v(ex,y));t.SetWidth(p.FromMM(.25));t.SetLayer(p.F_Cu);t.SetNet(pad.GetNet());b.Add(t)
 if pad.GetNetname()!='GND':
  via=p.PCB_VIA(b);via.SetPosition(v(ex,y));via.SetWidth(p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(pad.GetNet());b.Add(via);starts[pad.GetNetname()]=[1,ex,y]
z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayer(p.F_Cu);z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowZoneFills(True);poly=z.Outline();poly.NewOutline()
for x,y in [(29.2,2.2),(33.0,2.2),(33.0,9.3),(29.2,9.3)]:poly.Append(v(x,y))
b.Add(z);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);(R/'hardware/design/pogo_escape_starts.json').write_text(json.dumps(starts,indent=2)+'\n')
