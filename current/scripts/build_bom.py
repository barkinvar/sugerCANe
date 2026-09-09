"""Generate complete and SMT-only files; supplier observations are not a quote."""
from pathlib import Path
import collections,csv,json
R=Path(__file__).resolve().parents[1]
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
catalog=json.loads((R/'bom/catalog_china.json').read_text())
groups=collections.defaultdict(list)
for ref,c in parts.items():
 if not c.get('exclude_bom'):groups[c['mpn']].append(ref)
def write(name,rows):
 with (R/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for mpn,refs in sorted(groups.items()):
 c,s=parts[refs[0]],catalog[mpn];manual=all(ref.startswith('J') for ref in refs);price=s['tiers'][0][1]
 rows.append(dict(MPN=mpn,Manufacturer=s['manufacturer'],Quantity=len(refs),References=', '.join(refs),Value=c['value'],Footprint=c['footprint'],Voltage=c.get('voltage',''),Tolerance=c.get('tolerance',''),Power_W=c.get('rated_power_W',''),Dielectric=c.get('dielectric',''),Assembly='Hand solder' if manual else 'Factory SMT',Supplier=s['supplier'],Supplier_part=s['supplier_part'],LCSC_part=s.get('lcsc',''),MOQ=s['moq'],Multiple=s['multiple'],Unit_USD_first_tier=price,Extended_USD_first_tier=round(len(refs)*price,6),Observed_stock=s['stock_observed'],Checked_date=s['observed_date'],Supplier_URL=s['url'],DigiKey_SKU=s.get('digikey_sku',''),Factory_stock_status=s['factory_stock_status'],Component_notes=c.get('note','')))
write('bom/BOM_grouped.csv',rows)
manual=[r for r in rows if r['Assembly']=='Hand solder'];s=catalog['SPN02SVEN-RC']
write('bom/ACCESSORIES.csv',[dict(MPN=s['mpn'],Manufacturer=s['manufacturer'],Quantity=3,References='Three loose voltage-selection caps',Value='Closed-top 2 mm shunt',Supplier=s['supplier'],Supplier_part=s['supplier_part'],Supplier_URL=s['url'],Unit_USD_first_tier=s['tiers'][0][1])])
write('bom/Hand_solder_BOM.csv',manual)
factory=[dict(Comment=r['Value'],Designator=r['References'],Footprint=r['Footprint'],Quantity=r['Quantity'],Manufacturer=r['Manufacturer'],MPN=r['MPN'],LCSC_Part=r['LCSC_part'],Supplier_URL=r['Supplier_URL']) for r in rows if r['Assembly']=='Factory SMT']
write('bom/Factory_BOM.csv',factory)
write('bom/BOM_JLCPCB.csv',[dict(Comment=r['MPN'],Designator=r['Designator'],Footprint=r['Footprint'],**{'LCSC Part #':r['LCSC_Part']}) for r in factory])
write('bom/BOM_per_reference.csv',[dict(reference=ref,MPN=c['mpn'],value=c['value'],footprint=c['footprint'],voltage=c.get('voltage',''),tolerance=c.get('tolerance',''),rated_power_W=c.get('rated_power_W',''),dielectric=c.get('dielectric',''),note=c.get('note','')) for ref,c in sorted(parts.items()) if not c.get('exclude_bom')])
write('bom/DigiKey_hand_solder_import.csv',[dict(Part=r['DigiKey_SKU'],Quantity=r['Quantity'],Reference=r['References']) for r in manual]+[dict(Part=s['digikey_sku'],Quantity=3,Reference='Loose closed-top voltage caps')])
fitted=sum(r['Quantity'] for r in rows)
summary=dict(revision='G output eFuse / CAN reset / rail ADC',modeled_parts=len(parts),fitted_parts=fitted,factory_smt_parts=sum(r['Quantity'] for r in rows if r['Assembly']=='Factory SMT'),hand_solder_parts=sum(r['Quantity'] for r in manual),purchase_lines=len(rows)+1,factory_smt_types=len(factory),shunts=3,component_consumed_first_tier_usd=round(sum(r['Extended_USD_first_tier'] for r in rows)+3*s['tiers'][0][1],2),note='Consumed parts at first supplier tier, including hand-fit parts and three loose shunts; not quantity-one purchasing cash or a PCBA quote. See cost_estimate.csv for MOQ and batch pricing.')
assert fitted==135 and summary['factory_smt_parts']==126 and summary['hand_solder_parts']==9
(R/'bom/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
