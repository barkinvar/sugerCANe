"""Lock short pogo escapes, keep pours away from contact pads, export autorouter input."""
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];H=R/'hardware';b=p.LoadBoard(str(H/'prerouted.kicad_pcb'))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
f=b.FindFootprintByReference('J8')
for pad in f.Pads():
 if not pad.GetNumber():continue
 x,y=p.ToMM(pad.GetPosition());end=8.8 if y>5.75 else 2.8
 t=p.PCB_TRACK(b);t.SetStart(pad.GetPosition());t.SetEnd(v(x,end));t.SetWidth(p.FromMM(.18));t.SetLayer(p.F_Cu);t.SetNet(pad.GetNet());t.SetLocked(True);b.Add(t)
 q=p.PCB_VIA(b);q.SetPosition(v(x,end));q.SetWidth(p.FromMM(.6));q.SetDrill(p.FromMM(.3));q.SetLayerPair(p.F_Cu,p.B_Cu);q.SetNet(pad.GetNet());q.SetLocked(True);b.Add(q)
z=p.ZONE(b);z.SetLayer(p.F_Cu);z.SetIsRuleArea(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False)
poly=z.Outline();poly.NewOutline()
for x,y in [(20.4,4),(27.6,4),(27.6,7.5),(20.4,7.5)]:poly.Append(v(x,y))
b.Add(z);b.BuildConnectivity();p.SaveBoard(str(H/'prerouted.kicad_pcb'),b);p.ExportSpecctraDSN(b,str(H/'design/prerouted.dsn'))
print('Pogo escapes locked and contact pour keepout added.')
