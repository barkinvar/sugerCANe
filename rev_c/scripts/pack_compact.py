"""Greedy courtyard packing, then legal local wire-length optimization.
This aids placement only. Native DRC and manual electrical/assembly review follow.
"""
from pathlib import Path
import json,math,numpy as np
ROOT=Path(__file__).resolve().parents[1];H=ROOT/'hardware/design'
G=json.loads((H/'placement_geometry.json').read_text());M=json.loads((H/'circuit.json').read_text())['parts']
by={g['ref']:g for g in G};placed={};rects=[];refs=[]
W,HEIGHT=52,56
preferred=json.loads((H/'placement_preferred.json').read_text())
anchors={r:tuple(preferred[r][:2]) if r in preferred else tuple(g['xy']) for r,g in by.items()}
fixed=['H1','H2','J1','J2','J3','J4','J5','J6','J8']
for ch,cx in enumerate([10,26,42],1):
 for offset,dx in [(1,-3),(3,3)]:
  r=f'JP{ch*100+offset}';fixed.append(r);anchors[r]=(cx+dx,43.5);preferred[r]=[cx+dx,43.5,0]
anchors['JP2']=(17,4);preferred['JP2']=[17,4,90];fixed.append('JP2')
critical=[r for r in ['F1','Q1','D3','R3','D2','C1','U1','C2','C3','C6','L1','C4','C5','C13','R1','R2','U5','U7','Y1','R20','C25','C26','C20','C21','C22','C23','C24','U2','C7','C8','R4','U6','C40','C41','D20','R40','R41','R42','JP2','U3','R5','C14','C9','C10','U4','R10','C11','C12','C50'] if r in M and r not in fixed]
manual={'C301':(37.5,31.3,0),'R303':(41.5,31.3,0),'R304':(41,34.3,90),'R103':(36,41.1,0),'C101':(40,41.1,0),'R203':(43.3,37.5,90),'C201':(43.5,40.75,0),'C50':(33,41.8,270),'C20':(37.5,18.5,0),'C21':(33,30,270),'C23':(30.5,30,270),'C22':(46,29,270),'C24':(49,29,90),'D101':(18,48,90),'D201':(34,48,90),'D301':(49.95,48,90),
'U1':(13.5,23,180),'L1':(22.3,24,0),'C1':(4.75,23,90),
'C2':(19,16.9,0),'C3':(16.7,20.5,270),'C6':(13.5,26.5,0),'R1':(10.25,21.5,270),'R2':(10.25,25.5,270),
'C4':(24.3,18,90),'C5':(27.7,18,90),'C13':(31.1,18,90),
'U5':(39.5,25,0),'Y1':(31,23,180),'R20':(31,27,180),'C25':(34,17.5,90),'C26':(28,27.2,270),
'U7':(35,36.2,90)}
for r,xy in manual.items():anchors[r]=xy[:2];preferred[r]=list(xy);fixed.append(r)
anchors['D2']=(23,12.5);preferred['D2']=[23,12.5,0]
# Put input divider/filter/feedback parts near their actual comparator input pins.
for ch,xy in [(1,(36,40.5)),(2,(42,38.5)),(3,(41,32))]:
 for suf in [1,3,4,5]:
  r=f'R{ch*100+suf}'
  if r not in fixed:anchors[r]=xy;critical.append(r)
 r=f'C{ch*100+1}'
 if r not in fixed:anchors[r]=xy;critical.append(r)
input_parts=[f'{p}{ch*100+n}' for ch in [1,2,3] for p,n in [('R',3),('C',1),('R',4),('R',1),('R',5)]]
critical=[r for r in input_parts if r not in fixed]+[r for r in critical if r not in fixed and r not in input_parts]
# Starting headings from initial placement; rotate shape about its origin.
def geom(r,a):
 g=by[r];x,y=g['xy'];bb=g['bbox'];cs=np.array([[bb[0]-x,bb[1]-y],[bb[2]-x,bb[1]-y],[bb[2]-x,bb[3]-y],[bb[0]-x,bb[3]-y]])
 theta=math.radians(a-g['angle']);rot=np.array([[math.cos(theta),math.sin(theta)],[-math.sin(theta),math.cos(theta)]])
 q=cs@rot.T
 return np.r_[q.min(0),q.max(0)]
