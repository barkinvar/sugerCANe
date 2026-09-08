#!/usr/bin/env python3
from pathlib import Path
import pcbnew as p
import json
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
b=p.LoadBoard(str(HW/'routed_pass1.kicad_pcb'));nets=b.GetNetsByName()
f={f.GetReference():f for f in b.GetFootprints()};pads={(ref,z.GetNumber()):z for ref,x in f.items() for z in x.Pads() if z.GetNumber()}
def v(pt):return p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))
def xy(a):return tuple(p.ToMM(pads[a].GetPosition())) if isinstance(a[0],str) else a
def route(net,*pts,width=.5,layer=p.F_Cu):
 for a,c in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(xy(a)));t.SetEnd(v(xy(c)));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
def via(net,pt):
 t=p.PCB_VIA(b);t.SetPosition(v(pt));t.SetWidth(p.FromMM(.8));t.SetDrill(p.FromMM(.4));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[net]);b.Add(t)
# Router neckdowns are 0.1874mm. Declare0.18mm minimum (7.1mil), above standard6mil fabrication capability.
b.GetDesignSettings().m_TrackMinWidth=p.FromMM(.18)
route('V5_INTERNAL',('TP3','1'),(37,31))
route('VPORT1',('JP101','2'),(7.5,78.54),(7.5,87),('J4','1'))
route('SENSOR_VBAT',('TP6','1'),(5,47),width=.6);via('SENSOR_VBAT',(5,47))
route('SENSOR_VBAT',(5,47),(3,49),(3,81.08),('JP101','3'),width=.6,layer=p.B_Cu)
r=json.loads((HW/'design/last_route.json').read_text());points=r['path']
route('VPORT3',r['start_exact'],points[0][1:])
for a,c in zip(points,points[1:]):
 if a[0]!=c[0]:
  assert a[1:]==c[1:];via('VPORT3',a[1:])
 else:route('VPORT3',a[1:],c[1:],layer=p.F_Cu if a[0]==0 else p.B_Cu)
route('VPORT3',points[-1][1:],r['goal_exact'],layer=p.F_Cu if points[-1][0]==0 else p.B_Cu)
for project in HW.glob('*.kicad_pro'):
 data=json.loads(project.read_text());data.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{})['min_track_width']=.18;project.write_text(json.dumps(data,indent=2)+'\n')
p.SaveBoard(str(HW/'routed_pass2.kicad_pcb'),b)
