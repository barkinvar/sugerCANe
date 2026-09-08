"""Transparent order-budget model; never presented as a factory quotation."""
from pathlib import Path
import csv
import json
import math
R=Path(__file__).resolve().parents[1]
catalog=json.loads((R/'bom/catalog_china.json').read_text())
bom=list(csv.DictReader((R/'bom/BOM_grouped.csv').open()))
counts=json.loads((R/'reports/factory_counts.json').read_text())
def price(c,n):return [p for qty,p in c['tiers'] if qty<=n and p is not None][-1]
rows=[];proc=[]
for n in [1,2,5,10,25]:
    component_total=0;consumed=0
    for row in bom:
        c=catalog[row['MPN']];need=n*int(row['Quantity'])
        # Exact-purchase MOQ cost plus separate allowance below for attrition.
        buy=max(c['moq'],math.ceil(need/c['multiple'])*c['multiple'])
        unit=price(c,buy);amount=buy*unit;component_total+=amount;consumed+=need*unit
        proc.append(dict(boards=n,MPN=row['MPN'],supplier=c['supplier'],required=need,
            purchased_with_moq=buy,unused=buy-need,unit_usd=unit,line_usd=round(amount,4)))
    # Standard PCBA is budgeted: manual THT, external sourcing and controlled reflow.
    # Conservatively count all fitted types for feeder fees, including THT types.
    fixed=25.56+8.21+1.53*(counts['SMT_types']+counts['THT_types'])+16.42+3.58+.45
    # U3 exposed pad inspection modeled as one X-ray component per board.
    xray=1.64 if n<=10 else .82
    assembly=fixed+n*(counts['SMT_solder_joints']*.0016+
                        counts['THT_solder_joints']*.0164+xray+.50+.00003*40.8)
    # Engineering allowances: not published factory quotes. Include ENIG/rails,
    # component handling, supplier freight, loss quantities, and destination freight.
    pcb_low=20+max(0,n-5)*1.;pcb_high=40+max(0,n-5)*2.
    loss_low=max(5,.03*component_total);loss_high=max(15,.08*component_total)
    sourcing_low=10+.05*component_total;sourcing_high=30+.15*component_total
    ship_low=25 if n<=10 else 35;ship_high=50 if n<=10 else 70
    low=component_total+assembly+pcb_low+loss_low+sourcing_low+ship_low
    high=component_total+assembly+pcb_high+loss_high+sourcing_high+ship_high
    rows.append(dict(assembled_boards=n,JLCPCB_minimum_met=n>=2,
        components_including_moq_usd=round(component_total,2),consumed_components_usd=round(consumed,2),
        assembly_model_usd=round(assembly,2),pcb_allowance_low=pcb_low,pcb_allowance_high=pcb_high,
        attrition_allowance_low=round(loss_low,2),attrition_allowance_high=round(loss_high,2),
        sourcing_allowance_low=round(sourcing_low,2),sourcing_allowance_high=round(sourcing_high,2),
        shipping_allowance_low=ship_low,shipping_allowance_high=ship_high,
        order_estimate_low_usd=math.floor(low/5)*5,order_estimate_high_usd=math.ceil(high/5)*5,
        per_board_low_usd=round(low/n,2),per_board_high_usd=round(high/n,2),
        optional_program_basic_test_low_usd=50+3*n,optional_program_basic_test_high_usd=100+5*n))
def write(name,data):
    with (R/'bom'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
write('cost_estimate.csv',rows);write('procurement_quantities.csv',proc)
(R/'bom/cost_assumptions.json').write_text(json.dumps(dict(
    currency='USD',observed_date='2026-09-08',status='Engineering budget, no supplier quote/cart submitted',
    source='https://jlcpcb.com/help/article/pcb-assembly-price',
    minimum_source='https://jlcpcb.com/solutions/pcb-prototype-assembly',
    service='Standard PCBA, one side, mixed SMT/THT, factory-created rails/fiducials',
    input_prices='Dated LCSC observations for 13 MPNs; conservative original DigiKey prices for remaining exact parts. Original DigiKey qty10 rates used when purchase quantity reaches 10.',
    factory_inventory='LCSC stock and prices do not establish JLCPCB allocation or classification; matching and external procurement required.',
    shipping='Allowance for ordinary international small-parcel shipment; destination unspecified; no live freight quote',
    exclusions=['destination VAT/sales tax','import duties/tariffs','qualification testing','custom production jig','enclosure','programmer'],
    optional_testing='Separate allowance includes simple custom cable setup, SWD flash/verify and no-load rail checks. Not a quote or full functional/temperature/EMC test.',
    notes=['1-board row is hypothetical service-cost comparison only: below published JLCPCB minimum.','Minimum bare-board fabrication quantity assumed five, with unassembled spares.','No coupons or promotional discounts. Factory may quote additional fixture/pre-reflow charges.','Procurement MOQ excess and attrition allowance are both included; factory internal-stock consumption may cost less.']
),indent=2)+'\n')
table=['| Assembled boards | Estimated order total | Approx. per board |','|---:|---:|---:|']
for q in rows:
    if q['assembled_boards']==1:continue
    table.append(f"| {q['assembled_boards']} | ${q['order_estimate_low_usd']}–{q['order_estimate_high_usd']} | ${q['per_board_low_usd']:.0f}–{q['per_board_high_usd']:.0f} |")
text='''# Rev B-2 China assembly budget

These are USD engineering estimates dated 2026-09-08, not a submitted quotation. The PCB has not been physically qualified. Pricing assumes full SMT and through-hole assembly, ENIG, bagged shunts and ordinary international shipping; destination taxes and tariffs are excluded.

JLCPCB publishes a minimum of **two assembled boards**. If you only need one, the first realistic JLCPCB order still pays for two. The one-board row in the CSV is hypothetical and must not be treated as an available service. PCBWay's current capability page publishes a five-piece minimum.

'''+ '\n'.join(table)+'''

The component-only consumed comparison is **$46.35 per board versus Rev B's $59.30**, about 22% lower on the stated first-tier basis. This comparison does not include MOQ leftovers or assembly. It combines cheaper equivalents with cheaper procurement of identical parts; it is not a $46 finished-board price.

The order model uses dated per-line prices and MOQ rounding, then adds the published JLCPCB Standard setup/stencil/feeder and solder-joint rates. It conservatively budgets feeder fees for all 50 fitted part types. Other costs are explicit allowances: ENIG boards/panel rails, attrition, procurement handling/inbound freight, inspection and international shipping. The factory's actual sourcing quote may differ considerably. LCSC inventory is not JLCPCB assembly inventory.

Factory programming and simple no-load checks are optional and additional: budget **$50–100 setup plus $3–5 per board**, including an allowance for the custom SWD adapter. The archive supplies the firmware and wiring. Full sensor/CAN/load testing, a repeatable production fixture and qualification are separate work.

At prototype quantities, this is not yet a cost-competitive retail product. The 50 fitted part types, premium connectors and supplier setup costs dominate; reducing capacitors alone does little. A further cost revision should consolidate functional circuits and selectors after this prototype is measured.

See `bom/cost_estimate.csv` for every allowance and `bom/procurement_quantities.csv` for exact modeled purchase quantities, leftover parts and price breaks.

Sources: [JLCPCB assembly fees](https://jlcpcb.com/help/article/pcb-assembly-price), [JLCPCB prototype minimum](https://jlcpcb.com/solutions/pcb-prototype-assembly), [PCBWay minimum](https://www.pcbway.com/assembly-capabilities.html). Component source URLs and observation dates are in the BOM.
'''
(R/'docs/COST.md').write_text(text)
print('\n'.join(table))
