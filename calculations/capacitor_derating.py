"""Use manufacturer characteristic samples, explicitly separating typical data
from engineering budgets. This is not a guaranteed capacitance measurement.
"""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'sources/datasheets/samsung_CL31A226_characteristics.json').read_text())
curve=next(g for g in data if g['graphType']=='DCBias')['selectPartsList'][0]['chartList'][0]['data']
x=np.array([float(p['x']) for p in curve]);y=np.array([float(p['y']) for p in curve])
vmax=json.loads((ROOT/'reports/electrical/calculations.json').read_text())['buck']['dc_reference_and_divider_only_V'][1]
bias_percent=float(np.interp(vmax,x,y));typical_one=22*(1+bias_percent/100)
budgets={'initial_tolerance_factor':.9,'temperature_factor':.85,'aging_allowance_factor':.95,'extra_curve_uncertainty_factor':.9}
factor=float(np.prod(list(budgets.values())))
effective=3*typical_one*factor
assert effective>25
result={'part':'CL31A226KAHNNNE','source_url':'https://product.samsungsem.com/cn/mlcc/CL31A226KAHNNN.do',
 'source_description':'Manufacturer embedded datasheetData, DCBias graph,25C,120Hz,0.5Vrms test amplitude; typical characterization, not a guaranteed minimum.',
 'raw_curve_file':'sources/datasheets/samsung_CL31A226_characteristics.json',
 'dc_voltage_V':vmax,'typical_capacitance_change_percent':bias_percent,'typical_one_cap_uF':typical_one,
 'capacitor_count':3,'nominal_bank_uF':66,'additional_budgets':budgets,'budgeted_bank_uF':effective,
 'previous_two_cap_bank_uF':2*typical_one*factor,
 'design_target_uF':25,
 'estimated_capacitive_ripple_V_at_1A_450kHz':1/(8*450e3*effective*1e-6),
 'estimated_300mA_load_step_excursion_V_TI_eight_cycle_model':4*.3/(450e3*effective*1e-6),
 'limitations':'DC-bias and temperature behavior need not combine multiplicatively; aging and extra curve factor are engineering allowances, not manufacturer guarantees. Confirm actual effective capacitance, loop stability, PFM ripple and load transients on prototype.'}
out=ROOT/'reports/electrical';out.mkdir(exist_ok=True)
(out/'capacitor_derating.json').write_text(json.dumps(result,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(7,4));ax.plot(x,22*(1+y/100),label='Manufacturer typical, one capacitor')
ax.axvline(vmax,color='#c24',ls='--',label=f'Maximum DC output estimate: {vmax:.3f} V')
ax.scatter([vmax],[typical_one],color='#c24');ax.set(xlim=(0,18),ylim=(0,23),xlabel='DC bias (V)',ylabel='Typical capacitance (µF)',title='22 µF / 25 V X5R capacitance under DC bias')
ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'capacitor_derating.png',dpi=180);fig.savefig(out/'capacitor_derating.pdf');plt.close(fig)
print(json.dumps(result,indent=2))
