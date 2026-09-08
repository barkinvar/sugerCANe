"""Add fabrication-ready ground fills, mounting clearances and stitching.
Run after finish_routes.py; retains all reviewed signal routes.
"""
from pathlib import Path
import math,json,shutil
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
b=p.LoadBoard(str(HW/'routed_pass2.kicad_pcb'));gnd=b.GetNetsByName()['GND']
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
# Copper keepout is larger than an M3 washer; conductive mounting hardware must
# still be insulated from robot structure as described in the installation guide.
for x,y in [(4,4),(92,4),(4,92),(92,92)]:
 z=p.ZONE(b);z.SetLayerSet(p.LSET.AllCuMask());z.SetIsRuleArea(True)
 z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
 poly=z.Outline();poly.NewOutline()
 for i in range(48):a=2*math.pi*i/48;poly.Append(v(x+3.52*math.cos(a),y+3.52*math.sin(a)))
 b.Add(z)
# Conservative point/geometry checks for additional ground stitching.  This is
# a placement aid only; native KiCad DRC is the authority after filling.
def distseg(q,a,c):
 d=(c[0]-a[0],c[1]-a[1]);den=d[0]**2+d[1]**2
 t=max(0,min(1,((q[0]-a[0])*d[0]+(q[1]-a[1])*d[1])/den)) if den else 0
 return math.hypot(q[0]-a[0]-t*d[0],q[1]-a[1]-t*d[1])
def clear(x,y):
 if any(math.hypot(x-a,y-c)<4 for a,c in [(4,4),(92,4),(4,92),(92,92)]):return False
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   bb=pad.GetBoundingBox();ex=.6
   if p.ToMM(bb.GetX())-ex<x<p.ToMM(bb.GetRight())+ex and p.ToMM(bb.GetY())-ex<y<p.ToMM(bb.GetBottom())+ex:return False
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   if math.dist((x,y),p.ToMM(t.GetPosition()))<.325+p.ToMM(t.GetWidth(p.F_Cu))/2+.22:return False
  elif t.GetNetname()!='GND' and distseg((x,y),p.ToMM(t.GetStart()),p.ToMM(t.GetEnd()))<.325+p.ToMM(t.GetWidth())/2+.22:return False
 return True
pts=[]
for x,y in [(17.0,89.7),(60.55,90),(55.2,71.04)]:
 t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(.65));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(gnd);b.Add(t);pts.append([x,y])
for x in range(6,91,12):
 for y in range(6,91,12):
  if clear(x,y):
   t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(.65));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(gnd);b.Add(t);pts.append([x,y])
for layer in [p.F_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(gnd);z.SetLocalClearance(p.FromMM(.25));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(p.FromMM(.25));z.SetIslandRemovalMode(0);z.SetMinIslandArea(p.FromMM(1)**2)
 poly=z.Outline();poly.NewOutline()
 for x,y in [(.5,.5),(95.5,.5),(95.5,95.5),(.5,95.5)]:poly.Append(v(x,y))
 b.Add(z)
# Solid thermal connection for the high-side switch exposed pad and its vias.
for f in b.GetFootprints():
 for pad in f.Pads():
  if (f.GetReference(),pad.GetNumber()) in [('U3','9'),('U6','2'),('JP202','2'),('U1','1'),('C2','2'),('C3','2'),('C4','2'),('C5','2'),('C13','2')]:pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
# Correct actual left-to-right connector polarity after the 180 degree rotation.
for t in b.GetDrawings():
 if isinstance(t,p.PCB_TEXT):
  if t.GetText()=='H  L':t.SetText('L  H')
  if t.GetText()=='REV A - PROTOTYPE':t.SetPosition(v(76,48));t.SetTextSize(v(.9,.9))
b.BuildConnectivity();filler=p.ZONE_FILLER(b);filler.Fill(b.Zones())
p.SaveBoard(str(HW/'grounded.kicad_pcb'),b)
shutil.copyfile(HW/'routed_pass2.kicad_pro',HW/'grounded.kicad_pro')
(HW/'design/ground_stitching.json').write_text(json.dumps(pts,indent=2)+'\n')
print('Added',len(pts),'ground stitching vias and two filled ground planes.')
