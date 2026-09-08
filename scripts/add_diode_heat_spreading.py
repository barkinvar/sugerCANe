#!/usr/bin/env python3
"""Local positive-net copper around D1; bounded away from the buck switch/feedback area."""
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];PATH=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(PATH));nets=b.GetNetsByName()
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for net,x1,y1,x2,y2,points in [
 ('VIN_FUSED',10.6,12.7,17.3,20.8,[(15,13.2),(14.2,19.7)]),
 ('VIN_PROT',18.7,12.5,24.3,21.1,[(23,13),(23,17.5)])]:
 for layer in (p.F_Cu,p.B_Cu):
  z=p.ZONE(b);z.SetNet(nets[net]);z.SetLayer(layer);z.SetAssignedPriority(5)
  z.SetZoneName('D1 heat spread '+net+' '+b.GetLayerName(layer))
  z.SetLocalClearance(p.FromMM(.25));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
  z.SetMinThickness(p.FromMM(.2));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
  outline=z.Outline();outline.NewOutline()
  for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:outline.Append(p.FromMM(x),p.FromMM(y))
  b.Add(z)
 for x,y in points:
  via=p.PCB_VIA(b);via.SetPosition(v(x,y));via.SetWidth(p.FromMM(.7));via.SetDrill(p.FromMM(.3))
  via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(nets[net]);via.SetLocked(True)
  via.SetFrontTentingMode(p.TENTING_MODE_TENTED);via.SetBackTentingMode(p.TENTING_MODE_TENTED);b.Add(via)
for f in b.GetFootprints():
 if f.GetReference()=='C3':
  f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.Reference().SetPosition(v(22.0,23.4))
filler=p.ZONE_FILLER(b);filler.Fill(b.Zones());p.SaveBoard(str(PATH),b)
print('Added four bounded copper heat-spreading zones and four tented vias for D1.')
