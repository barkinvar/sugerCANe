"""Exact-MPN turnkey BOM, with dated procurement observations and no hidden DNPs."""
from pathlib import Path
import collections
import csv
import json

R=Path(__file__).resolve().parents[1]
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
original=json.loads((R/'bom/catalog_selected.json').read_text())
subs=json.loads((R/'bom/substitutions.json').read_text())
# USD list observations on 2026-09-08 UTC. LCSC stock is NOT JLCPCB stock.
# Tuple: exact MPN, LCSC ID, observed stock, MOQ/multiple, price tiers.
observations=[
 ('0805W8F1001T5E','C17513',26345600,100,[(100,.0042),(1000,.0033),(5000,.0027)]),
 ('0805W8F1002T5E','C17414',47196100,100,[(100,.0039),(1000,.0031),(5000,.0023)]),
 ('0805W8F4701T5E','C17673',3907600,100,[(100,.0051),(1000,.0040),(5000,.0035)]),
 ('0805W8F1003T5E','C149504',3765700,100,[(100,.0060),(1000,.0047),(5000,.0041)]),
 ('CL21B104KCFNNNE','C28233',605350,50,[(50,.0411),(500,.0325),(2000,.0287)]),
 ('TCAN3413DR','C22433320',233,1,[(1,1.0227),(10,.8391),(30,.7473),(100,.6572)]),
 ('LMR51420XDDCR','C5246146',109,1,[(1,1.0292),(10,.8604),(30,.7752),(100,.6916)]),
 ('TPS613222ADBVR','C2071163',3545,5,[(5,.3697),(50,.2958),(150,.2642)]),
 ('TPS2553DBVR-1','C111738',12065,5,[(5,.2978),(50,.2361),(150,.2096)]),
 ('BAT46W-E3-18','C5557780',4735,5,[(5,.1307),(50,.1084),(150,.0973)]),
 ('CL31A226KAHNNNE','C12891',211520,20,[(20,.1709),(200,.1297),(600,.1096)]),
 ('AO4485','C51499',88125,5,[(5,.3171),(50,.2505),(150,.2220)]),
 ('SMAJ30A','C148230',30185,5,[(5,.1459),(50,.1169),(150,.1023)]),
]
new_by_mpn={v[0]:(k,v[1],v[2]) for k,v in subs.items()}
catalog={}
for mpn, info in original.items():
    if mpn in subs: continue
    catalog[mpn]={
        'mpn':mpn,'manufacturer':info['manufacturer'],'supplier':'DigiKey',
        'supplier_part':info['digikey_sku'],'url':info['digikey_url'],
        'stock_observed':info['reported_stock'],'observed_date':info['checked_date'],
        'moq':1,'multiple':1,
        'tiers':[(1,info['unit_price_usd_qty1']),(10,info['unit_price_usd_qty10'])],
        'lcsc':'','factory_stock_status':'Not checked; turnkey procurement required',
        'digikey_sku':info['digikey_sku'],'digikey_url':info['digikey_url'],
    }
for mpn,cid,stock,multiple,tiers in observations:
    if mpn not in catalog:
        old,man,_=new_by_mpn[mpn]
        catalog[mpn]={'mpn':mpn,'manufacturer':man,'digikey_sku':'','digikey_url':'',
                      'previous_mpn':old}
    catalog[mpn].update(supplier='LCSC',supplier_part=cid,
        url=f'https://www.lcsc.com/product-detail/{cid}.html',lcsc=cid,
        stock_observed=stock,observed_date='2026-09-08',moq=multiple,multiple=multiple,
        tiers=tiers,factory_stock_status='LCSC listing verified; JLCPCB allocation/classification unverified')
# Additional catalog IDs are identification aids only, not inventory promises.
for mpn,cid in [('STM32F042K6T6','C69216'),('LM339LVDR','C22427665'),('TPS1H200AQDGNRQ1','C2653785')]:
    catalog[mpn]['lcsc']=cid
