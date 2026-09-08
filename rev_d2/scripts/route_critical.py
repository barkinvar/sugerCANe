from pathlib import Path
import json,math,heapq
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];g=json.loads((R/'hardware/design/routing_geometry.json').read_text());G=json.loads((R/'hardware/design/placement_geometry.json').read_text())
pads={(c['ref'],a['pin']):a for c in G for a in c['pads'] if a['pin']};S=.025;NX=2081;NY=2561
obstacles=g['obstacles'];routes=[]
def block(net,width):
 im=Image.new('1',(NX,NY));d=ImageDraw.Draw(im);extra=width/2+.205
 for ob in obstacles:
  if 0 not in ob['layers'] or ob['net']==net:continue
  if ob['type']=='rect':
   x1,y1,x2,y2=ob['bounds'];extra=width/2+(.52 if ob.get('reference')=='J8' else .205);d.rectangle((math.ceil((x1-extra)/S),math.ceil((y1-extra)/S),math.floor((x2+extra)/S),math.floor((y2+extra)/S)),fill=1)
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
 if a[0]=='U8' and dist[en]*S>15:raise RuntimeError(('IC route exceeds 15 mm',a,z,net))
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
# Explicit narrow escapes from the five long electrical strips. Power traces
# widen only after clearing the adjacent strip, never on the 0.5 mm pitch lands.
def direct(net,width,points,layer="F.Cu"):
 routes.append(dict(net=net,width=width,layer=layer,points=points,length_mm=sum(math.dist(a,b) for a,b in zip(points,points[1:])),intent='Reviewed converter short loop'))
 for a,b in zip(points,points[1:]):obstacles.append(dict(type='line',net=net,layers=[0 if layer=='F.Cu' else 1],a=a,b=b,width=width))
for n,net,x in [(8,'BB_SW1',16.46),(10,'BB_SW2',17.54)]:
 direct(net,.22,[(x,26),(x,23.95)])
direct('BB_SW1',.22,[(16.46,23.95),(15.78,23.27),(15.78,22.8)])
direct('BB_SW2',.22,[(17.54,23.95),(18.22,23.27),(18.22,22.8)])
direct('BB_BOOT1',.18,[(15.46,24.6),(15.46,24.1),(14.82,23.46),(14.82,22.8)])
direct('BB_BOOT2',.18,[(18.54,24.6),(18.54,24.1),(19.18,23.46),(19.18,22.8)])
direct('VIN_PROT',.22,[(15.96,26),(15.96,28.16),(15.545,28.575)])
direct('V12_RAW',.22,[(18.04,26),(18.04,29.085),(18.455,29.5)])
direct('GND',.25,[(17,26),(17,22.5)])
direct('GND',.25,[(17,26),(17,28.575),(16.505,28.575)])
direct('GND',.25,[(17,28.575),(17,29.5),(17.495,29.5)])
direct('GND',.3,[(17,29.5),(17,30.5)])
direct('BB_FB',.18,[(19.4,26.75),(19.8,26.75),(20.15,27.1)])
direct('BB_ISP',.18,[(18.54,27.4),(18.54,27.8),(19.2,28.46),(19.2,30.8)])
direct('BB_ISN',.18,[(19.04,27.375),(19.04,27.65),(20.1,28.71),(20.1,32.15)])
direct('BB_ISP',.18,[(25.42,27.3),(24.75,27.3),(24.75,28.2)])
direct('BB_ISN',.18,[(23.38,27.3),(23.9,27.3),(23.9,28.2)])
direct('V12_RAW',.4,[(25.92,26.5),(26.3,26.5),(26.3,28.1),(26.4,28.2)])
direct('SENSOR_12V',.5,[(22.88,26.5),(21.9,26.5)])
pads['POWER','1']={'xy':[26.9,26.5],'net':'V12_RAW'}
direct('V12_RAW',.4,[(18.455,29.5),(18.25,29.705),(18.25,31.4)])
direct('V12_RAW',.5,[pads['C62','1']['xy'],[24.6,31.125],[24.6,31.75]])
direct('V12_RAW',.6,[(18.25,31.4),(18.25,32.5),(18.75,33),(24.6,33),(24.6,31.75)],'B.Cu')
direct('V12_RAW',.6,[(26.4,28.2),(26.4,29.95),(24.6,31.75)],'B.Cu')
pre_vias=[dict(net='GND',xy=[17,y],diameter=.6,drill=.3) for y in [22.5,30.5]]
pre_vias += [dict(net=n,xy=xy,diameter=.6,drill=.3) for n,xy in [('BB_FB',[20.15,27.1]),('BB_ISP',[19.2,30.8]),('BB_ISN',[20.1,32.15]),('BB_ISP',[24.75,28.2]),('BB_ISN',[23.9,28.2])]]
pre_vias += [dict(net='V12_RAW',xy=xy,diameter=.8,drill=.4) for xy in [[18.25,31.4],[24.6,31.75],[26.4,28.2]]]
for q in pre_vias:obstacles.append(dict(type='circle',net=q['net'],layers=[0,1],xy=q['xy'],radius=q['diameter']/2))
# Only short critical loops are locked; broad rail distribution follows.
pairs=[('BUCK_SW',('U1','2'),('L1','1'),.4),('BUCK_SW',('U1','2'),('C6','2'),.3),('BUCK_CB',('U1','6'),('C6','1'),.25),('VIN_PROT',('U1','3'),('C3','1'),.35),('VIN_PROT',('C3','1'),('C2','1'),.5),('V5_INTERNAL',('L1','2'),('C4','1'),.6),('V5_INTERNAL',('C4','1'),('C5','1'),.6),('V5_INTERNAL',('C5','1'),('C13','1'),.6),('BUCK_FB',('U1','4'),('R1','2'),.2),('BUCK_FB',('R1','2'),('R2','1'),.2),('BOOST_SW',('U8','1'),('L2','2'),.35),('BOOST_SW',('U8','1'),('D4','2'),.35),('V5_INTERNAL',('U8','4'),('D4','1'),.4),('V5_INTERNAL',('D4','1'),('C15','1'),.6),('V5_INTERNAL',('D4','1'),('C16','1'),.6),('V5_INTERNAL',('U8','4'),('C17','1'),.3),('HSE_IN',('U5','2'),('Y1','1'),.2),('HSE_IN',('Y1','1'),('C25','1'),.2),('HSE_OUT',('U5','3'),('R20','1'),.18),('HSE_XTAL_OUT',('R20','2'),('Y1','3'),.2),('HSE_XTAL_OUT',('Y1','3'),('C26','1'),.2)]
pairs=[q for q in pairs if q[1] in pads and q[2] in pads and not q[0].startswith('BOOST') and q[1][0]!='U8']
pairs += [('BB_SW1',('C66','2'),('L2','1'),.4),('BB_SW2',('C67','2'),('L2','2'),.4),
 ('VIN_PROT',('C61','1'),('C60','1'),.5),('VIN_PROT',('C60','1'),('C70','1'),.6),
 ('V12_RAW',('C65','1'),('C62','1'),.5),('V12_RAW',('C62','1'),('C63','1'),.6),('V12_RAW',('C63','1'),('C64','1'),.6),
 ('V12_RAW',('POWER','1'),('C62','1'),.5),('BB_ISP',('U8','12'),('R64','3'),.18),
 ('BB_ISN',('U8','13'),('R64','4'),.18),('BB_ISN',('R64','4'),('R60','1'),.18),
 ('BB_FB',('U8','14'),('R60','2'),.18),('BB_FB',('R60','2'),('R61','1'),.2),
 ('BB_COMP',('U8','15'),('R63','1'),.18),('BB_COMP_RC',('R63','2'),('C69','1'),.2),
 ('V5_INTERNAL',('U8','18'),('C68','1'),.22),('GND',('NT1','2'),('C68','2'),.25)]
