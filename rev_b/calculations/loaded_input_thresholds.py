"""Correlated ground-return loading plus electrical corners at the input terminals.
This uses a DC numerical sheet model, not a hardware guarantee.
"""
from pathlib import Path
import json,itertools
import numpy as np
R=Path(__file__).resolve().parents[1]
g=json.loads((R/'reports/electrical/ground_return_model.json').read_text())
t=g['results'][-1]['transfer_ohm_to_sample_relative_J1_ground']
# Inflate ground-transfer potentials to allow numerical mesh sensitivity.
GROUND_SCALE=1.15
keys=next(iter(t.values())).keys();cases=[]
for vin,i5,ibat,p5,pbat in itertools.product([5,12,22],[0,.31],[0,.32],['J4.2','J5.2','J6.2'],['J4.2','J5.2','J6.2']):
 ilogic=.15;boost_out=i5+ilogic;boost_in=5.15*boost_out/(4.0*.80);iin=1.
 for _ in range(100):iin=ibat+5.15*boost_out/((vin-.276*iin)*.80*.80)
 buck_in=iin-ibat
 currents={k:0. for k in t};currents[p5]+=i5;currents[pbat]+=ibat
 currents['U2.2']+=ilogic;currents['U8.2']+=boost_in-boost_out;currents['U1.1']+=buck_in-boost_in
 potentials={k:GROUND_SCALE*sum(currents[port]*t[port][k] for port in t) for k in keys}
 cases.append({'vin':vin,'i5':i5,'ibat':ibat,'port5':p5,'portbat':pbat,'ground_V':potentials,'sum_ground_current_A':sum(currents.values()),'input_current_A':iin})
 assert abs(sum(currents.values())-iin)<1e-10
signs=np.array(list(itertools.product([-1,1],repeat=7)))
rs,rg,rf,rp,rt,rb,rm=(np.array([220e3,20e3,910e3,10e3,100e3,17.8e3,7.15e3])*(1+.0175*signs)).T
results=[]
for mode in ['logic','industrial']:
 for ch in [1,2,3]:
  low=float('inf');high=-float('inf');min_rise=float('inf');max_fall=-float('inf')
  for c in cases:
   v=c['ground_V'];vrg=v[f'R{ch}07.2'];vsg=v[f'R{ch}03.2'];vmg=v[f'JP{ch}02.2'];vport=v[f'J{ch+3}.2'];vg=v['U7.12']
   for supply,off,ibp,ibm in itertools.product([3.3*.97,3.3*1.03],[-.0055,.0055],[-50e-9,50e-9],[-50e-9,50e-9]):
    vs=supply+v['U2.2'];gm=1/rm if mode=='logic' else 0
    vn=(vs/rt+vrg/rb+vmg*gm-ibm)/(1/rt+1/rb+gm)+off
    for vol in [0,.55]:
     rise=vn*(1+rs/rg+rs/rf)-vsg*rs/rg-(vg+vol)*rs/rf+ibp*rs-vport
     min_rise=min(min_rise,float(rise.min()));high=max(high,float(rise.max()))
    for leak in [0,100e-9]:
     voh=(vs/rp+vn/rf-leak)/(1/rp+1/rf)
     fall=vn*(1+rs/rg+rs/rf)-vsg*rs/rg-voh*rs/rf+ibp*rs-vport
     low=min(low,float(fall.min()));max_fall=max(max_fall,float(fall.max()))
  target_low,target_high=(.8,2.4) if mode=='logic' else (4,7)
  results.append({'mode':mode,'channel':ch,'rising_V':[min_rise,high],'falling_V':[low,max_fall],'pass':low>target_low and high<target_high})
report={'result':'PASS' if all(q['pass'] for q in results) else 'FAIL','load_cases':len(cases),'ground_potential_inflation_factor':GROUND_SCALE,'results':results,'assumptions':'DC ground transfer from final Gerbers at 85 C, worst 150 mA logic load at U2 ground; 80% per-stage efficiency, 4 V intermediate and 5.15 V output for current balance. Both sensor rail load extremes at each port, 5/12/22 V input. Exact transfer correlation retained and inflated 15%. Same electrical component allowances as calculations.json. Input thresholds referenced to the corresponding board sensor ground terminal; external cable drop and AC ground bounce excluded.'}
(R/'reports/electrical/loaded_input_thresholds.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['result']=='PASS'
