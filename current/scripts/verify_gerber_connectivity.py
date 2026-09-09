"""Reconstruct copper connectivity independently from exported Gerber geometry.

Gerbonara parses shapes; Shapely unions actual copper on each layer. Plated
drill centers join layers. X2 pad labels provide expected net identities only;
track labels are not used to decide connectivity. Arc approximation is1um.
This is an independent geometry check, not an electrical/thermal field solver.
"""
from pathlib import Path
from collections import defaultdict
import json, math, warnings, time
import numpy as np
from gerbonara import LayerStack
from gerbonara import graphic_primitives as gp
from gerbonara.graphic_objects import Flash
from shapely.geometry import Point, LineString, Polygon, GeometryCollection, box
from shapely import union_all, make_valid, STRtree

ROOT=Path(__file__).resolve().parents[1]
start=time.monotonic()
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    stack=LayerStack.open(ROOT/'output/fabrication')
    layers={side:layer.instance for (side,use),layer in stack.graphic_layers.items() if use=='copper'}
    assert set(layers)=={'top','inner_1','inner_2','bottom'}
    drills=list(stack.drill_pth.instance.objects)
ERROR=.001

def shape(primitive):
    if isinstance(primitive,gp.Circle):
        if primitive.r<=0:return GeometryCollection()
        n=max(16,math.ceil(math.pi/(4*math.acos(max(-1,1-ERROR/primitive.r)))))
        return Point(primitive.x,primitive.y).buffer(primitive.r,quad_segs=n)
    if isinstance(primitive,gp.Line):
        r=primitive.width/2
        if r<=0:return GeometryCollection()
        n=max(16,math.ceil(math.pi/(4*math.acos(max(-1,1-ERROR/r)))))
        return LineString([(primitive.x1,primitive.y1),(primitive.x2,primitive.y2)]).buffer(r,quad_segs=n)
    if isinstance(primitive,gp.Rectangle):
        co,si=math.cos(primitive.rotation),math.sin(primitive.rotation)
        return Polygon([(primitive.x+x*co-y*si,primitive.y+x*si+y*co)
                        for x,y in [(-primitive.w/2,-primitive.h/2),
                                    (-primitive.w/2,primitive.h/2),
                                    (primitive.w/2,primitive.h/2),
                                    (primitive.w/2,-primitive.h/2)]])
    poly=primitive.to_arc_poly().approximate_arcs(max_error=ERROR)
    if len(poly.outline)<3:return GeometryCollection()
    return make_valid(Polygon(poly.outline))

def polygon_parts(geometry):
    if geometry.geom_type=='Polygon':return [geometry]
    if hasattr(geometry,'geoms'):
        return [p for g in geometry.geoms for p in polygon_parts(g)]
    return []

islands={};trees={};offset={};parent=[];areas={};counts={};copper_by_side={}
for side,layer in layers.items():
    primitives=[p for obj in layer.objects for p in obj.to_primitives()]
    # This release uses only positive copper primitives. Refuse a future clear
    # polarity instead of silently misinterpreting an unsupported export.
    assert all(p.polarity_dark for p in primitives),'Clear polarity needs ordered compositing'
    copper=union_all([shape(p) for p in primitives])
    copper_by_side[side]=copper
    islands[side]=polygon_parts(copper)
    trees[side]=STRtree(islands[side]);offset[side]=len(parent)
    parent.extend(range(len(parent),len(parent)+len(islands[side])))
    areas[side]=copper.area;counts[side]=len(islands[side])
    print(side,len(primitives),'primitives,',len(islands[side]),'copper islands',flush=True)

def root(i):
    while parent[i]!=i:
        parent[i]=parent[parent[i]];i=parent[i]
    return i
def join(a,b):
    a,b=root(a),root(b)
    if a!=b:parent[b]=a
def at(side,x,y):
    candidates=trees[side].query(Point(x,y),predicate='intersects')
    assert len(candidates)==1,(side,x,y,'expected one copper island',candidates.tolist())
    return offset[side]+int(candidates[0])

for drill in drills:
    assert isinstance(drill,Flash)
    a=at('top',drill.x,drill.y);join(a,at('bottom',drill.x,drill.y))
    for side in ('inner_1','inner_2'):
        candidates=trees[side].query(Point(drill.x,drill.y),predicate='intersects')
        assert len(candidates)<=1
        if len(candidates):join(a,offset[side]+int(candidates[0]))

