from pathlib import Path
import json,math,heapq
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];g=json.loads((R/'hardware/design/routing_geometry.json').read_text());G=json.loads((R/'hardware/design/placement_geometry.json').read_text())
pads={(c['ref'],a['pin']):a for c in G for a in c['pads'] if a['pin']};S=.05;NX=1041;NY=1121
obstacles=g['obstacles'];routes=[]
def block(net,width):
 im=Image.new('1',(NX,NY));d=ImageDraw.Draw(im);extra=width/2+.205
 for ob in obstacles:
  if 0 not in ob['layers'] or ob['net']==net:continue
  if ob['type']=='rect':
   x1,y1,x2,y2=ob['bounds'];extra=width/2+(.52 if ob.get('reference')=='J8' else .205);d.rectangle((math.floor((x1-extra)/S),math.floor((y1-extra)/S),math.ceil((x2+extra)/S),math.ceil((y2+extra)/S)),fill=1)
  elif ob['type']=='line':
   rad=ob['width']/2+extra;d.line([tuple(x/S for x in ob['a']),tuple(x/S for x in ob['b'])],fill=1,width=math.ceil(2*rad/S))
   for x,y in [ob['a'],ob['b']]:d.ellipse(((x-rad)/S,(y-rad)/S,(x+rad)/S,(y+rad)/S),fill=1)
  else:
   x,y=ob['xy'];rad=ob['radius']+extra;d.ellipse(((x-rad)/S,(y-rad)/S,(x+rad)/S,(y+rad)/S),fill=1)
 return np.array(im,dtype=bool)
def route(a,z,width=.3):
 start=pads[a];end=pads[z];net=start['net'];assert net==end['net'];occ=block(net,width)
 st=tuple(round(x/S) for x in start['xy']);en=tuple(round(x/S) for x in end['xy'])
 def h(q):return math.hypot(q[0]-en[0],q[1]-en[1])
 if occ[st[1],st[0]] or occ[en[1],en[0]]:raise RuntimeError(('blocked',a,z,net))
 Q=[(h(st),0,st)];dist={st:0};prev={};found=False
 while Q:
  _,cost,q=heapq.heappop(Q)
  if cost>dist[q]:continue
  if q==en:found=True;break
  x,y=q
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   xx,yy=x+dx,y+dy
   if not(8<xx<NX-8 and 8<yy<NY-8) or occ[yy,xx]:continue
   if dx and dy and (occ[yy,x] or occ[y,xx]):continue
   nn=(xx,yy);c=cost+(1.41421356237 if dx and dy else 1)
   if c<dist.get(nn,1e30):dist[nn]=c;prev[nn]=q;heapq.heappush(Q,(c+h(nn),c,nn))
  if len(dist)>300000:break
 if not found:raise RuntimeError(('no path',a,z,net))
 path=[en]
 while path[-1]!=st:path.append(prev[path[-1]])
 path.reverse();keep=[path[0]]
 for i in range(1,len(path)-1):
  a1,b,c=path[i-1:i+2]
  if (b[0]-a1[0],b[1]-a1[1])!=(c[0]-b[0],c[1]-b[1]):keep.append(b)
 keep.append(path[-1]);pts=[start['xy']]+[[x*S,y*S] for x,y in keep]+[end['xy']]
 if a[0]=='VIA' or z[0]=='VIA':
  if dist[en]*S>3:raise RuntimeError(('ground escape too long',a,z))
 rec=dict(net=net,width=width,layer='F.Cu',points=pts,ends=[a,z],length_mm=dist[en]*S);routes.append(rec)
 for aa,bb in zip(pts,pts[1:]):obstacles.append(dict(type='line',net=net,layers=[0],a=aa,b=bb,width=width))
 print(net,a,z,round(rec['length_mm'],2),'mm',flush=True)
