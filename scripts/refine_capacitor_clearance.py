"""Clear copper below C1's can except its necessary footprint lands.

Panasonic FK handling guidance discourages circuit patterns directly beneath
an aluminum capacitor. Route its input connection outside the body projection,
then clear top/bottom copper pours there. Existing C1 lands remain permitted.
"""
from pathlib import Path
import math
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(path))
def pos(xy):return p.VECTOR2I(p.FromMM(xy[0]),p.FromMM(xy[1]))
def near(a,c):return math.dist(a,c)<.002
def line(net,a,c,width,layer):
    t=p.PCB_TRACK(b);t.SetNet(b.GetNetsByName()[net]);t.SetStart(pos(a));t.SetEnd(pos(c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);b.Add(t)
# This transformation is intentionally specific to the reviewed source layout.
removed=[];moved=0
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA):
        if t.GetNetname()=='VIN_PROT' and near(p.ToMM(t.GetPosition()),(32.3,16.433499)):
            t.SetPosition(pos((31,17.8)));moved+=1
        continue
    a=p.ToMM(t.GetStart());c=p.ToMM(t.GetEnd())
    targets=[('VIN_PROT',(32.3,15),(32.3,16.433499)),
             ('VIN_PROT',(26.0012,16.6512),(32.082299,16.6512)),
             ('VIN_PROT',(32.082299,16.6512),(32.3,16.433499)),
             ('VIN_PROT',(32.3,16.433499),(32.3,35.0458)),
             ('GND',(29.8378,13.8122),(36.5122,13.8122)),
             ('GND',(36.5122,13.8122),(37.7,15)),
             ('GND',(37.7,15),(37.7,19.8))]
    if any(t.GetNetname()==n and ((near(a,x) and near(c,y)) or (near(a,y) and near(c,x))) for n,x,y in targets):
        removed.append((t.GetNetname(),a,c));b.Delete(t)
assert len(removed)==7 and moved==1,(len(removed),moved)
for a,c in [((26.0012,16.6512),(31,16.6512)),((31,15),(31,17.8))]:line('VIN_PROT',a,c,.5,p.F_Cu)
for a,c in [((31,17.8),(32.3,19.1)),((32.3,19.1),(32.3,35.0458))]:line('VIN_PROT',a,c,.5,p.B_Cu)
z=p.ZONE(b);z.SetLayerSet(p.LSET.AllCuMask());z.SetIsRuleArea(True)
z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
poly=z.Outline();poly.NewOutline()
for i in range(64):
    a=2*math.pi*i/64;poly.Append(pos((35+3.6*math.cos(a),15+3.6*math.sin(a))))
b.Add(z)
for fp in b.GetFootprints():
    if fp.GetReference()=='C1':
        for pad in fp.Pads():
            if pad.GetNumber()=='2':pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
print('C1 body copper keepout radius 3.6 mm; seven old segments replaced, one VIN via moved.')
