"""Place readable reference labels with conservative rectangular exclusions.
Native DRC and rendered views are checked after this geometric aid.
"""
from pathlib import Path
import json,math,shutil
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
b=p.LoadBoard(str(HW/'grounded.kicad_pcb'))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def box(ob,ex=0):
 bb=ob.GetBoundingBox();return (p.ToMM(bb.GetX())-ex,p.ToMM(bb.GetY())-ex,p.ToMM(bb.GetRight())+ex,p.ToMM(bb.GetBottom())+ex)
def intersect(a,c):return a[0]<c[2] and a[2]>c[0] and a[1]<c[3] and a[3]>c[1]
def addtext(s,x,y,size=.85,layer=p.F_SilkS):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.13));t.SetLayer(layer);t.SetMirrored(layer==p.B_SilkS);b.Add(t)
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):t.SetFrontTentingMode(p.TENTING_MODE_TENTED);t.SetBackTentingMode(p.TENTING_MODE_TENTED)
for t in list(b.GetDrawings()):
 if isinstance(t,p.PCB_TEXT):
  if t.GetText().startswith('IN ') or t.GetText()=='P  G  S':t.SetLayer(p.Cmts_User)
  elif t.GetLayer()==p.B_SilkS:t.SetPosition(v(48,p.ToMM(t.GetPosition().y)+30))
for ch,x in enumerate([10.5,32,54,75.5],1):
 addtext(f'{ch}:P',x,94.8);addtext('G',x+5,94.8);addtext('S',x+10,94.8)
# Permanent useful user-facing jumper labels, placed in remaining clear areas.
# Reference names remain traceable to the assembly drawing and jumper table.
obstacles=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.IsOnLayer(p.F_Cu):obstacles.append(box(pad,.18))
 for item in f.GraphicalItems():
  if item.GetLayer() in [p.F_SilkS,p.F_Fab] and not isinstance(item,p.PCB_TEXT):obstacles.append(box(item,.14))
for item in b.GetDrawings():
 if item.GetLayer()==p.F_SilkS:obstacles.append(box(item,.15))
placements={};unplaced=[]
refs=sorted(b.GetFootprints(),key=lambda f:(0 if f.GetReference().startswith(('J','U','H')) else 1,f.GetReference()))
for f in refs:
 t=f.Reference();t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetKeepUpright(True);t.SetTextSize(v(.85,.85));t.SetTextThickness(p.FromMM(.13))
 original=tuple(p.ToMM(t.GetPosition()));fx,fy=p.ToMM(f.GetPosition())
 # Include candidates surrounding the original reference, with a preference
 # for short moves and horizontal text. Do not hide any reference designator.
 candidates=[(original[0]+dx/2,original[1]+dy/2) for dx in range(-12,13) for dy in range(-12,13)]
 for dist in [.5,1,1.5,2,2.5,3,3.5,4,4.5,5,6,7]:
  for dx,dy in [(0,-dist),(0,dist),(-dist,0),(dist,0),(-dist,-dist),(dist,-dist),(-dist,dist),(dist,dist)]:candidates.append((original[0]+dx,original[1]+dy))
 candidates.sort(key=lambda q:math.dist(original,q)+.05*abs(q[0]-original[0]))
 found=None
 for q in candidates:
  t.SetPosition(v(*q));bb=box(t,.1)
  if bb[0]<.5 or bb[1]<.5 or bb[2]>95.5 or bb[3]>95.5:continue
  if not any(intersect(bb,o) for o in obstacles):found=q;obstacles.append(bb);break
 if found is None:t.SetPosition(v(*original));obstacles.append(box(t,.1));unplaced.append(f.GetReference())
 placements[f.GetReference()]={'position_mm':list(p.ToMM(t.GetPosition())),'angle_degrees':0,'moved_mm':math.dist(original,p.ToMM(t.GetPosition()))}
b.BuildConnectivity();p.SaveBoard(str(HW/'FRC_Sensor_CAN.kicad_pcb'),b)
shutil.copyfile(HW/'grounded.kicad_pro',HW/'FRC_Sensor_CAN.kicad_pro')
(HW/'design/reference_placement.json').write_text(json.dumps(placements,indent=2)+'\n')
print('Unplaced labels:',unplaced)
