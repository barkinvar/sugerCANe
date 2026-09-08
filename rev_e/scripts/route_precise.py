"""Exact geometric raster routing aid; every result requires native DRC."""
from pathlib import Path
import json,math,heapq,sys,os
import numpy as np
from shapely.geometry import Point,LineString,box
from shapely import contains_xy
ROOT=Path(__file__).resolve().parents[1]
g=json.loads((ROOT/'hardware/design/routing_geometry.json').read_text())
NET=sys.argv[1];START=list(map(float,sys.argv[2:4]));GOAL=list(map(float,sys.argv[4:6]));START_LAYER=int(sys.argv[6]);GOAL_LAYER=int(sys.argv[7]);WIDTH=float(sys.argv[8]);VIA_DIAMETER=float(sys.argv[10]);VIA_DRILL=.3 if VIA_DIAMETER<.8 else .4
STEP=.025;N=2801;CLEAR=.202
occ=np.zeros((2,N,N),dtype=bool);vocc=np.zeros((N,N),dtype=bool)
def shape(o):
 if o['type']=='rect':return box(*o['bounds'])
 if o['type']=='circle':return Point(*o['xy']).buffer(o['radius'],quad_segs=32)
 return LineString([o['a'],o['b']]).buffer(o['width']/2,quad_segs=32)
def paint(im,z,value=True):
 if z.is_empty:return
 x1,y1,x2,y2=z.bounds;lx=max(0,math.floor(x1/STEP));rx=min(N-1,math.ceil(x2/STEP));ly=max(0,math.floor(y1/STEP));ry=min(N-1,math.ceil(y2/STEP))
 if lx>rx or ly>ry:return
 mask=contains_xy(z,np.arange(lx,rx+1)[None,:]*STEP,np.arange(ly,ry+1)[:,None]*STEP)
 view=im[ly:ry+1,lx:rx+1]
 if value:view|=mask
 else:view[mask]=False
own=[];transition=[]
for o in g['obstacles']:
 if not o['layers']:continue
 z=shape(o)
 if o['net']==NET:
  own.append((o,z))
  if o.get('smd'):paint(vocc,z.buffer(VIA_DIAMETER/2+.025,quad_segs=24))
  if set(o['layers'])=={0,1}:
   xx,yy=o['xy'] if o['type']=='circle' else ((o['bounds'][0]+o['bounds'][2])/2,(o['bounds'][1]+o['bounds'][3])/2)
   transition.append((xx,yy))
  continue
 local_clear=.510 if o.get('reference')=='J8' else CLEAR
 for l in o['layers']:paint(occ[l],z.buffer(local_clear+WIDTH/2,quad_segs=24))
 paint(vocc,z.buffer(local_clear+VIA_DIAMETER/2,quad_segs=24))
for h in g['holes']:paint(vocc,Point(*h['xy']).buffer(h['radius']+.251+VIA_DRILL/2,quad_segs=24))
# Existing, DRC-checked same-net copper permits travel inside its own width.
for o,z in own:
 safe=z.buffer(-WIDTH/2-.003)
 for l in o['layers']:paint(occ[l],safe,False)
for i,im in enumerate([occ[0],occ[1],vocc]):
 m=.301+(WIDTH/2 if i<2 else VIA_DIAMETER/2)
 im[:math.ceil(m/STEP),:]=True;im[:,:math.ceil(m/STEP)]=True
 im[math.floor((70-m)/STEP):,:]=True;im[:,math.floor((52-m)/STEP):]=True
 for x,y in [(3.5,4),(48.5,42.5)]:paint(im,Point(x,y).buffer(3.3+(WIDTH/2 if i<2 else VIA_DIAMETER/2)+.01,quad_segs=24))
for x,y in transition:
 ix,iy=round(x/STEP),round(y/STEP);vocc[iy,ix]=False
if os.environ.get('CANDI_BOOT_ESCAPE')=='1':
 paint(occ[0],box(28,0,34,10));paint(vocc,box(28,0,34,10))
start=(START_LAYER,round(START[0]/STEP),round(START[1]/STEP));goalxy=(round(GOAL[0]/STEP),round(GOAL[1]/STEP))
assert not occ[start[0],start[2],start[1]],'start blocked'
def h(s):return math.hypot(s[1]-goalxy[0],s[2]-goalxy[1])
queue=[(h(start),0,start)];dist={start:0};prev={};found=None
moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,math.sqrt(2)),(1,-1,math.sqrt(2)),(-1,1,math.sqrt(2)),(-1,-1,math.sqrt(2))]
while queue:
 _,cost,s=heapq.heappop(queue)
 if cost>dist[s]:continue
 l,x,y=s
 if (x,y)==goalxy and (GOAL_LAYER<0 or l==GOAL_LAYER):found=s;break
 for dx,dy,dc in moves:
  nx,ny=x+dx,y+dy
  if not(10<nx<N-10 and 10<ny<N-10) or occ[l,ny,nx]:continue
  if dx and dy and (occ[l,y,nx] or occ[l,ny,x]):continue
  ns=(l,nx,ny);nc=cost+dc
  if nc<dist.get(ns,1e30):dist[ns]=nc;prev[ns]=s;heapq.heappush(queue,(nc+h(ns),nc,ns))
 if not vocc[y,x]:
  ns=(1-l,x,y);nc=cost+(float(sys.argv[9]) if len(sys.argv)>9 else 50)
  if nc<dist.get(ns,1e30):dist[ns]=nc;prev[ns]=s;heapq.heappush(queue,(nc+h(ns),nc,ns))
assert found,f'No route found; explored {len(dist)} cells; goal occupancy={[bool(occ[i,goalxy[1],goalxy[0]]) for i in [0,1]]}; reached layers={set(q[0] for q in dist)}'
path=[found]
while path[-1]!=start:path.append(prev[path[-1]])
path.reverse()
# Compress straight runs while retaining layer transitions.
keep=[path[0]]
for i in range(1,len(path)-1):
 a,c,z=path[i-1:i+2]
 if (c[0]-a[0],c[1]-a[1],c[2]-a[2])!=(z[0]-c[0],z[1]-c[1],z[2]-c[2]):keep.append(c)
keep.append(path[-1])
result={'net':NET,'width':WIDTH,'via_diameter':VIA_DIAMETER,'via_drill':VIA_DRILL,'path':[[l,round(x*STEP,4),round(y*STEP,4)] for l,x,y in keep],
        'start_exact':START,'goal_exact':GOAL,'visited_states':len(dist),'length_cost_mm':dist[found]*STEP}
(ROOT/f'hardware/design/last_route_{NET}.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
