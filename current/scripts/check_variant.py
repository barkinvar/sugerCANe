"""Audit Rev H against the immutable Rev G circuit contract."""
from pathlib import Path
import json,csv,hashlib,math
import pcbnew as p
R=Path(__file__).resolve().parents[1]
basefile=R/'hardware/design/rev_g_baseline.json';base=json.loads(basefile.read_text())
old=base['parts'];new=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
added={'U10','R31','C74','C75'}
assert set(new)-set(old)==added and not set(old)-set(new)
allowed=added|{'U5','J8','R30','D10'};changes=[]
substitutions=json.loads((R/'bom/jlc_sourcing.json').read_text())['substitutions']
procurement={r:s for s in substitutions for r in s['references']}
for ref in sorted(old):
 fields=[k for k in set(old[ref])|set(new[ref]) if old[ref].get(k)!=new[ref].get(k)]
 if fields:changes.append(dict(reference=ref,fields=sorted(fields)))
 if ref=='C1':
  cap=json.loads((R/'bom/jlc_sourcing.json').read_text())['capacitor_reflow_review']
  assert old[ref]==cap['before'] and new[ref]==cap['after']
  assert set(fields)=={'mpn','footprint','source_footprint','note'},fields
 elif ref in ('U1','L1'):
  buck=json.loads((R/'bom/jlc_sourcing.json').read_text())['buck_margin_review']
  assert old[ref]==buck['before'][ref] and new[ref]==buck['after'][ref]
  assert set(fields)==set(buck['changed_fields'][ref]),(ref,fields)
 elif ref in procurement:
  s=procurement[ref]
  assert old[ref]['mpn']==s['old_mpn'] and new[ref]['mpn']==s['new_mpn']
  if ref in ('C25','C26'):
   assert set(fields)=={'mpn','value'} and old[ref]['value']==s['old_value']=='30pF' and new[ref]['value']==s['value']=='20pF'
  else:assert fields==['mpn'],(ref,fields)
 elif ref not in allowed:assert not fields,(ref,fields)
assert {k:v for k,v in old['U5'].items() if k!='pins'}=={k:v for k,v in new['U5'].items() if k!='pins'}
assert {k:v for k,v in old['U5']['pins'].items() if k!='26'}=={k:v for k,v in new['U5']['pins'].items() if k!='26'}
assert new['U5']['pins']['26']=='STATUS_DATA'
assert new['J8']['pins']==old['J8']['pins']
assert new['D10']['mpn']=='SK6805-EC15' and new['U10']['mpn']=='SN74AHCT1G125DBVR'
b=p.LoadBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'))
points={tuple(round(v,5) for v in p.ToMM(q)) for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts for q in (d.GetStart(),d.GetEnd())}
assert points=={(1.5,0),(50.5,0),(52,1.5),(52,72.5),(50.5,74),(1.5,74),(0,72.5),(0,1.5)}
current=sum(float(r['purchase_usd'])/10 for r in csv.DictReader((R/'bom/cost_detail.csv').open()) if r['boards']=='10')
report=dict(result='PASS',baseline_commit=base['source_commit'],baseline_sha256=hashlib.sha256(basefile.read_bytes()).hexdigest(),
 added_parts=sorted(added),removed_parts=[],changed_parts=changes,
 procurement_substitutions=substitutions,
 unchanged='Sensor-output current limits, protection, comparator/bias and CAN topology retained. Internal buck now uses LMR51430XDDCR with SRP7028A-8R2M, in unchanged footprints. Five passive MPN types use equal-value JLC parts; C25/C26 are 20 pF for crystal startup gain margin. C1 uses the high-reflow Panasonic FT capacitor and size-D lands. MCU remains STM32F042K6T6; PB3 sends RGB data. J8 electrical pin numbers retained, physical pattern replaced.',
 board_mm=[52,74],corner_radius_mm=1.5,bounding_box_area_change_from_rev_g_percent=0,
 area_change_from_rev_g_percent=-(4-math.pi)*1.5**2/(52*74)*100,
 cost_10_board_purchase_USD=dict(rev_g=base['cost_10_board_purchase_usd'],rev_h=current,added_vs_rev_g=current-base['cost_10_board_purchase_usd']),
 firmware='Hardware 8 / app 0.9.0 / boot 1.1.0 / protocol 4. Rev H image tag prevents accidental cross-revision LED firmware.',
 scope='Circuit contract and procurement arithmetic; native CAD/copper verification and physical testing remain separate.')
(R/'reports/variant_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
