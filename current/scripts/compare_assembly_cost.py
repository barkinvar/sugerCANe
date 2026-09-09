"""Assembly fee sensitivity, not a delivered quote. Unknown charges stay excluded."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1]
parts={int(r['boards']):float(r['all_parts_cash_per_board_usd']) for r in csv.DictReader((R/'bom/cost_estimate.csv').open())}
groups=list(csv.DictReader((R/'bom/BOM_grouped.csv').open()))
mpns=len({g['MPN'] for g in groups if g['Assembly']=='Factory SMT'})
rows=[]
for n in (5,10,25):
 for service,extended in [('Standard',mpns)]+[('Economic',e) for e in (10,20,30,mpns)]:
  fixed=25.56+8.21+1.53*mpns+16.42 if service=='Standard' else 8.18+1.53+3.07*extended
  rows.append(dict(boards=n,service=service,charged_feeder_types=extended,parts_per_board=parts[n],setup_stencil_feeders_fixture_per_order=round(fixed,2),partial_per_board=round(parts[n]+fixed/n,2)))
with (R/'bom/assembly_scenarios.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
report=dict(date='2026-09-09',source='https://jlcpcb.com/help/article/pcb-assembly-price',smt_mpn_types=mpns,economic_cheaper_in_this_limited_comparison_when_charged_extended_types_at_most=int((25.56+8.21+1.53*mpns+16.42-8.18-1.53)/3.07),unknowns=['Exact part allocation and Economic eligibility','PCB','Placement and minimum adjustments','X-ray','Attrition','Handling/packing','Programming/test','Freight','Tax/duty'],scenarios=rows)
(R/'reports/manufacturing/cost_scenarios.json').write_text(json.dumps(report,indent=2)+'\n')
print('Wrote partial-cost scenarios; no factory quote or delivery total claimed.')
