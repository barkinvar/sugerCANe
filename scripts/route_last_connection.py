"""Conservative raster A* for a single remaining low-current port-bias branch.
Not a general PCB router. All output is subsequently checked by KiCad DRC.
"""
from pathlib import Path
import json,math,heapq,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
g=json.loads((ROOT/'hardware/design/routing_geometry.json').read_text())
NET=sys.argv[1];START=[float(x) for x in sys.argv[2:4]];GOAL=[float(x) for x in sys.argv[4:6]];START_LAYER=int(sys.argv[6]);GOAL_LAYER=int(sys.argv[7]);STEP=.1;N=961;WIDTH=float(sys.argv[8]) if len(sys.argv)>8 else .5;CLEAR=.25 # extra margin for rasterization
VIA_DIAMETER=float(sys.argv[10]) if len(sys.argv)>10 else .8
VIA_DRILL=.3 if VIA_DIAMETER<.8 else .4
ims=[Image.new('1',(N,N)),Image.new('1',(N,N))]
vims=[Image.new('1',(N,N)),Image.new('1',(N,N))]
def drawobs(image,ob,extra):
 d=ImageDraw.Draw(image)
 if ob['type']=='rect':
  x1,y1,x2,y2=ob['bounds'];d.rectangle((math.floor((x1-extra)/STEP),math.floor((y1-extra)/STEP),math.ceil((x2+extra)/STEP),math.ceil((y2+extra)/STEP)),fill=1)
 elif ob['type']=='circle':
  x,y=ob['xy'];r=ob['radius']+extra;d.ellipse(((x-r)/STEP,(y-r)/STEP,(x+r)/STEP,(y+r)/STEP),fill=1)
 else:
  r=ob['width']/2+extra
  d.line([tuple(x/STEP for x in ob['a']),tuple(x/STEP for x in ob['b'])],fill=1,width=math.ceil(2*r/STEP))
  for x,y in [ob['a'],ob['b']]:d.ellipse(((x-r)/STEP,(y-r)/STEP,(x+r)/STEP,(y+r)/STEP),fill=1)
for ob in g['obstacles']:
 if ob.get('smd'):
  for l in ob['layers']:drawobs(vims[l],ob,VIA_DIAMETER/2+.2) # Keep vias out of solder lands.
 if ob['net']==NET:continue
 for l in ob['layers']:
  drawobs(ims[l],ob,CLEAR+WIDTH/2);drawobs(vims[l],ob,CLEAR+VIA_DIAMETER/2)
for hole in g['holes']:
 x,y=hole['xy'];r=hole['radius']+.25+VIA_DRILL/2
 for im in vims:ImageDraw.Draw(im).ellipse(((x-r)/STEP,(y-r)/STEP,(x+r)/STEP,(y+r)/STEP),fill=1)
for im in ims+vims:
 d=ImageDraw.Draw(im)
 d.rectangle((0,0,N-1,5),fill=1);d.rectangle((0,N-6,N-1,N-1),fill=1);d.rectangle((0,0,5,N-1),fill=1);d.rectangle((N-6,0,N-1,N-1),fill=1)
occ=np.stack([np.array(im,dtype=bool) for im in ims]);vocc=np.logical_or(np.array(vims[0],dtype=bool),np.array(vims[1],dtype=bool))
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
assert found,'No route found'
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
