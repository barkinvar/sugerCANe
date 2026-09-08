from pathlib import Path
import json,csv,collections
R=Path(__file__).resolve().parents[1];parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
base=json.loads((R/'bom/catalog_inherited_observations.json').read_text())
new=[('RT0805BRD07102KL', 'YAG4817CT-ND', '1075541', 2938, 0.1, 0.08, 'DigiKey product and current substitute listing checked; multiple manufacturer equivalents available; price is dated observation, not a live quotation.'), ('RT0805BRD0713K7L', 'YAG4829CT-ND', '1075594', 4402, 0.1, 0.08, '0.1%, 25 ppm/C; keep precision grade for 5 V accuracy.'), ('RC0805FR-07220KL', '311-220KCRCT-ND', '727742', 74744, 0.11, 0.036, '220k, 1%, 100ppm/C; single series input resistor.'), ('RC0805FR-072M2L', '311-2.20MCRCT-ND', '727677', 35399, 0.1, 0.034, '2.2M, 1%, 100ppm/C feedback resistor.'), ('RC0805FR-075K23L', '311-5.23KCRCT-ND', '727993', 8358, 0.1, 0.034, '5.23k, 1%, 100ppm/C shared threshold reference.'), ('RC1206FR-0710KL', '311-10.0KFRCT-ND', '728483', 2088085, 0.11, 0.05, '10k, 1206, 0.25W input pulldown; do not replace by 0805 without power review.')]
for mpn,sku,pid,stock,p1,p10,note in new:
 base[mpn]=dict(mpn=mpn,manufacturer='YAGEO',digikey_sku=sku,digikey_url=f'https://www.digikey.com/en/products/detail/yageo/{mpn}/{pid}',reported_stock=stock,unit_price_usd_qty1=p1,unit_price_usd_qty10=p10,checked_date='2026-09-08',availability_note=note,evidence_kind='Dated DigiKey web/index observation; recheck before ordering')
base.update(json.loads((R/'bom/catalog_rev_d_observations.json').read_text()))
groups=collections.defaultdict(list)
for r,c in parts.items():
 if not c.get('exclude_bom'):groups[c['mpn']].append(r)
rows=[]
for mpn,rr in sorted(groups.items()):
 cat=base[mpn];c=parts.get(rr[0],{'value':'2 mm shunt','footprint':'Off-board assembly accessory'})
 rows.append(dict(MPN=mpn,Manufacturer=cat['manufacturer'],DigiKey_SKU=cat['digikey_sku'],Quantity=len(rr),References=', '.join(rr) if mpn!='M22-1900005' else '10 configuration shunts',Value=c['value'],Footprint=c['footprint'],Voltage=c.get('voltage',''),Tolerance=c.get('tolerance',''),Power_W=c.get('rated_power_W',''),Dielectric=c.get('dielectric',''),Component_notes=c.get('note',''),Unit_USD_qty1=cat['unit_price_usd_qty1'],Extended_USD_qty1=round(len(rr)*cat['unit_price_usd_qty1'],4),Observed_stock=cat['reported_stock'],Checked_date=cat['checked_date'],DigiKey_URL=cat['digikey_url'],Notes=cat.get('availability_note','')))
out=R/'bom';out.mkdir(exist_ok=True)
with (out/'BOM_grouped.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (out/'DigiKey_import.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['DigiKey Part Number','Quantity','Customer Reference']);w.writerows((r['DigiKey_SKU'],r['Quantity'],r['References']) for r in rows)
(out/'catalog_selected.json').write_text(json.dumps({m:base[m] for m in groups},indent=2)+'\n')
summary=dict(revision='D Regulated 12 V',modeled_parts=len(parts),fitted_parts=sum(not p.get('exclude_bom',False) for p in parts.values()),purchase_lines=len(rows),shunts=0,component_estimate_usd_qty1=round(sum(r['Extended_USD_qty1'] for r in rows),2),note='Conservative quantity-one basis, excludes PCB, shipping, tax, programming cable and tools. Some inherited observations dated 2026-09-07. Recheck exact stock before ordering.')
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

with (out/'BOM_per_reference.csv').open('w') as f:
 fields=['reference','MPN','value','footprint','voltage','tolerance','rated_power_W','dielectric','note']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for ref,c in sorted(parts.items()):
  if not c.get('exclude_bom'):w.writerow({**{k:c.get(k,'') for k in fields},'reference':ref,'MPN':c['mpn']})

# Factory-friendly exact-MPN BOM; no speculative LCSC substitutions.
with (out/'Factory_BOM.csv').open('w') as f:
 fields=['Comment','Designator','Footprint','Quantity','Manufacturer','MPN','DigiKey_SKU']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for row in rows:w.writerow({'Comment':row['Value'],'Designator':row['References'],'Footprint':row['Footprint'],'Quantity':row['Quantity'],'Manufacturer':row['Manufacturer'],'MPN':row['MPN'],'DigiKey_SKU':row['DigiKey_SKU']})