# Reserve the fine-pitch signal escapes before routing the wider output bank.
priority={'BB_COMP':0,'BB_FB':1,'V5_INTERNAL':4,'BB_ISN':2,'BB_ISP':2}
pairs=[q for q in pairs if q[0] not in ['BB_ISP','BB_ISN'] and not(q[0]=='BB_FB' and q[1][0]=='U8') and q[1][0] not in ['POWER','C65']]
pairs.sort(key=lambda q:priority.get(q[0],3))
failed=[]
for net,a,z,w in pairs:
 try:route(a,z,w)
 except RuntimeError as e:print('FAILED',e,flush=True);failed.append(str(e))
(R/'hardware/design/critical_routes.json').write_text(json.dumps({'routes':routes,'failed':failed},indent=2)+'\n')
# Ground vias directly beside local bypass returns, outside exposed solder lands.
from shapely.geometry import box,Point,LineString
from shapely.ops import unary_union
via_records=list(pre_vias)
def shape(o):
 if o['type']=='rect':return box(*o['bounds'])
 if o['type']=='circle':return Point(o['xy']).buffer(o['radius'])
 return LineString([o['a'],o['b']]).buffer(o['width']/2)
return_pads=[('U1','1'),('C2','2'),('C3','2'),('C4','2'),('C5','2'),('C13','2'),('U8','2'),('C15','2'),('C16','2'),('C17','2'),('U5','16'),('U5','32'),('C20','2'),('C21','2'),('C22','2'),('C23','2'),('C24','2'),('Y1','2'),('Y1','4'),('C25','2'),('C26','2'),('U2','2'),('C8','2'),('C9','2'),('U6','2'),('C40','2'),('C41','2'),('C42','2'),('U7','12'),('C50','2')]
return_pads=[k for k in return_pads if k in pads and pads[k]['net']=='GND']
return_pads += [(r,'2') for r in ['C60','C70','C62','C63','C64','C68']]
for k in return_pads:
 pt=np.array(pads[k]['xy'])
 keepout=unary_union([shape(o).buffer(.325+.24) for o in obstacles if o['type']=='rect' or o['net']!='GND' or o['type']=='circle'])
 candidates_v=[(round(pt[0]+dx/10,1),round(pt[1]+dy/10,1)) for dx in range(-22,23,2) for dy in range(-22,23,2)]
 candidates_v.sort(key=lambda a:math.dist(a,pt))
 success=False
 for xy in candidates_v:
  if min(xy)<.8 or xy[0]>51.2 or xy[1]>63.2 or keepout.intersects(Point(xy)):continue
  key=('VIA',str(len(via_records)));pads[key]={'xy':xy,'net':'GND'}
  try:route(k,key,.25)
  except RuntimeError:continue
  via_records.append({'net':'GND','xy':xy,'diameter':.65,'drill':.3});obstacles.append(dict(type='circle',net='GND',layers=[0,1],xy=xy,radius=.325));success=True;break
 if not success:print('GROUND VIA PENDING',k)
(R/'hardware/design/critical_routes.json').write_text(json.dumps({'routes':routes,'vias':via_records,'failed':failed},indent=2)+'\n')
