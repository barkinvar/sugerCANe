"""Simplified mechanical envelopes; manufacturer drawings control purchase/tooling."""
from pathlib import Path
import cadquery as cq
import json
R=Path(__file__).resolve().parents[1]; D=R/'hardware/library/3d'
manifest=[]
def box(x,y,z,xyz):return cq.Workplane('XY').box(x,y,z).translate(xyz)
for n in [2,3]:
 name=f'Weidmuller_LSF_135_{n}P';a=cq.Assembly(name=name)
 width=(n-1)*3.5+4.2
 # Local PCB Y is inverted in STEP; seating plane is Z=0.
 body=box(width,12.7,12.9,((n-1)*1.75,-1.75,6.45))
 for i in range(n):
  body=body.cut(box(2.5,2.0,3.0,(i*3.5,-7.9,8.5)))
  a.add(box(1.3,1.8,.5,(i*3.5,-3.8,12.7)),name=f'actuator_{i}',color=cq.Color(.95,.45,.1))
  for j,y in enumerate([0,-5]):a.add(box(.5,.8,3.5,(i*3.5,y,-1.75)),name=f'leg_{i}_{j}',color=cq.Color(.7,.7,.72))
 a.add(body,name='housing',color=cq.Color(.13,.14,.15));a.export(str(D/(name+'.step')))
 manifest.append(dict(name=name,body_mm=[width,12.7,12.9],lead_projection_mm=3.5,source=f'https://datasheet.weidmueller.com/pdf/en/{1885650000 if n==2 else 1885660000}/scope/1/',note='Nominal envelope; actuator/wire openings illustrative.'))
name='Bourns_SRP4020TA';a=cq.Assembly(name=name)
a.add(box(4.45,4.06,1.85,(0,0,1.075)),name='body',color=cq.Color(.12,.12,.14))
for i,x in enumerate([-1.85,1.85]):a.add(box(.6,2.4,.3,(x,0,.15)),name=f'terminal_{i}',color=cq.Color(.65,.65,.67))
a.export(str(D/(name+'.step')));manifest.append(dict(name=name,body_mm=[4.45,4.06,2.0],source='https://www.bourns.com/docs/product-datasheets/srp4020ta.pdf',note='Maximum body envelope; recommended copper lands are separately defined in footprint.'))
(D/'rev_b_models.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Generated',len(manifest),'mechanical envelopes')
