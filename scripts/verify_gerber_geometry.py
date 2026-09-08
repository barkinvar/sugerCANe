"""Independent exported-geometry manufacturing screens, in millimeters.

Uses the same independent Gerber parser as the copper-connectivity review;
checks etch clearances, edge/mount clearance, annular rings and drill spacing.
Mask/paste numbers are descriptive; actual process capability is supplier-owned.
"""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import Point,box
from shapely import union_all,STRtree
from gerbonara.graphic_objects import Flash
import verify_gerber_connectivity as g

ROOT=Path(__file__).resolve().parents[1]
outline=box(0,-96,96,0)
mounts=[(4,-4),(92,-4),(4,-92),(92,-92)]
report={'units':'mm','arc_approximation_tolerance_mm':g.ERROR,'copper':{},'mask':{},'paste':{}}
for side,polys in g.islands.items():
    copper=union_all(polys)
    assert copper.difference(outline).area<1e-8
    edge=copper.distance(outline.boundary)
    mounting=min(copper.distance(Point(x,y)) for x,y in mounts)
    candidates=[]
    for i,poly in enumerate(polys):
        for j in g.trees[side].query(poly.buffer(.25)):
            if j<=i or g.root(g.offset[side]+i)==g.root(g.offset[side]+int(j)):continue
            distance=poly.distance(polys[j])
            candidates.append((distance,i,int(j)))
    distance,i,j=min(candidates)
    names=lambda n:sorted(g.root_nets[g.root(g.offset[side]+n)])
    assert distance>=.2-2*g.ERROR,(side,distance)
    assert edge>=.5-2*g.ERROR,(side,edge)
    assert mounting>=3.5-2*g.ERROR,(side,mounting)
    annular=[]
    for drill in g.drills:
        island=g.at(side,drill.x,drill.y)-g.offset[side]
        width=Point(drill.x,drill.y).distance(polys[island].boundary)-drill.aperture.diameter/2
        annular.append(width)
    assert min(annular)>=.15-2*g.ERROR,(side,min(annular))
    report['copper'][side]=dict(minimum_other_net_clearance=distance,closest_nets=[names(i),names(j)],
                              minimum_board_edge_clearance=edge,minimum_mount_center_clearance=mounting,
                              minimum_plated_hole_annular_copper=min(annular))

all_drills=g.drills+list(g.stack.drill_npth.instance.objects)
nearest=(math.inf,None,None)
for i,a in enumerate(all_drills):
    for j in range(i+1,len(all_drills)):
        b=all_drills[j]
        clearance=math.hypot(a.x-b.x,a.y-b.y)-(a.aperture.diameter+b.aperture.diameter)/2
        if clearance<nearest[0]:nearest=(clearance,i,j)
assert nearest[0]>=.25-2*g.ERROR,nearest
report['minimum_hole_to_hole_web']=nearest[0]
report['minimum_hole_edge_distance']=min(Point(d.x,d.y).distance(outline.boundary)-d.aperture.diameter/2 for d in all_drills)
for side in ['top','bottom']:
    for layer_type in ['mask','paste']:
        layer=g.stack[(side,layer_type)].instance
        primitives=[p for obj in layer.objects for p in obj.to_primitives()]
        assert all(p.polarity_dark for p in primitives)
        shapes=[g.shape(p) for p in primitives]
        islands=g.polygon_parts(union_all(shapes))
        if not islands:
            report[layer_type][side]={'openings':0};continue
        tree=STRtree(islands);gaps=[]
        for i,poly in enumerate(islands):
            for j in tree.query(poly.buffer(1)):
                if j>i:gaps.append(poly.distance(islands[j]))
        entry=dict(openings=len(islands),minimum_gap_between_separate_openings=min(gaps) if gaps else None,
                   total_open_area_mm2=sum(p.area for p in islands))
        if layer_type=='paste':
            entry['minimum_area_ratio_at_0_10mm_stencil']=min(p.area/(p.length*.10) for p in islands)
        report[layer_type][side]=entry
# C1 maximum can diameter is6.8mm (6.3+0.5). A3.6mm vertex-radius
# keepout adds placement allowance. Permit only its own required top lands.
c1_lands=union_all([g.shape(p) for obj in g.layers['top'].objects
                   if isinstance(obj,Flash) and obj.attrs.get('.P',('',''))[0]=='C1'
                   for p in obj.to_primitives()])
report['capacitor_C1_body_clearance']={}
for side,polys in g.islands.items():
    copper=union_all(polys)
    if side=='top':copper=copper.difference(c1_lands.buffer(g.ERROR))
    radial=copper.distance(Point(35,-15))
    assert radial>=3.5-2*g.ERROR,(side,'C1 body',radial)
    report['capacitor_C1_body_clearance'][side]=radial
report['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'output/fabrication').glob('*')) if p.suffix in ('.gbr','.gtl','.gbl','.gts','.gbs','.gtp','.gbp','.gto','.gbo','.gm1','.drl')}
report['result']='PASS'
report['limits']='Etch geometry only, with1um arc approximation. Annular rings use filled pad copper and drill center/diameter, not drill wander or plated thickness tolerance. Mask and paste figures do not establish stencil release, registration or assembly yield. Nominal holes and copper are not fabricated measurements.'
(ROOT/'reports/manufacturing/gerber_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
