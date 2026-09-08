"""Find exposed geometric opportunities to join unequal-potential ground pours.
Uses the prior exported DC sheet field; native DRC remains required.
"""
from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Point,LineString,box
from shapely import union_all,contains_xy
R=Path(__file__).resolve().parents[1];g=json.loads((R/'hardware/design/routing_geometry.json').read_text());z=np.load(R/'reports/electrical/ground_fields.npz');pitch=float(z['pitch'])
a,c=z['top'],z['bottom'];yy,xx=np.indices(a.shape);x=(xx+.5)*pitch;y=(yy+.5)*pitch
blocked=[]
for o in g['obstacles']:
 if not o['layers']:continue
 if o['type']=='rect':p=box(*o['bounds'])
 elif o['type']=='circle':p=Point(*o['xy']).buffer(o['radius'])
 else:p=LineString([o['a'],o['b']]).buffer(o['width']/2)
 if o['net']!='GND':blocked.append(p.buffer(.502))
 elif o['type']=='rect':blocked.append(p.buffer(.35)) # no drilling into lands
 elif o['type']=='circle':blocked.append(p.buffer(.45)) # no near-duplicate barrels
for h in g['holes']:blocked.append(Point(*h['xy']).buffer(h['radius']+.401))
for q in [(3.5,3.5),(56.5,3.5),(3.5,64.5),(56.5,64.5)]:blocked.append(Point(*q).buffer(3.62))
blocked.append(box(28,0,35,12))
mask=np.isfinite(a)&np.isfinite(c)&(x>.65)&(x<59.35)&(y>.65)&(y<67.35)
mask&=~contains_xy(union_all(blocked),x,y)
score=np.where(mask,np.abs(a-c),0);points=[]
for _ in range(10):
 i,j=np.unravel_index(np.argmax(score),score.shape);val=float(score[i,j])
 if val<.15:break
 px,py=float(x[i,j]),float(y[i,j]);points.append({'x':px,'y':py,'prior_layer_difference_mV_at310mA':val})
 score[np.hypot(x-px,y-py)<2.5]=0
(R/'hardware/design/proposed_ground_stitches.json').write_text(json.dumps(points,indent=2)+'\n');print(points)
