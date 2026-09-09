"""Audit changes against a frozen Rev E electrical and purchasing baseline."""
from pathlib import Path
import json,csv
import pcbnew as p
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'hardware/design/rev_e_baseline.json').read_text())
old=base['parts'];new=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
removed={'C67','C68','C70','NT1','R64'};added={'D4','R67','U9'}
assert set(old)-set(new)==removed and set(new)-set(old)==added
power={'U8','U9','D4','L2','R67'}|{f'R{n}' for n in range(60,67)}|{f'C{n}' for n in range(60,71)}|{'NT1'}
passives={'C7','C8','C23','C24'}
changed=[]
for ref in sorted(set(old)&set(new)):
 differences=[k for k,v in old[ref].items() if new[ref].get(k)!=v]
 if differences:changed.append(dict(reference=ref,fields=differences))
 if ref not in power|passives|{'U7'}:assert not differences,(ref,differences)
 if ref in passives:assert differences==['mpn'],(ref,differences)
for pin,net in old['U7']['pins'].items():
 if pin not in ('10','11','13'):assert new['U7']['pins'][pin]==net
assert new['U9']['mpn']=='TPS2553DBVR-1'
b=p.LoadBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'));edges=[d for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts]
points={tuple(round(v,5) for v in p.ToMM(x)) for d in edges for x in (d.GetStart(),d.GetEnd())}
assert points=={(0,0),(52,0),(52,64),(0,64)}
# Attribute MOQ purchasing savings: outside-stage substitutions/resourcing first;
# the remainder includes all changed power parts and shared passive price breaks.
now={r['MPN']:float(r['purchase_usd'])/10 for r in csv.DictReader((R/'bom/cost_detail.csv').open()) if r['boards']=='10'}
was={r['MPN']:float(r['purchase_usd'])/10 for r in base['cost_10']}
oldcaps={'CC0805JRNPO9BN102','CC0805KKX7R9BB105','TMK212AB7475KG-T'}
newcaps={'CC0805JRNPO9BN102','CL21B105KBFNNNE','CL21B475KAFNNNE'}
passive_saving=sum(was[k] for k in oldcaps)-sum(now[k] for k in newcaps)
saving=sum(was.values())-sum(now.values())
report=dict(result='PASS',baseline_commit=base['source_commit'],baseline_source_sha256=base['source_sha256'],removed_parts=sorted(removed),added_parts=sorted(added),changed_parts=changed,unchanged='Connectors, removable voltage selectors, three signal/bias circuits, MCU and CAN; only the unused fourth comparator is repurposed.',board_mm=[52,64],area_reduction_percent=100*(1-64/70),cost_10_board_purchase_USD=dict(rev_e=sum(was.values()),rev_f=sum(now.values()),outside_power_passive_saving=passive_saving,power_stage_and_shared_price_break_saving=saving-passive_saving,total_saving=saving),firmware='Hardware 6 / app 0.7.0 / protocol 4; separate product and configuration tags.',scope='Contract regression and procurement arithmetic. Native ERC/DRC/copper tests are separate; no physical qualification.')
(R/'reports/variant_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
