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
from shapely.geometry import Point, LineString, Polygon, GeometryCollection
from shapely import union_all, make_valid, STRtree

ROOT=Path(__file__).resolve().parents[1]
start=time.monotonic()
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    stack=LayerStack.open(ROOT/'output/fabrication')
    layers={side:stack[(side,'copper')].instance for side in ('top','bottom')}
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

islands={};trees={};offset={};parent=[];areas={};counts={}
for side,layer in layers.items():
    primitives=[p for obj in layer.objects for p in obj.to_primitives()]
    # This release uses only positive copper primitives. Refuse a future clear
    # polarity instead of silently misinterpreting an unsupported export.
    assert all(p.polarity_dark for p in primitives),'Clear polarity needs ordered compositing'
    copper=union_all([shape(p) for p in primitives])
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
    join(at('top',drill.x,drill.y),at('bottom',drill.x,drill.y))

net_roots=defaultdict(set);root_nets=defaultdict(set);pad_count=0
for side,layer in layers.items():
    for obj in layer.objects:
        if not isinstance(obj,Flash) or '.P' not in obj.attrs:continue
        ref,pin,*_=obj.attrs['.P']
        net=obj.attrs.get('.N',('N/C',))[0]
        if net in ('','N/C'):net=f'UNCONNECTED:{ref}.{pin}'
        r=root(at(side,obj.x,obj.y))
        net_roots[net].add(r);root_nets[r].add(net);pad_count+=1
shorts={str(r):sorted(nets) for r,nets in root_nets.items() if len(nets)>1}
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
            shorts=shorts,opens=opens,unassigned_copper_islands=orphan_count,
            unassigned_copper_area_mm2=orphan_area,elapsed_seconds=time.monotonic()-start,
            limitations='Plated holes represented as connected filled pad centers; no barrel manufacturing defect, annular-ring fracture, impedance, thermal or EMC model. Positive Gerber primitives only.')
dest=ROOT/'reports/manufacturing/gerber_connectivity.json'
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert not shorts and not opens
