"""Factory coordinates, placement cross-checks and a minimal Gerber ZIP."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import zipfile
import sexpdata as sx

R=Path(__file__).resolve().parents[1]
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
b=sx.loads((R/'hardware/FRC_Sensor_CAN.kicad_pcb').read_text())
def tag(x,t):return isinstance(x,list) and x and str(x[0])==t
def child(x,t):return next((c for c in x if tag(c,t)),None)
manifest=json.loads((R/'reports/manufacturing/board_manifest.json').read_text())
byref={q['reference']:q for q in manifest['components']}
cpl=[];pinmap=[];offsets=[];counts=Counter();types={'SMT':set(),'THT':set()}
for fp in b:
    if not tag(fp,'footprint'):continue
    ref=next(q[2] for q in fp if tag(q,'property') and q[1]=='Reference')
    if ref not in parts or parts[ref].get('exclude_bom'):continue
    c=parts[ref];m=byref[ref]
    attr=child(fp,'attr');kind='SMT' if sx.Symbol('smd') in attr else 'THT'
    counts[kind+'_placements']+=1;types[kind].add(c['mpn'])
    counts[kind+'_solder_joints']+=sum(1 for p in fp if tag(p,'pad') and p[1] and str(p[2]) in ('smd','thru_hole'))
    dx=dy=0.0
    if ref in ['J1','J2','J3','J4','J5','J6']:
        # Center of fixed housing, excluding projecting spring actuators.
        dx=(len(c['pins'])-1)*3.5/2;dy=(-1.7+10.0)/2
        pads=[p for p in fp if tag(p,'pad') and p[1]]
        assert len(pads)==2*len(c['pins'])
        assert sorted({float(child(p,'at')[2]) for p in pads})==[0.,7.]
        assert all(abs(float(child(p,'drill')[1])-1.1)<1e-6 for p in pads)
    elif ref.startswith('JP'):
        n=len(c['pins']);cols=2 if n==6 else 1
        dx=(cols-1)*1.;dy=(n//cols-1)*1.
    a=math.radians(m['rotation_deg'])
    x=m['x_mm']+dx*math.cos(a)+dy*math.sin(a)
    y=68+m['y_mm']+dx*math.sin(a)-dy*math.cos(a)
    assert 0<=x<=60 and 0<=y<=68,(ref,x,y)
    cpl.append({'Designator':ref,'Mid X':f'{x:.6f}mm','Mid Y':f'{y:.6f}mm',
                'Layer':'Top','Rotation':f"{m['rotation_deg']%360:.6f}"})
    offsets.append(dict(reference=ref,assembly=kind,native_origin_x_mm=m['x_mm'],
        native_origin_y_up_mm=m['y_mm'],local_body_center_x_mm=dx,local_body_center_y_down_mm=dy,
        factory_center_x_mm=x,factory_center_y_mm=y,rotation_ccw_deg=m['rotation_deg']%360))
    for p in m['pads']:
        if not p['number']:continue
        pinmap.append(dict(Reference=ref,Pin=p['number'],Net=p['net'],
                           X_mm=p['x_mm'],Y_mm=68+p['y_mm']))
assert len(cpl)==144 and len({r['Designator'] for r in cpl})==144
counts['SMT_types']=len(types['SMT']);counts['THT_types']=len(types['THT'])
def write(path,rows):
    with (R/path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('output/assembly/CPL_JLCPCB.csv',cpl)
write('output/assembly/pad_coordinates.csv',pinmap)
write('output/assembly/coordinate_offsets.csv',offsets)
(R/'reports/factory_placement.json').write_text(json.dumps(dict(result='PASS',counts=dict(counts),
    origin='Lower-left PCB corner viewed from top; millimeters, +X right, +Y up',
    rotation='Native KiCad top-side degrees, counterclockwise; factory library rotation reconciliation required',
    center='SMT footprints use native body-center origins. THT center offsets explicitly applied; pad coordinates are authoritative.',
    checked='BOM/placement bijection; 144 references; all centers within PCB; horizontal connector holes 7mm rows and 1.1mm drills.',
    limitations='Not a JLCPCB preview approval. All 50 fitted MPNs and pin-one/polarity orientation must be matched by the assembler.'),indent=2)+'\n')
(R/'order').mkdir(exist_ok=True)
extensions={'.gtl','.gbl','.gts','.gbs','.gto','.gbo','.gtp','.gbp','.gm1','.drl','.gbrjob'}
files=[p for p in (R/'output/fabrication').iterdir() if p.suffix in extensions]
assert len([p for p in files if p.suffix=='.drl'])==2
with zipfile.ZipFile(R/'order/RevB2_Gerbers.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,p.name)
(R/'reports/factory_counts.json').write_text(json.dumps(dict(counts),indent=2)+'\n')
print(dict(counts))
