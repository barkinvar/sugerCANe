"""Apply the reviewed low-current switched-battery sense route to the final PCB."""
from pathlib import Path
import json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(path))
r=json.loads((ROOT/'hardware/design/last_route_SENSOR_VBAT.json').read_text())
net=b.GetNetsByName()[r['net']]
def v(pt):return p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))
points=[[r['path'][0][0],*r['start_exact']]]+r['path']+[[r['path'][-1][0],*r['goal_exact']]]
for a,c in zip(points,points[1:]):
 if a==c:continue
 if a[0]!=c[0]:
  assert a[1:]==c[1:]
  t=p.PCB_VIA(b);t.SetPosition(v(a[1:]));t.SetWidth(p.FromMM(r['via_diameter']));t.SetDrill(p.FromMM(r['via_drill']));t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(v(a[1:]));t.SetEnd(v(c[1:]));t.SetWidth(p.FromMM(r['width']));t.SetLayer(p.F_Cu if a[0]==0 else p.B_Cu)
 t.SetNet(net);b.Add(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
print('Battery-output sense route applied and zones refilled')
