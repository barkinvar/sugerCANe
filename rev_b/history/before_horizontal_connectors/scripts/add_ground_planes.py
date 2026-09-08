"""Fill both layers after routing; retain existing mounting and pogo keepouts."""
from pathlib import Path
import math,json,shutil
import pcbnew as p
R=Path(__file__).resolve().parents[1]; HW=R/'hardware'
b=p.LoadBoard(str(HW/'routed_pass1.kicad_pcb'));gnd=b.GetNetsByName()['GND']
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def distseg(q,a,c):
 d=(c[0]-a[0],c[1]-a[1]);den=sum(x*x for x in d)
 t=max(0,min(1,((q[0]-a[0])*d[0]+(q[1]-a[1])*d[1])/den)) if den else 0
 return math.hypot(q[0]-a[0]-t*d[0],q[1]-a[1]-t*d[1])
def clear(x,y):
 if any(math.hypot(x-a,y-c)<3.9 for a,c in [(3.5,3.5),(56.5,3.5),(3.5,64.5),(56.5,64.5)]):return False
 if 28.3<x<34 and y<12:return False # programming cable access
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   bb=pad.GetBoundingBox();ex=.6
   if p.ToMM(bb.GetX())-ex<x<p.ToMM(bb.GetRight())+ex and p.ToMM(bb.GetY())-ex<y<p.ToMM(bb.GetBottom())+ex:return False
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   if math.dist((x,y),p.ToMM(t.GetPosition()))<.325+p.ToMM(t.GetWidth(p.F_Cu))/2+.23:return False
  elif t.GetNetname()!='GND' and distseg((x,y),p.ToMM(t.GetStart()),p.ToMM(t.GetEnd()))<.325+p.ToMM(t.GetWidth())/2+.23:return False
 return True
pts=[]
for x in range(5,59,7):
 for y in range(5,67,7):
  if not clear(x,y):continue
  t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(.65));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(gnd);b.Add(t);pts.append([x,y])
for layer in [p.F_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(gnd);z.SetLocalClearance(p.FromMM(.25));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(p.FromMM(.2));z.SetIslandRemovalMode(0);z.SetMinIslandArea(p.FromMM(1)**2)
 poly=z.Outline();poly.NewOutline()
 for x,y in [(.5,.5),(59.5,.5),(59.5,67.5),(.5,67.5)]:poly.Append(v(x,y))
 b.Add(z)
for fp in b.GetFootprints():
 for pad in fp.Pads():
  if pad.GetNetname()=='GND' and (fp.GetReference().startswith('C') or fp.GetReference() in ['U1','U3','U8']):pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(HW/'grounded.kicad_pcb'),b);shutil.copyfile(HW/'placed.kicad_pro',HW/'grounded.kicad_pro')
(HW/'design/ground_stitching.json').write_text(json.dumps(pts,indent=2)+'\n')
print('Added',len(pts),'ground stitching vias; filled two ground layers.')
