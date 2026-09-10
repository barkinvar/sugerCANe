"""Audit the dated public JLC snapshot; availability is not reserved inventory."""
from pathlib import Path
import csv, hashlib, json, re
import sexpdata

R=Path(__file__).resolve().parents[1]
snapshot=json.loads((R/'bom/jlc_sourcing.json').read_text())
model=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
factory=list(csv.DictReader((R/'bom/Factory_BOM.csv').open()))
jlc=list(csv.DictReader((R/'bom/BOM_JLCPCB.csv').open()))
cpl=list(csv.DictReader((R/'output/assembly/CPL_JLCPCB.csv').open()))
catalog=json.loads((R/'bom/catalog_china.json').read_text())
rows=snapshot['parts'];by_mpn={r['mpn']:r for r in rows}
def normalized(value):return re.sub(r'[^A-Z0-9]','',value.upper())
manufacturer_aliases={normalized(k):normalized(v) for k,v in {
 'Abracon LLC':'Abracon','Alpha & Omega Semicon':'Alpha & Omega Semiconductor',
 'UNI-ROYAL(Uniroyal Elec)':'UNI-ROYAL','Vishay Intertech':'Vishay'}.items()}
def manufacturer(value):return manufacturer_aliases.get(normalized(value),normalized(value))
assert len(rows)==len(by_mpn)==len(factory)==len(jlc)==55
assert {r['MPN'] for r in factory}==set(by_mpn)
assert all(r['LCSC Part #'] for r in jlc)
refs=set();shortages=[];cash=0
for f,j in zip(factory,jlc):
 r=by_mpn[f['MPN']];s=catalog[f['MPN']]
 assert r['lcsc']==f['LCSC_Part']==j['LCSC Part #']==s['lcsc']
 assert normalized(r['catalog_mpn'])==normalized(f['MPN'])
 assert manufacturer(r['manufacturer'])==manufacturer(f['Manufacturer'])==manufacturer(s['manufacturer'])
 assert r['catalog_status']=='yes'
 assert r['pcba_services']=={0:['Economic','Standard'],2:['Standard']}[r['catalog_product_type']]
 assert f['MPN']==j['Comment'] and f['Designator']==j['Designator']
 assert set(f['Designator'].split(', '))==set(r['references'])
 assert int(f['Quantity'])==r['quantity_per_board']==len(r['references'])
 assert r['assembly_mode']=='smtWeld' and r['allocation_confirmed'] is False
 for ref in r['references']:
  assert ref not in refs and model[ref]['mpn']==r['mpn']
  assert model[ref]['footprint']==f['Footprint']
  refs.add(ref)
 need=snapshot['batch_boards']*r['quantity_per_board']
 budget=max(need+r['attrition_allowance'],r['minimum_assembly'],r['minimum_purchase'])
 assert budget==r['ten_board_budget_quantity']
 sufficient=r['available_to_order']>=budget
 assert sufficient==r['ten_board_stock_sufficient']
 if not sufficient:shortages.append(dict(mpn=r['mpn'],lcsc=r['lcsc'],references=r['references'],required=budget,available=r['available_to_order'],source_url=r['source_url']))
 price=max((t for t in r['price_tiers_usd'] if t[0]<=budget),key=lambda t:t[0])[1]
 cash+=budget*price
assert len(refs)==130
assert len(cpl)==len({r['Designator'] for r in cpl})==130
assert {r['Designator'] for r in cpl}==refs and all(r['Layer']=='Top' for r in cpl)
manual=set(snapshot['hand_solder']['references'])
assert len(manual)==10 and not refs&manual
assert refs|manual=={r for r,c in model.items() if not c.get('exclude_bom')}
for s in snapshot['substitutions']:
 for ref in s['references']:
  assert model[ref]['mpn']==s['new_mpn'] and model[ref]['value']==s['value']
  assert model[ref]['footprint']==s['footprint']
for d in snapshot['datasheets']:
 assert hashlib.sha256((R/d['file']).read_bytes()).hexdigest()==d['sha256']
# Electrical model changes are still limited to the reviewed MPN strings.
for path,key in [('hardware/design/circuit.json','baseline_model_sha256')]:
 restored=(R/path).read_text()
 for s in snapshot['substitutions']:restored=restored.replace(s['new_mpn'],s['old_mpn'])
 assert hashlib.sha256(restored.encode()).hexdigest()==snapshot[key],('Change beyond sourcing metadata',path)
# Subsequent user-authorized routing edits have their own exact board review.
# The exact nonrouting hash pins footprints, retained vias, stack and zone rules.
# The routing review records the earlier redundant via removals and the later
# ground-zone settings/cutouts and J8.7 spoke angle. Exact native comparisons
# preserve every object outside these explicitly reviewed changes.
route_review=snapshot['routing_review']
board_path=R/'hardware/FRC_Sensor_CAN.kicad_pcb'
assert hashlib.sha256(board_path.read_bytes()).hexdigest()==route_review['board_sha256']
for via in route_review.get('removed_redundant_vias', []):
 assert via['id'] not in board_path.read_text()
native=sexpdata.loads(board_path.read_text())
review=snapshot['equivalence_review']
assert review['board_sha256']==route_review['board_sha256']
assert len(review['substitutions'])==len(snapshot['substitutions'])==6
def children(rows,name):
 return [v for v in rows if isinstance(v,list) and str(v[0])==name]