# Only small local loops are locked; broad rail distribution remains for the router.
pairs=[('BUCK_SW',('U1','2'),('L1','1'),.4),('BUCK_SW',('U1','2'),('C6','2'),.3),('BUCK_CB',('U1','6'),('C6','1'),.25),('VIN_PROT',('U1','3'),('C3','1'),.35),('VIN_PROT',('C3','1'),('C2','1'),.5),('V5_INTERNAL',('L1','2'),('C4','1'),.6),('V5_INTERNAL',('C4','1'),('C5','1'),.6),('V5_INTERNAL',('C5','1'),('C13','1'),.6),('BUCK_FB',('U1','4'),('R1','2'),.2),('BUCK_FB',('R1','2'),('R2','1'),.2),('BOOST_SW',('U8','1'),('L2','2'),.35),('BOOST_SW',('U8','1'),('D4','2'),.35),('V5_INTERNAL',('U8','4'),('D4','1'),.4),('V5_INTERNAL',('D4','1'),('C15','1'),.6),('V5_INTERNAL',('D4','1'),('C16','1'),.6),('V5_INTERNAL',('U8','4'),('C17','1'),.3),('HSE_IN',('U5','2'),('Y1','1'),.2),('HSE_IN',('Y1','1'),('C25','1'),.2),('HSE_OUT',('U5','3'),('R20','1'),.18),('HSE_XTAL_OUT',('R20','2'),('Y1','3'),.2),('HSE_XTAL_OUT',('Y1','3'),('C26','1'),.2)]
pairs=[q for q in pairs if q[1] in pads and q[2] in pads]
failed=[]
for net,a,z,w in pairs:
 try:route(a,z,w)
 except RuntimeError as e:print('FAILED',e,flush=True);failed.append(str(e))
(R/'hardware/design/critical_routes.json').write_text(json.dumps({'routes':routes,'failed':failed},indent=2)+'\n')
# Ground vias directly beside local bypass returns, outside exposed solder lands.
from shapely.geometry import box,Point,LineString
from shapely.ops import unary_union
via_records=[]
def shape(o):
 if o['type']=='rect':return box(*o['bounds'])
 if o['type']=='circle':return Point(o['xy']).buffer(o['radius'])
 return LineString([o['a'],o['b']]).buffer(o['width']/2)
return_pads=[('U1','1'),('C2','2'),('C3','2'),('C4','2'),('C5','2'),('C13','2'),('U8','2'),('C15','2'),('C16','2'),('C17','2'),('U5','16'),('U5','32'),('C20','2'),('C21','2'),('C22','2'),('C23','2'),('C24','2'),('Y1','2'),('Y1','4'),('C25','2'),('C26','2'),('U2','2'),('C8','2'),('C9','2'),('U6','2'),('C40','2'),('C41','2'),('C42','2'),('U7','12'),('C50','2')]
return_pads=[k for k in return_pads if k in pads]
for k in return_pads:
 pt=np.array(pads[k]['xy'])
 keepout=unary_union([shape(o).buffer(.325+.24) for o in obstacles if o['type']=='rect' or o['net']!='GND' or o['type']=='circle'])
 candidates_v=[(round(pt[0]+dx/10,1),round(pt[1]+dy/10,1)) for dx in range(-22,23,2) for dy in range(-22,23,2)]
 candidates_v.sort(key=lambda a:math.dist(a,pt))
 success=False
 for xy in candidates_v:
  if min(xy)<.8 or xy[0]>51.2 or xy[1]>55.2 or keepout.intersects(Point(xy)):continue
  key=('VIA',str(len(via_records)));pads[key]={'xy':xy,'net':'GND'}
  try:route(k,key,.25)
  except RuntimeError:continue
  via_records.append({'net':'GND','xy':xy,'diameter':.65,'drill':.3});obstacles.append(dict(type='circle',net='GND',layers=[0,1],xy=xy,radius=.325));success=True;break
 if not success:print('GROUND VIA PENDING',k)
(R/'hardware/design/critical_routes.json').write_text(json.dumps({'routes':routes,'vias':via_records,'failed':failed},indent=2)+'\n')
