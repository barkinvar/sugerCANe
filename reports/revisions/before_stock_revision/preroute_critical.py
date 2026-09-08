#!/usr/bin/env python3
"""Short fixed routes for switching regulator and crystal before signal autorouting."""
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]; HW=ROOT/'hardware'
b=p.LoadBoard(str(HW/'placed.kicad_pcb'))
f={x.GetReference():x for x in b.GetFootprints()}
pads={(r,z.GetNumber()):z for r,x in f.items() for z in x.Pads() if z.GetNumber()}
nets=b.GetNetsByName()
via_positions=set()
def xy(a):
 if isinstance(a,tuple) and isinstance(a[0],str):return tuple(p.ToMM(pads[a].GetPosition()))
 return a
def v(a):return p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1]))
def route(net,*points,width=.3,layer=p.F_Cu):
 for a,c in zip(points,points[1:]):
  a,c=xy(a),xy(c)
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(c));t.SetLayer(layer);t.SetWidth(p.FromMM(width));t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
def via(net,x,y,size=.7,drill=.3):
 key=(net,x,y)
 if key in via_positions:return
 via_positions.add(key)
 z=p.PCB_VIA(b);z.SetPosition(v((x,y)));z.SetWidth(p.FromMM(size));z.SetDrill(p.FromMM(drill));z.SetLayerPair(p.F_Cu,p.B_Cu);z.SetNet(nets[net]);z.SetLocked(True);b.Add(z)
def gnd(ref,pin,x,y):
 route('GND',(ref,str(pin)),(x,y));via('GND',x,y)
# Input protection path and regulator high-current connections.
route('VIN_RAW',('J1','1'),(17,11.5),(14,11.5),('F1','1'),width=.9)
route('VIN_FUSED',('F1','2'),(13,19.455),(14.2,18.255),('D1','2'),width=.9)
route('VIN_PROT',('D1','1'),(21.2,17.2),(21.2,19.175),('C2','1'),width=.8)
route('VIN_PROT',('C2','1'),(21.2,20.825),(21.2,22.05),('C3','1'),width=.5)
route('VIN_PROT',('C3','1'),(19.8,24.3875),('U1','3'),width=.45)
route('VIN_PROT',('U1','5'),(15.5,26),(15.5,27.3));via('VIN_PROT',15.5,27.3)
route('VIN_PROT',(15.5,27.3),(15.5,21),(17.5,19),(21,19),(22,20),width=.3,layer=p.B_Cu)
via('VIN_PROT',22.0,20);route('VIN_PROT',('C2','1'),(22.0,20),width=.5)
# The long bottom connection ends at this via; SMD pad itself is top-only.
route('VIN_PROT',('C2','1'),(22.0,20),layer=p.B_Cu)
route('BUCK_SW',('U1','2'),('L1','1'),width=.8)
route('BUCK_SW',(21,26),(21,28.8),(19.8,30),('C6','2'),width=.35)
route('BUCK_CB',('U1','6'),(16.8625,29.8125),('C6','1'),width=.3)
route('V5_INTERNAL',('L1','2'),(31.525,26),('C4','1'),width=.8)
route('V5_INTERNAL',('C4','1'),('C5','1'),width=.8)
route('V5_INTERNAL',('C5','1'),(32.525,32),(37,32),(37,26.95),('U2','3'),width=.55)
route('V5_INTERNAL',(37,26.95),(37,25.05),('U2','1'),width=.45)
route('V5_INTERNAL',(37,25.05),(37,22.55),('C7','1'),width=.45)
route('BUCK_FB',('R1','2'),(15.5,23),(16.8625,24.3625),('U1','4'),width=.25)
route('BUCK_FB',('R2','1'),(15.0,26),(15.0,25.05),('U1','4'),width=.25)
route('+3V3',('U2','5'),(43.1,25.05),('C8','1'),width=.4)
for args in [('U1',1,19.1375,28.2),('C3',2,18.7,21.55),('C2',2,26.2,20),('C4',2,35.6,23.6),('C5',2,35.8,31),('U2',2,37.85,26),('C7',2,40.8,21.5),('C8',2,45.2,24),('R2',2,11,26)]:gnd(*args)
# Clock: short top-layer routes, no vias in oscillator signals.
route('HSE_IN',('U5','2'),('Y1','1'),width=.25)
route('HSE_IN',(52,24),('C25','1'),width=.25)
route('HSE_OUT',('U5','3'),(54.5,24.8),(54.5,26),('R20','1'),width=.25)
route('HSE_XTAL_OUT',('R20','2'),(51.6,26.4875),(51.6,27.5),(46.35,27.5),('Y1','3'),width=.25)
route('HSE_XTAL_OUT',(46.35,27.5),('C26','1'),width=.25)
for args in [('Y1',2,45.2,24),('Y1',4,50.6,25.2),('C25',2,51,20.75),('C26',2,46,31.5),('U5',16,62.8,31.4),('U5',32,57.2,20.5),('C20',2,59.9,19)]:gnd(*args)
# Local MCU supply at pin1, with ground returned through its nearby via.
route('+3V3',('C20','1'),(55.3,20.75),(55.3,23.2),('U5','1'),width=.3)
# Adjacent supply/output pins of the protected battery switch are strapped, not left for a thin route.
for net,pins in [('SENSOR_VBAT',['5','6','7']),('VIN_PROT',['8','9','10'])]:
 for a,c in zip(pins,pins[1:]):route(net,('U3',a),('U3',c),width=.45)

p.SaveBoard(str(HW/'prerouted.kicad_pcb'),b)
print('Added',len(b.GetTracks()),'fixed track/via items.')
