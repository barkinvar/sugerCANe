from pathlib import Path
import json,csv,collections
R=Path(__file__).resolve().parents[1];parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
base=json.loads((R/'bom/catalog_rev_a_observations.json').read_text())
# Dated distributor observations, not reserved inventory or landed-price quotes.
new=[
('LM339LVDR','Texas Instruments','296-LM339LVDRCT-ND','https://www.digikey.com/en/products/detail/texas-instruments/LM339LVDR/21598795',1085,.42,.293,'1.65-5.5 V supply, rail-to-rail failsafe inputs. Supplied from 3V3; not interchangeable with battery-supplied Rev A without changing supply.'),
('1824420000','Weidmuller','281-2020-ND','https://www.digikey.com/en/products/detail/weidm%C3%BCller/1824420000/1094358',12805,1.54,1.113,'Horizontal /90 entry; 3.5 mm pins, 7 mm row spacing. US listing checked 2026-09-08.'),
('1824430000','Weidmuller','281-2021-ND','https://www.digikey.com/en/products/detail/weidm%C3%BCller/1824430000/1094359',1698,2.21,1.591,'Horizontal /90 entry; 3.5 mm pins, 7 mm row spacing. US listing checked 2026-09-08.'),
('EEE-FK1H470P','Panasonic','PCE3815CT-ND','https://www.digikey.com/en/products/detail/panasonic-industry/EEE-FK1H470P/765984',10108,.93,.589,'50 V, 47 uF, 8 mm diameter, 6.5 mm maximum seated height.'),
('SMBJ22A-E3/52','Vishay','SMBJ22A-E3/52GICT-ND','https://www.digikey.com/en/products/detail/vishay-general-semiconductor-diodes-division/SMBJ22A-E3-52/1119260',705,.56,.348,'22 V standoff; not a continuous overvoltage regulator.'),
('TPS613222ADBVR','Texas Instruments','296-50503-1-ND','https://www.digikey.com/en/products/detail/texas-instruments/TPS613222ADBVR/8638376',15432,.55,.388,'Fixed 5 V boost in SOT-23-5; switch current is not output current.'),
('SRP4020TA-4R7M','Bourns','SRP4020TA-4R7MCT-ND','https://www.digikey.com/en/products/detail/bourns-inc/SRP4020TA-4R7M/4901006',9132,1.07,.88,'4.7 uH, 2.6 A RMS, 3.5 A saturation. Exact custom land pattern.'),
('SS14-E3/61T','Vishay','SS14-E3/61TGICT-ND','https://www.digikey.com/en/products/detail/vishay-general-semiconductor-diodes-division/SS14-E3-61T/1091538',99297,.47,.286,'External boost rectifier, SMA, 1 A/40 V.'),
('M22-2010205','Harwin','952-2273-ND','https://www.digikey.com/en/products/detail/harwin-inc/M22-2010205/3728237',7644,.16,.134,'2 mm pitch, 1 A contact.'),
('M22-2010305','Harwin','952-2274-ND','https://www.digikey.com/en/products/detail/harwin-inc/M22-2010305/3728238',35632,.22,.188,'2 mm pitch, 1 A contact.'),
('M22-2020305','Harwin','952-2133-ND','https://www.digikey.com/en/products/detail/harwin-inc/M22-2020305/3728097',838,.41,.35,'2 x 3, 2 mm pitch in both directions.'),
('M22-1900005','Harwin','952-1305-ND','https://www.digikey.com/en/products/detail/harwin-inc/M22-1900005/2264286',31908,.35,.293,'2 mm shunt; ten supplied allow all modes plus optional termination.')]
for m,man,sku,url,stock,p1,p10,note in new:
 base[m]=dict(mpn=m,manufacturer=man,digikey_sku=sku,digikey_url=url,reported_stock=stock,unit_price_usd_qty1=p1,unit_price_usd_qty10=p10,checked_date='2026-09-08',availability_note=note,evidence_kind='Dated DigiKey webpage observation; recheck before order')
groups=collections.defaultdict(list)
for r,c in parts.items():
 if not c.get('exclude_bom'):groups[c['mpn']].append(r)
groups['M22-1900005']=['SHUNT']*10
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
summary=dict(revision='B',modeled_parts=len(parts),fitted_parts=sum(not p.get('exclude_bom',False) for p in parts.values()),purchase_lines=len(rows),shunts=10,component_estimate_usd_qty1=round(sum(r['Extended_USD_qty1'] for r in rows),2),note='Conservative quantity-one basis, excludes PCB, shipping, tax, programming cable and tools. Some inherited observations dated 2026-09-07. Recheck exact stock before ordering.')
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

with (out/'BOM_per_reference.csv').open('w') as f:
 fields=['reference','MPN','value','footprint','voltage','tolerance','rated_power_W','dielectric','note']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for ref,c in sorted(parts.items()):
  if not c.get('exclude_bom'):w.writerow({**{k:c.get(k,'') for k in fields},'reference':ref,'MPN':c['mpn']})