net_roots=defaultdict(set);root_nets=defaultdict(set);pad_count=0
for side,layer in layers.items():
    for obj in layer.objects:
        if not isinstance(obj,Flash) or '.P' not in obj.attrs:continue
        ref,pin,*_=obj.attrs['.P']
        net=obj.attrs.get('.N',('N/C',))[0]
        if net in ('','N/C'):net=f'UNCONNECTED:{ref}.{pin}'
        r=root(at(side,obj.x,obj.y))
        net_roots[net].add(r);root_nets[r].add(net);pad_count+=1
# Intentional copper net ties. Each pair is independently checked for isolation
# everywhere outside its declared physical land/bridge, so this is not a blanket
# exemption for connecting an analog ground or Kelvin sense wire anywhere.
manifest=json.loads((ROOT/'reports/manufacturing/board_manifest.json').read_text())
fps={x['reference']:x for x in manifest['components']}
def pad(ref,pin):return next(q for q in fps[ref]['pads'] if q['number']==str(pin))
def land(q,hx,hy):return box(q['x_mm']-hx,q['y_mm']-hy,q['x_mm']+hx,q['y_mm']+hy)
ties=[] # Rev F has no intentional copper net ties.
alias={a:b for a,b,_ in ties}
# Cut only the declared physical tie lands from the top copper, then rebuild
# the plated-barrel graph. Non-tie component-pad labels must now be separated.
# This second test does not trust track net labels or globally alias grounds.
cut=union_all([region for _,_,region in ties]);ci={};ct={};co={};cp=[]
for side,copper in copper_by_side.items():
    ci[side]=polygon_parts(copper.difference(cut) if side=='top' else copper)
    ct[side]=STRtree(ci[side]);co[side]=len(cp)
    cp.extend(range(len(cp),len(cp)+len(ci[side])))
def cr(i):
    while cp[i]!=i:cp[i]=cp[cp[i]];i=cp[i]
    return i
def cat(side,x,y):
    q=ct[side].query(Point(x,y),predicate='intersects')
    assert len(q)<=1
    return co[side]+int(q[0]) if len(q) else None
for drill in drills:
    nodes=[cat(side,drill.x,drill.y) for side in layers]
    nodes=[n for n in nodes if n is not None]
    for n in nodes[1:]:cp[cr(n)]=cr(nodes[0])
cut_nets=defaultdict(set)
for side,layer in layers.items():
 for obj in layer.objects:
    if not isinstance(obj,Flash) or '.P' not in obj.attrs:continue
    ref,pin,*_=obj.attrs['.P']
    n=obj.attrs.get('.N',('N/C',))[0]
    if n in ('','N/C'):n=f'UNCONNECTED:{ref}.{pin}'
    node=cat(side,obj.x,obj.y);assert node is not None,(ref,pin,'unexpectedly inside tie removal')
    cut_nets[cr(node)].add(n)
extra_ties={str(i):sorted(n) for i,n in cut_nets.items() if len(n)>1}
assert not extra_ties,('Short outside declared copper net ties',extra_ties)
intentional_isolation=dict(method='Rev F has no intentional ties; independently rebuild all four copper layers and plated barrels and reject merged pad net identities',removed_tie_pairs=[[a,b] for a,b,_ in ties],extra_shorts=extra_ties,track_net_labels_used=False)
shorts={str(r):sorted(nets) for r,nets in root_nets.items() if len({alias.get(n,n) for n in nets})>1}
opens={net:sorted(roots) for net,roots in net_roots.items() if len(roots)>1}
orphan_area=0.0;orphan_count=0
for side,polys in islands.items():
    for i,poly in enumerate(polys):
        if root(offset[side]+i) not in root_nets:
            orphan_area+=poly.area;orphan_count+=1
result=dict(result='PASS' if not shorts and not opens else 'FAIL',
            method='Gerbonara1.6.3 plus Shapely2.1.2 copper polygon union and plated-barrel graph',
            maximum_arc_approximation_error_mm=ERROR,copper_area_mm2=areas,
            layer_island_counts=counts,plated_barrels_joined=len(drills),
            pad_layer_records=pad_count,identified_nets=len(net_roots),
            shorts=shorts,opens=opens,intentional_net_tie_isolation= intentional_isolation,unassigned_copper_islands=orphan_count,
            unassigned_copper_area_mm2=orphan_area,elapsed_seconds=time.monotonic()-start,
            limitations='Plated holes represented as connected filled pad centers; no barrel manufacturing defect, annular-ring fracture, impedance, thermal or EMC model. Positive Gerber primitives only.')
dest=ROOT/'reports/manufacturing/gerber_connectivity.json'
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert not shorts and not opens