footprints={next(v[2] for v in children(f,'property') if v[1]=='Reference'):f for f in children(native,'footprint')}
for approved,checked in zip(snapshot['substitutions'],review['substitutions']):
 for key in ('references','old_mpn','new_mpn','footprint'):assert checked[key]==approved[key]
 assert checked['two_terminal_nonpolar']
 assert set(checked['sources']) <= {d['file'] for d in snapshot['datasheets']}
 for ref in checked['references']:
  pads=children(footprints[ref],'pad');assert {p[1] for p in pads}=={'1','2'} and len(pads)==2
  for pad,x in zip(sorted(pads,key=lambda p:p[1]),checked['nominal_pad_centers_x_mm']):
   assert children(pad,'size')[0][1:]==checked['nominal_pad_size_mm'],ref
   assert children(pad,'at')[0][1:3]==[x,0],ref
fixed=[]
for row in native:
 if isinstance(row,list):
  if str(row[0]) in ('segment','arc'):continue
  if str(row[0])=='zone':row=[v for v in row if not isinstance(v,list) or str(v[0]) not in ('filled_polygon','fill_segments')]
 fixed.append(row)
assert hashlib.sha256(sexpdata.dumps(fixed).encode()).hexdigest()==route_review['nonrouting_objects_sha256']
basic=sum(r['library_class']=='base' for r in rows)
preferred=sum(r['library_class']=='expand' and r['preferred_extended'] for r in rows)
fees=len(rows)-basic-preferred
assembly=snapshot['assembly_review'];service=assembly['selected_service']
ineligible=[dict(mpn=r['mpn'],references=r['references'],source_url=r['source_url']) for r in rows if service not in r['pcba_services']]
economic_blockers=[dict(mpn=r['mpn'],references=r['references'],source_url=r['source_url']) for r in rows if 'Economic' not in r['pcba_services']]
thermal_conflicts=[]
for constraint in assembly['reflow_constraints']:
 assert model[constraint['reference']]['mpn']==constraint['mpn']
 if constraint['peak_C']<assembly['standard_nominal_peak_C']+assembly['standard_peak_tolerance_C']:
  thermal_conflicts.append(constraint)
if assembly['factory_profile_confirmed']:
 evidence=assembly['factory_profile_evidence']
 assert evidence and hashlib.sha256((R/evidence['file']).read_bytes()).hexdigest()==evidence['sha256']
holds=[]
if shortages:holds.append('Insufficient orderable public stock: '+', '.join(r['mpn'] for r in shortages)+'; procurement unconfirmed')
if ineligible:holds.append('Selected assembly service excludes BOM parts')
if thermal_conflicts and not assembly['factory_profile_confirmed']:holds.append('C1 profile (2) permits 235 C peak; nominal Standard process can reach 245 C')
if not assembly['all_component_reflow_profiles_qualified']:holds.append('Factory qualification of all exact-part solder profiles and moisture handling is pending')
hand=float(next(r for r in csv.DictReader((R/'bom/cost_estimate.csv').open()) if r['boards']=='10')['hand_parts_cash_per_board_usd'])
report=dict(result='PASS sourcing-file consistency; HOLD manufacturing review' if holds else 'PASS sourcing-file consistency; allocation unconfirmed',
 observed_utc=snapshot['observed_utc'],stock_observation_window_utc=snapshot['stock_observation_window_utc'],availability_definition=snapshot['availability_definition'],boards=10,factory_placements=130,matched_mpn_types=len(rows),stock_sufficient_types=len(rows)-len(shortages),
 shortage_types=shortages,basic_types=basic,preferred_extended_types=preferred,ordinary_extended_types=fees,
 smt_parts_with_conservative_attrition_per_board_usd=round(cash/10,2),manual_parts_per_board_usd=hand,
 combined_parts_budget_per_board_usd=round(cash/10+hand,2),
 selected_service=service,economic_eligible=not economic_blockers,economic_blockers=economic_blockers,
 standard_setup_stencil_loading_two_fixtures_per_order_usd=round(25.56+8.21+1.53*len(rows)+16.42,2),
 moisture_sensitive_parts=[dict(references=r['references'],msl=r['moisture_sensitivity_level']) for r in rows if r['moisture_sensitivity_level'] not in ('Not stated','MSL 1')],
 nominal_standard_reflow_conflicts=thermal_conflicts,manufacturing_holds=holds,
 quantity_method=snapshot['quantity_method'],factory_allocation_confirmed=False,
 electrical_model_only_reviewed_mpn_metadata_changed=True,reviewed_routing=route_review,
 substitution_review=review,alternative_stock_review=snapshot['alternative_stock_review'],hand_solder_availability=snapshot['hand_solder'],
 order_decision='HOLD: user approval and new simulations pending; MCU sourcing, C1 reflow and factory stack/quote unconfirmed',
 limitations='Catalog snapshots and displayed price tiers are not a cart, guaranteed stock, complete assembled cost, qualified reflow profile or lead-time commitment.',
 input_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['bom/jlc_sourcing.json','bom/catalog_china.json','bom/Factory_BOM.csv','bom/BOM_JLCPCB.csv','output/assembly/CPL_JLCPCB.csv','hardware/design/circuit.json','hardware/FRC_Sensor_CAN.kicad_pcb','scripts/check_jlc_sourcing.py',*[d['file'] for d in snapshot['datasheets']]]})
(R/'reports/manufacturing/jlc_sourcing.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
