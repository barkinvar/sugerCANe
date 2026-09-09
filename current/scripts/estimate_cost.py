"""Reproducible batch parts budget. No live cart or factory quotation."""
from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parents[1]
catalog=json.loads((R/'bom/catalog_china.json').read_text())
groups=list(csv.DictReader((R/'bom/BOM_grouped.csv').open()))
groups.append(dict(MPN='SPN02SVEN-RC',Quantity=3,Assembly='Hand solder'))
def price(c,q):return max((t for t in c['tiers'] if int(t[0])<=q),key=lambda t:int(t[0]))[1]
detail=[];summary=[]
for n in (1,5,10,25):
 cash={'Factory SMT':0.,'Hand solder':0.};consumed=0
 for g in groups:
  c=catalog[g['MPN']];need=n*int(g['Quantity']);minimum=math.ceil(max(need,c['moq'])/c['multiple'])*c['multiple'];candidates=[minimum]+[math.ceil(t[0]/c['multiple'])*c['multiple'] for t in c['tiers'] if t[0]>=minimum];buy=min(candidates,key=lambda q:q*price(c,q));p=price(c,buy)
  cash[g['Assembly']]+=buy*p;consumed+=need*p
  detail.append(dict(boards=n,MPN=g['MPN'],assembly=g['Assembly'],needed=need,purchase_quantity=buy,unit_usd=p,purchase_usd=round(buy*p,4),leftover=buy-need,supplier=c['supplier'],source=c['url']))
 summary.append(dict(boards=n,parts_consumed_per_board_usd=round(consumed/n,2),SMT_procurement_cash_per_board_usd=round(cash['Factory SMT']/n,2),hand_parts_cash_per_board_usd=round(cash['Hand solder']/n,2),all_parts_cash_per_board_usd=round(sum(cash.values())/n,2),all_parts_batch_cash_usd=round(sum(cash.values()),2)))
for name,rows in [('cost_estimate.csv',summary),('cost_detail.csv',detail)]:
 with (R/'bom'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(summary,indent=2))
