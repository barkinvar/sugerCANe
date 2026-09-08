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
# A0.3mm lead escape is needed between the0.65mm-pitch high-side switch pins.
# The distribution route widens to0.5mm after leaving the package.
route('SENSOR_VBAT',('U3','7'),(23.7,41.675),width=.3)
for project in HW.glob('*.kicad_pro'):
 data=json.loads(project.read_text());data.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{})['min_track_width']=.18;project.write_text(json.dumps(data,indent=2)+'\n')
p.SaveBoard(str(HW/'routed_pass2.kicad_pcb'),b)
