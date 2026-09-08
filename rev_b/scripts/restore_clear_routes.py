"""Restore useful reviewed routes only where current other-net copper clears them."""
from pathlib import Path
import json,sys
import sexpdata as s
from shapely.geometry import Point,LineString,box
from shapely import STRtree
R=Path(__file__).resolve().parents[1];H=R/'hardware';net=sys.argv[1]
g=json.loads((H/'design/routing_geometry.json').read_text());path=H/'finishing.kicad_pcb';b=s.loads(path.read_text())
def data(a):return {str(c[0]):c[1:] for c in a[1:] if isinstance(c,list)}
def shape(o):
 if o['type']=='rect':return box(*o['bounds'])
 if o['type']=='circle':return Point(*o['xy']).buffer(o['radius'],quad_segs=24)
 return LineString([o['a'],o['b']]).buffer(o['width']/2,quad_segs=24)
polys=[[],[]]
for o in g['obstacles']:
 if o['net']==net:continue
 for layer in o['layers']:polys[layer].append(shape(o))
trees=[STRtree(x) for x in polys]
existing={str(data(a).get('uuid')) for a in b if isinstance(a,list) and str(a[0]) in ['segment','via']}
source=s.loads((H/'grounded.kicad_pcb').read_text());accepted=[];rejected=[]
for a in source:
 if not isinstance(a,list) or str(a[0]) not in ['segment','via']:continue
 d=data(a)
 if d.get('net')!=[net] or str(d.get('uuid')) in existing:continue
 if net=='GND' and str(a[0])=='via':continue # original ground vias are retained
 if net=='VBAT_FAULT_N' and any(len(d.get(k,[]))>=2 and d[k][0]<14 and d[k][1]>39 for k in ['start','end','at']):continue
 if str(a[0])=='segment':
  if d['start']==d['end']:continue
  poly=LineString([d['start'],d['end']]).buffer(d['width'][0]/2,quad_segs=24);layers=[0 if d['layer']==['F.Cu'] else 1]
 else:poly=Point(*d['at']).buffer(d['size'][0]/2,quad_segs=24);layers=[0,1]
 clear=all(all(poly.distance(polys[l][int(i)])>=.2-1e-6 for i in trees[l].query(poly.buffer(.201))) for l in layers)
 if clear:b.append(a);accepted.append(d.get('uuid'))
 else:rejected.append(d.get('uuid'))
path.write_text(s.dumps(b));report=dict(net=net,restored=len(accepted),rejected=len(rejected),accepted=accepted)
(R/f'reports/restored_{net}.json').write_text(json.dumps(report,indent=2)+'\n');print(net,'restored',len(accepted),'rejected',len(rejected))
