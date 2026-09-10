"""Derive SMT-only CPL and validate it against the native-board manifest."""
from pathlib import Path
import csv,json,hashlib
from layout_contract import WIDTH, HEIGHT, BOTTOM_REFERENCES
R=Path(__file__).resolve().parents[1]
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
plan=json.loads((R/'bom/assembly_plan.json').read_text())
assert plan['factory_service']=='JLCPCB Standard PCBA, both sides'
manifest=json.loads((R/'reports/manufacturing/board_manifest.json').read_text())
physical={c['reference']:c for c in manifest['components']}
bom=list(csv.DictReader((R/'bom/Factory_BOM.csv').open()))
expected={r.strip() for c in bom for r in c['Designator'].split(',')}
manual={r.strip() for c in csv.DictReader((R/'bom/Hand_solder_BOM.csv').open()) for r in c['References'].split(',')}
assert len(expected)==129 and len(manual)==11 and not expected&manual
assert manual==set(plan['hand_solder_references']) and 'U5' not in expected
assert expected|manual=={r for r,p in parts.items() if not p.get('exclude_bom')}
native=list(csv.DictReader((R/'output/assembly/positions_smd.csv').open()))
selected=[r for r in native if r['Ref'] in expected]
assert len(selected)==129 and {r['Ref'] for r in selected}==expected
rows=[]
for r in selected:
 c=physical[r['Ref']]
 assert r['Side']==c['side']==('bottom' if r['Ref'] in BOTTOM_REFERENCES else 'top')
 assert abs(float(r['PosX'])-c['x_mm'])<1e-5 and abs(float(r['PosY'])-c['y_mm'])<1e-5
 assert abs((float(r['Rot'])-c['rotation_deg']+180)%360-180)<1e-5
 rows.append({'Designator':r['Ref'],'Mid X':f"{float(r['PosX']):.6f}mm",'Mid Y':f"{HEIGHT+float(r['PosY']):.6f}mm",'Layer':r['Side'].title(),'Rotation':r['Rot']})
dest=R/'output/assembly/CPL_JLCPCB.csv'
with dest.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# All fitted component numbered pads are soldered terminations.
joints=sum(len({p['number'] for p in physical[r]['pads'] if p['number']}) for r in expected)
report=dict(result='PASS',factory_smt_placements=129,factory_smt_types=len(bom),hand_solder_parts=11,hand_solder_through_hole_parts=10,hand_solder_through_hole_joints=49,hand_solder_mcu_joints=32,hand_solder_joints=81,loose_shunts=3,estimated_smt_joints_per_board=joints,position_origin='PCB lower-left, X right / Y up, mm; native footprint rotation counterclockwise. Factory must reconcile part-library pin 1.',matched_to='Native manifest and model/BOM exact reference sets',sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),assembly_plan_sha256=hashlib.sha256((R/'bom/assembly_plan.json').read_bytes()).hexdigest(),factory_part_allocation_confirmed=False)
report['factory_top_placements']=sum(r['Layer']=='Top' for r in rows)
report['factory_bottom_placements']=sum(r['Layer']=='Bottom' for r in rows)
report['board_size_mm']=[WIDTH,HEIGHT]
(R/'reports/manufacturing/factory_files.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
