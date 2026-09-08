"""Greedy courtyard packing, then legal local wire-length optimization.
This aids placement only. Native DRC and manual electrical/assembly review follow.
"""
from pathlib import Path
import json,math,numpy as np
ROOT=Path(__file__).resolve().parents[1];H=ROOT/'hardware/design'
G=json.loads((H/'placement_geometry.json').read_text());M=json.loads((H/'circuit.json').read_text())['parts']
by={g['ref']:g for g in G};placed={};rects=[];refs=[]
W,HEIGHT=52,64
preferred=json.loads((H/'placement_preferred.json').read_text())
anchors={r:tuple(preferred[r][:2]) if r in preferred else tuple(g['xy']) for r,g in by.items()}
fixed=['H1','H2','J1','J2','J3','J4','J5','J6','J8','JP2','JP101','JP103','JP201','JP203','JP301','JP303',
'R63','C69','U8','L2','C61','C65','C66','C67','NT1','C68',
'F1','Q1','D3','R3','D2','C1','U1','C2','C3','C6','L1','C4','C5','C13','R1','R2',
'U5','Y1','R20','C25','C26','U6','C40','C41','D20','R40','R41','R42','U7']
critical=[r for r in ['C60','C70','C62','C63','C64','R60','R61','R62','R63','R64','R65','R66','C69','U2','C7','C8','R4','U4','R10','C11','C12','C20','C21','C22','C23','C24','C50','R103','R203','R303','C101','C201','C301','R104','R204','R304'] if r not in fixed]
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
 weight=4 if n in ['HSE_IN','HSE_OUT','HSE_XTAL_OUT','BUCK_SW','BUCK_CB','BB_SW1','BB_SW2','BUCK_FB'] else 1
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
print('Packed',len(P),'parts at 52x64 mm; zero rectangular courtyard overlap.')
for r in critical:
 if math.dist(placed[r][:2],anchors[r])>2:print('Critical move:',r,anchors[r],placed[r][:3])
