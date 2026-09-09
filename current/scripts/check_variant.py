"""Audit Rev G changes against the immutable Rev F electrical contract."""
from pathlib import Path
import json,csv,hashlib
import pcbnew as p
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'hardware/design/rev_f_baseline.json').read_text())
old=base['parts'];new=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
added={'Q2','Q3','D5','D6','C70','C71','C72','C73',*[f'R{i}' for i in range(68,76)]}
assert set(new)-set(old)==added and not set(old)-set(new)
allowed=added|{'C7','C8','C23','C24','U4','U5','U7','U8','U9','L2','D4','C60','C61','C62','C63','C64','C65','C66','R60','R62','R65','R66','R67'}
changes=[]
for ref in sorted(old):
 fields=[k for k in set(old[ref])|set(new[ref]) if old[ref].get(k)!=new[ref].get(k)]
 if fields:changes.append(dict(reference=ref,fields=sorted(fields)))
 if ref not in allowed:assert not fields,(ref,fields)
assert new['U9']['mpn']=='TPS259620DDAR'
assert all(new['U5']['pins'][pin]==net for pin,net in {'14':'ADC_5V','15':'ADC_12V','25':'POWER_5V_EN','28':'BIAS_DOWN1','29':'BIAS_DOWN2','30':'POWER_12V_EN'}.items())
for ref in ['U6','J1','J2','J3','J4','J5','J6','J8','JP101','JP201','JP301']:
 assert new[ref]==old[ref],ref
b=p.LoadBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'))
points={tuple(round(v,5) for v in p.ToMM(q)) for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts for q in (d.GetStart(),d.GetEnd())}
assert points=={(0,0),(52,0),(52,74),(0,74)}
current=sum(float(r['purchase_usd'])/10 for r in csv.DictReader((R/'bom/cost_detail.csv').open()) if r['boards']=='10')
e=json.loads((R/'hardware/design/rev_e_baseline.json').read_text());rev_e=sum(float(r['purchase_usd'])/10 for r in e['cost_10'])
report=dict(result='PASS',baseline_commit=base['source_commit'],baseline_sha256=hashlib.sha256((R/'hardware/design/rev_f_baseline.json').read_bytes()).hexdigest(),
 added_parts=sorted(added),removed_parts=[],changed_parts=changes,
 unchanged='Sensor connectors, power jumpers, CAN transceiver, MCU part, clock and three comparator/bias signal circuits. Two MCU bias-control pins moved to free ADC channels.',
 board_mm=[52,74],area_change_from_rev_f_percent=100*(74/64-1),
 cost_10_board_purchase_USD=dict(rev_e=rev_e,rev_f=27.1738,rev_g=current,saving_vs_rev_e=rev_e-current,added_vs_rev_f=current-27.1738),
 firmware='Hardware 7 / app 0.8.0 / protocol 4. New power enables and rail ADC pins; prior update image tags rejected.',
 scope='Electrical contract and procurement arithmetic; native CAD/copper verification and physical testing are separate.')
(R/'reports/variant_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