# All pairs on smaller nets; rail/GND center attraction would distort placement.
edges={r:[] for r in by};netparts={}
for r,c in M.items():
 for n in set(c['pins'].values()):
  if n:netparts.setdefault(n,[]).append(r)
for n,rr in netparts.items():
 if n=='GND' or len(rr)>12:continue
 weight=4 if n in ['HSE_IN','HSE_OUT','HSE_XTAL_OUT','BUCK_SW','BUCK_CB','BOOST_SW','BUCK_FB'] else 1
 for r in rr:edges[r].extend((v,weight/(len(rr)-1)) for v in rr if v!=r)
order=fixed+critical+[r for r in by if r.startswith('JP')]+sorted([r for r in by if r not in fixed+critical and not r.startswith('JP')],key=lambda r:-np.prod(np.array(by[r]['bbox'][2:])-by[r]['bbox'][:2]))
order=list(dict.fromkeys(order))
xs,ys=np.meshgrid(np.arange(1,W-.99,.5),np.arange(1,HEIGHT-.99,.5));candidates=np.c_[xs.ravel(),ys.ravel()]
def choose(r,initial=False):
 anchor=np.array(anchors[r]);baseangle=preferred.get(r,[0,0,by[r]['angle']])[2]
 angles=[baseangle] if r in fixed or r in ['U1','U5','U7','Y1','U8'] else [baseangle,(baseangle+90)%360]
 best=None
 for a in angles:
  off=geom(r,a)
  pts=np.array([anchor]) if r in fixed else candidates
  rr=np.c_[pts,pts]+off
  ok=(rr[:,0]>=.25)&(rr[:,2]<=W-.25)
  if r not in ['J1','J2','J3','J4','J5','J6']:ok &= (rr[:,1]>=.25)&(rr[:,3]<=HEIGHT-.25)
  for other,bb in placed.items():
   if other==r:continue
   q=bb[3]
   overlap=(rr[:,0]<q[2]+.05)&(rr[:,2]>q[0]-.05)&(rr[:,1]<q[3]+.05)&(rr[:,3]>q[1]-.05)
   ok &= ~overlap
  if not ok.any():continue
  legal=pts[ok];boxes=rr[ok]
  cost=np.sum((legal-anchor)**2,axis=1)*(.5 if r in critical else .08)
  for neighbor,weight in edges.get(r,[]):
   if neighbor in placed:cost+=weight*np.abs(legal-np.array(placed[neighbor][:2])).sum(1)
  # Core signal parts stay away from connector and selector access areas.
  if r in critical:cost+=np.sum((legal-anchor)**2,axis=1)*12
  k=cost.argmin();score=cost[k]+(0 if a==by[r]['angle'] else .2)
  if best is None or score<best[0]:best=(score,*legal[k],a,boxes[k])
 if best is None:
  print('FAILED',r,anchor,geom(r,angles[0]), 'box', np.r_[anchor,anchor]+geom(r,angles[0]))
  for k,z in placed.items():
   bb=z[3];rr=np.r_[anchor,anchor]+geom(r,angles[0])
   if rr[0]<bb[2]+.05 and rr[2]>bb[0]-.05 and rr[1]<bb[3]+.05 and rr[3]>bb[1]-.05:print('HITS',k,bb)
  raise RuntimeError('No legal placement '+r)
 _,x,y,a,bb=best;placed[r]=(x,y,a,bb)
for r in order:choose(r,True)
for _ in range(2):
 for r in reversed(order):
  if r not in fixed+critical:choose(r)
P={r:[float(v[0]),float(v[1]),float(v[2])] for r,v in placed.items() if r in M}
(H/'compact_placement.json').write_text(json.dumps(P,indent=2)+'\n')
print('Packed',len(P),'parts at 52x56 mm; zero rectangular courtyard overlap.')
for r in critical:
 if math.dist(placed[r][:2],anchors[r])>2:print('Critical move:',r,anchors[r],placed[r][:3])
