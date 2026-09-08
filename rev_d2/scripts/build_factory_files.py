"""Derive SMT-only CPL and validate it against the native-board manifest."""
from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parents[1]
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
manifest=json.loads((R/'reports/manufacturing/board_manifest.json').read_text())
physical={c['reference']:c for c in manifest['components']}
bom=list(csv.DictReader((R/'bom/Factory_BOM.csv').open()))
expected={r.strip() for c in bom for r in c['Designator'].split(',')}
manual={r.strip() for c in csv.DictReader((R/'bom/Hand_solder_BOM.csv').open()) for r in c['References'].split(',')}
assert len(expected)==98 and len(manual)==9 and not expected&manual
assert expected|manual=={r for r,p in parts.items() if not p.get('exclude_bom')}
native=list(csv.DictReader((R/'output/assembly/positions_smd_top.csv').open()))
selected=[r for r in native if r['Ref'] in expected]
assert len(selected)==98 and {r['Ref'] for r in selected}==expected
rows=[]
for r in selected:
 c=physical[r['Ref']]
 assert r['Side']=='top' and abs(float(r['PosX'])-c['x_mm'])<1e-5 and abs(float(r['PosY'])-c['y_mm'])<1e-5
 assert abs((float(r['Rot'])-c['rotation_deg']+180)%360-180)<1e-5
 rows.append({'Designator':r['Ref'],'Mid X':f"{float(r['PosX']):.6f}mm",'Mid Y':f"{64+float(r['PosY']):.6f}mm",'Layer':'Top','Rotation':r['Rot']})
dest=R/'output/assembly/CPL_JLCPCB.csv'
with dest.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# R64 has two real solder terminations plus two copper-only Kelvin sense taps.
joints=sum(len({p['number'] for p in physical[r]['pads'] if p['number']}) for r in expected)-2
report=dict(result='PASS',factory_smt_placements=98,factory_smt_types=len(bom),hand_solder_parts=9,hand_solder_joints=39,loose_shunts=3,estimated_smt_joints_per_board=joints,position_origin='PCB lower-left, X right / Y up, mm; native footprint rotation counterclockwise. Factory must reconcile part-library pin 1.',matched_to='Native manifest and model/BOM exact reference sets',sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),factory_part_allocation_confirmed=False)
(R/'reports/manufacturing/factory_files.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