catalog['STM32F042K6T6']['factory_stock_status']='LCSC C69216 OUT OF STOCK at observation; procure exact MCU from DigiKey/authorized source'

groups=collections.defaultdict(list)
for ref,c in parts.items():
    if not c.get('exclude_bom'):groups[c['mpn']].append(ref)
groups['M22-1900005']=['ACCESSORY']*10
rows=[]
for mpn,refs in sorted(groups.items()):
    source=catalog[mpn]
    c=parts.get(refs[0],{'value':'2 mm shunt','footprint':'Bagged accessory'})
    kind='ACCESSORY' if refs[0]=='ACCESSORY' else 'THT' if refs[0].startswith('J') else 'SMT'
    unit=source['tiers'][0][1]
    rows.append(dict(MPN=mpn,Manufacturer=source['manufacturer'],Quantity=len(refs),
        References=', '.join(refs) if kind!='ACCESSORY' else '10 loose configuration shunts',
        Value=c['value'],Footprint=c['footprint'],Assembly=kind,Side='TOP' if kind!='ACCESSORY' else 'BAG',
        Voltage=c.get('voltage',''),Tolerance=c.get('tolerance',''),Power_W=c.get('rated_power_W',''),
        Dielectric=c.get('dielectric',''),Component_notes=c.get('note',''),
        Preferred_supplier=source['supplier'],Supplier_part=source['supplier_part'],
        LCSC=source['lcsc'],DigiKey_SKU=source['digikey_sku'],DigiKey_URL=source['digikey_url'],
        Supplier_URL=source['url'],Observed_stock=source['stock_observed'],Checked_date=source['observed_date'],
        Supplier_MOQ=source['moq'],Supplier_multiple=source['multiple'],
        Unit_USD_first_tier=unit,Extended_USD_consumed=round(len(refs)*unit,4),
        Factory_stock_status=source['factory_stock_status']))

def write(path,rows,fields=None):
    with (R/path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
write('bom/BOM_grouped.csv',rows)
write('bom/BOM_turnkey.csv',rows)
refrows=[]
for ref,c in parts.items():
    if not c.get('exclude_bom'):
        refrows.append(dict(reference=ref,MPN=c['mpn'],value=c['value'],footprint=c['footprint'],
            voltage=c.get('voltage',''),tolerance=c.get('tolerance',''),note=c.get('note','')))
write('bom/BOM_per_reference.csv',refrows)
jlc=[{'Comment':q['MPN'],'Designator':q['References'],'Footprint':q['Footprint'].split(':')[-1],
      'LCSC Part #':q['LCSC']} for q in rows if q['Assembly']!='ACCESSORY']
write('bom/BOM_JLCPCB.csv',jlc)
write('bom/ACCESSORIES.csv',[q for q in rows if q['Assembly']=='ACCESSORY'])
(R/'bom/catalog_china.json').write_text(json.dumps(catalog,indent=2)+'\n')
base_total=sum(float(q['unit_price_usd_qty1'])*len(groups.get(mpn,[])) for mpn,q in original.items() if mpn not in subs)
base_total+=sum(original[k]['unit_price_usd_qty1']*len(groups[v[0]]) for k,v in subs.items())
consumed=round(sum(q['Extended_USD_consumed'] for q in rows),2)
summary=dict(revision='B-2',modeled_parts=len(parts),fitted_parts=len(refrows),purchase_lines=len(rows),
    smt_placements=sum(q['Quantity'] for q in rows if q['Assembly']=='SMT'),
    tht_placements=sum(q['Quantity'] for q in rows if q['Assembly']=='THT'),shunts=10,
    changed_mpn_placements=sum(len(groups[v[0]]) for v in subs.values()),
    component_consumed_first_tier_usd=consumed,base_rev_b_qty1_usd=round(base_total,2),
    note='Consumed component comparison only: supplier MOQ, attrition, sourcing, PCB, assembly, shipping and taxes are extra. Use cost_estimate.csv for order budgets. JLC parts import requires procurement/matching review.')
(R/'bom/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
