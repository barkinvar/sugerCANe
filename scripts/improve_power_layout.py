#!/usr/bin/env python3
"""Local reviewed edits to the routed board; retain all unrelated routing and 3D metadata."""
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(PATH));fs={f.GetReference():f for f in b.GetFootprints()};nets=b.GetNetsByName()
def v(a):return p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1]))
def route(net,points,width):
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(p.FromMM(width));t.SetLayer(p.F_Cu);t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
remove={
 ('VIN_PROT',(22.025,20.0),(21.2,20.825)),
 ('VIN_PROT',(21.2,20.825),(21.2,22.05)),
 ('VIN_PROT',(21.2,22.05),(19.8,23.45)),
 ('VIN_PROT',(19.8,23.45),(19.8,24.3875)),
 ('VIN_PROT',(19.8,24.3875),(19.1375,25.05)),
 ('GND',(19.8,21.55),(18.7,21.55)),
}
selected=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):continue
 key=(t.GetNetname(),tuple(p.ToMM(t.GetStart())),tuple(p.ToMM(t.GetEnd())))
 if key in remove or t.GetNetname()=='BUCK_SW':selected.append(t)
assert len(selected)==10,('Run exactly once on before_power_layout board',len(selected))
for t in selected:b.Remove(t)
fs['C3'].SetOrientationDegrees(270);fs['C3'].SetPosition(v((21.3,26)))
route('VIN_PROT',[(22.025,20),(21.3,20.725),(21.3,25.05),(19.1375,25.05)],.45)
route('GND',[(21.3,26.95),(19.1375,26.95)],.4)
route('BUCK_SW',[(19.1375,26),(22.5,26)],.4)
route('BUCK_SW',[(22.5,26),(24.275,26)],.8)
route('BUCK_SW',[(22.5,26),(22.5,28.5),(21,30),(18.95,30)],.35)
for ref,pin in [('U1','1'),('C2','2'),('C3','2'),('C4','2'),('C5','2'),('C13','2')]:
 for pad in fs[ref].Pads():
  if pad.GetNumber()==pin:pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
filler=p.ZONE_FILLER(b);filler.Fill(b.Zones())
p.SaveBoard(str(PATH),b)
print('Moved C3 adjacent to VIN/GND; shortened high-frequency input loop; direct ground pours on buck bypass pads.')
