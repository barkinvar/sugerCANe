"""Create grouped, placement and DigiKey import BOMs from the reviewed circuit."""
from pathlib import Path
from collections import defaultdict
import csv,json,sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from bom.catalog import CATALOG
parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
groups=defaultdict(list)
for ref,c in parts.items():
    if not c.get('exclude_bom'):groups[c['mpn']].append(c)
groups['QPC02SXGN-RC']=[{'ref':'CONFIGURATION_SHUNTS','value':'2.54mm shorting shunt','footprint':'Accessory','kind':'SHUNT'}]*13
rows=[];per_ref=[]
for mpn,items in sorted(groups.items()):
    cat=CATALOG[mpn]
    assert cat['digikey_sku'] and cat['reported_stock'] is not None and cat['unit_price_usd_qty1'] is not None,mpn
    first=items[0];refs=' '.join(sorted({c['ref'] for c in items}));qty=len(items)
    assert len({(c['value'],c['footprint']) for c in items})==1,mpn
    row={'references':refs,'quantity':qty,'value':first['value'],'footprint':first['footprint'],
         'voltage':first.get('voltage',''),'rated_power_W':first.get('rated_power_W',''),'temperature_coefficient_ppm_C':first.get('temperature_coefficient_ppm_C',''),'tolerance':first.get('tolerance',''),'dielectric':first.get('dielectric',''),
         **cat,'extended_usd_at_qty1_price':round(qty*cat['unit_price_usd_qty1'],2),
         'recommended_order_quantity':qty+(max(2,math.ceil(qty*.2)) if first['kind'] in ['R','C','CP','LED','D','ZENER'] and first['ref'][0] in 'RCD' else 0)}
    rows.append(row)
    for c in items:
        if c['kind']!='SHUNT':per_ref.append({'reference':c['ref'],'value':c['value'],'mpn':mpn,'digikey_sku':cat['digikey_sku'],'footprint':c['footprint'],'notes':c.get('note','')})
def write_csv(name,entries):
    with (ROOT/'bom'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(entries[0]));w.writeheader();w.writerows(entries)
write_csv('BOM_grouped.csv',rows);write_csv('BOM_per_reference.csv',sorted(per_ref,key=lambda c:c['reference']))
write_csv('DigiKey_import_exact.csv',[{'DigiKey Part Number':r['digikey_sku'],'Quantity':r['quantity'],'Customer Reference':r['references']} for r in rows])
write_csv('DigiKey_import_with_spares.csv',[{'DigiKey Part Number':r['digikey_sku'],'Quantity':r['recommended_order_quantity'],'Customer Reference':r['references']} for r in rows])
total=round(sum(r['extended_usd_at_qty1_price'] for r in rows),2)
summary={'observation_date':'2026-09-07','board_components_to_purchase':len(per_ref),'shunts_to_purchase':13,
         'unique_purchase_lines':len(rows),'estimated_parts_total_usd_qty1_basis':total,
         'zero_stock_lines':[r['mpn'] for r in rows if not r['reported_stock']],
         'scope':'DigiKey catalog/search-index observations, not a live quote or reserved stock. Tax, freight, PCB, stencil, tools and mounting hardware excluded. Quantity discounts may reduce cost.',
         'spares_policy':'20% extra rounded up, at least2 extra, for resistors/capacitors/diodes/LEDs; no extra ICs/connectors/inductor/crystal/fuse.',
         'not_purchased':'10 copper test points are fabricated on the PCB, not separate components; 4 mounting holes are nonplated features.'}
(ROOT/'bom/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(ROOT/'bom/catalog_selected.json').write_text(json.dumps({r['mpn']:CATALOG[r['mpn']] for r in rows},indent=2)+'\n')
text=f'''# Revision A purchasing files

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

All {len(rows)} purchase lines have a DigiKey order code. The board uses {len(per_ref)} fitted components; buy 13 configuration shunts separately. Ten test pads and four mounting holes are PCB features.

Indicative one-board parts total: **US${total:.2f}**, calculated conservatively using catalog quantity-one prices for every unit. This excludes PCB fabrication, stencil, shipping, tax, tools and mounting hardware. It is not a live quote. Stock and price observations were collected 2026-09-07; some distributor pages are indexed snapshots and disagree across regions. Reconfirm the exact SKU in a cart before ordering.

A readable version is available at `output/documentation/BOM_RevA.pdf`; programming and mounting accessories are listed separately in `Accessories_DigiKey.csv` and `docs/ACCESSORIES.md`.

Use `DigiKey_import_exact.csv` for exact assembly quantities or `DigiKey_import_with_spares.csv` for extra small parts suitable for hand assembly. `BOM_grouped.csv` contains ratings, source links, availability notes and suggested alternatives. `BOM_per_reference.csv` maps every fitted reference to its part.

The TPS1H100A battery switch was rejected when the current US listing showed no stock; the board uses the stocked TPS1H200A with a different footprint and pin map. Do not fit the older part. The input reverse-polarity element is Q1 AO4485 with a 12 V gate clamp; the earlier series-diode approach was replaced to improve low-battery headroom.

Alternatives in the catalog are review candidates, not an automatic substitution list. Verify package, pinout, voltage, temperature coefficient, leakage, capacitance under DC bias, and firmware behavior as applicable. Keep the 0.1% feedback resistors, C0G timing/filter capacitors, 100V bias diodes, and 2010 pulldown power resistors.

The 13 shunts allow four power selections, four bias selections, four logic-threshold selections and one CAN terminator. Install only the shunts required for your sensors. JP1 is momentary reset and must remain open in normal use.
'''
(ROOT/'bom/README.md').write_text(text)
print(json.dumps(summary,indent=2))
