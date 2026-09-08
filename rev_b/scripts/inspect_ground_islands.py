from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import types
g=types.ModuleType('g');g.__dict__['__file__']=str(Path(__file__).with_name('verify_gerber_connectivity.py'))
exec(Path(g.__file__).read_text().replace('assert not shorts and not opens',''),g.__dict__)
from gerbonara.graphic_objects import Flash
for side,polys in g.islands.items():
 for i,p in enumerate(polys):
  root=g.root(g.offset[side]+i)
  if root not in g.root_nets:
   print('ORPHAN',side,root,p.area,p.bounds)
for d in g.drills:
 root=g.root(g.at('top',d.x,d.y))
 if root not in g.root_nets:print('ORPHAN_VIA',d.x,-d.y,d.aperture.diameter)

for side,layer in g.layers.items():
 for obj in layer.objects:
  if isinstance(obj,Flash) and '.P' in obj.attrs and obj.attrs.get('.N',('',''))[0]=='GND':
   print('GND_PAD',side,obj.attrs['.P'],obj.x,-obj.y,g.root(g.at(side,obj.x,obj.y)))
