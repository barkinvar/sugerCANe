"""Reproducible DC/tolerance budgets; expressly not physical prototype qualification."""
from pathlib import Path
import itertools,json,math
R=Path(__file__).resolve().parents[1];M=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
for ref,value in {'R1':'102k','R2':'13.7k','R50':'100k','R51':'5.23k','R101':'220k','R103':'20k','R104':'2.2M','R105':'10k'}.items():assert M[ref]['value']==value
budget=.0175 # 1% initial +100 ppm/C*65C +0.1% extra.
a={'resistors_total_fraction':budget,'logic_rail_fraction':.03,'comparator_offset_V':.0055,'input_bias_A_per_pin':50e-9,'shared_reference_inputs':3,'output_leakage_A':100e-9,'output_low_range_V':[0,.55], 'scope':'Offset includes common-mode/supply margin. TI lists typical bias/leakage, not guaranteed maxima; these allowances require prototype qualification.'}
rise=[];fall=[]
for signs in itertools.product((-1,1),repeat=6):
 rs,rg,rf,rp,rt,rb=[x*(1+budget*s) for x,s in zip([220e3,20e3,2.2e6,10e3,100e3,5230],signs)]
 for vr,off,ibref,ibs in itertools.product((3.3*.97,3.3*1.03),(-.0055,.0055),(-150e-9,150e-9),(-50e-9,50e-9)):
  vref=(vr/rt-ibref)/(1/rt+1/rb);vn=vref+off
  for vol in (0,.55):rise.append(vn*(1+rs/rg+rs/rf)-vol*rs/rf+ibs*rs)
  for leak in (0,100e-9):
   voh=(vr/rp+vn/rf-leak)/(1/rp+1/rf)
   fall.append(vn*(1+rs/rg+rs/rf)-voh*rs/rf+ibs*rs)
limits={'rising_V':[min(rise),max(rise)],'falling_V':[min(fall),max(fall)],'corners':len(rise)+len(fall),'logic_low_target_V':1.2,'logic_high_target_V':2.4,'ground_offset_allowance_V':.1}
assert min(fall)>1.2+.1 and max(rise)<2.4-.1, limits
vref=3.3*5230/(100000+5230);gain=1+220000/20000+220000/2200000
nom={'rising_V':vref*gain-.15*220000/2200000,'falling_V':vref*gain-((3.3/10000+vref/2200000)/(1/10000+1/2200000))*220000/2200000,'sense_filter_tau_us':1e-9/(1/220000+1/20000+1/2200000)*1e6}
fb_budget=.00375 # 0.1% initial +25ppm/C*65C +0.1125% allowance.
assert all(M[r]["tolerance"]=="0.1%" for r in ["R1","R2"])
vmin=.591*(1+102e3*(1-fb_budget)/(13700*(1+fb_budget)))-50e-9*102e3*(1+fb_budget)
vmax=.609*(1+102e3*(1+fb_budget)/(13700*(1-fb_budget)))+50e-9*102e3*(1+fb_budget)
# Add separate regulation/transient budget rather than representing it as a DC datasheet guarantee.
vregmin=vmin-.04;vregmax=vmax+.04
rs=220000*(1-budget);rg=20000*(1+budget);rf=2200000*(1-budget)
vsense=(30/rs+3.3*1.03/rf)/(1/rs+1/rg+1/rf)
assert vsense<3.3*.97
switch={'VBAT_limit_A':[.8*2500/3900*.8/(1+budget),.8*2500/3900*1.2/(1-budget)],'5V_limit_A':[.001*25230/(59*(1+budget))**1.016,.001*22980/(59*(1-budget))**.94],'VBAT_latch_delay_typ_ms':.4+33e-9*1.45/4.5e-6*1000,'note':'Conservative 20% battery limit accuracy budget; actual table depends on current and VS-OUT>=2.5V. Latch delay and short-circuit behavior require measurement. Both rails reset by power cycling.'}
# 300mA useful per rail plus pullups. 100mA budget for MCU/CAN/comparator at 3V3.
iin=1
for _ in range(100):
 vprot=6-iin*.276
 iin=.31+vregmax*(.31+.10)/(vprot*.8)
assert vregmax/vprot<.95 and iin<1.2
power={'input_range_V':[6,22],'sensor_load_A_per_rail_shared':.3,'logic_allowance_A':.1,'buck_efficiency_assumption':.8,'entry_resistance_assumption_ohm':.276,'input_current_at_6V_A':iin,'protected_input_at_6V_V':vprot,'max_duty_budget':vregmax/vprot,'LDO_loss_budget_W':(vregmax-3.3)*.1,'buck_peak_ripple_at22V_A':vregmax*(1-vregmax/22)/(8e-6*450e3),'sensor5_min_before_distribution_loss_V':vregmin-.31*.135,'sensor5_max_DC_budget_V':vregmax,'note':'No guarantee of 5V +/-5% at a remote sensor. Include actual connector/wire losses and measure load transients.'}
# Effective output bank from Samsung typical DC-bias curve plus explicit derating factors.
source=R/'sources/datasheets/samsung_CL31A226_characteristics.json'
data=json.loads(source.read_text());points=next(x for x in data if x['graphType']=='DCBias')['selectPartsList'][0]['chartList'][0]['data'];points=sorted((float(p['x']),float(p['y'])) for p in points)
for (x1,y1),(x2,y2) in zip(points,points[1:]):
 if x1<=vregmax<=x2:bias=y1+(y2-y1)*(vregmax-x1)/(x2-x1);break
one=22*(1+bias/100)*.9*.85*.95*.9
cap={'part':'CL31A226KAHNNNE','count':3,'nominal_uF':66,'bias_voltage_V':vregmax,'typical_bias_change_percent':bias,'additional_factors':[.9,.85,.95,.9],'budgeted_bank_uF':3*one,'two_part_bank_uF':2*one,'target_uF':25,'note':'Manufacturer typical curve and independent engineering budgets, not a guaranteed minimum. Keep all three output capacitors pending measured loop/transient qualification.'}
assert cap['budgeted_bank_uF']>25
stress={'input_signal_range_V':[0,30],'sense_node_at30V_worst_V':vsense,'series_resistor_at30V_W':30**2/(220000*(1-budget)),'pulldown_at30V_W':30**2/(10000*(1-budget)),'pulldown_rating_W':.25,'pullup_at22V_W':22**2/(10000*(1-budget)),'pullup_rating_W':.125,'input_TVS_standoff_V':30,'entry_TVS_standoff_V':22,'entry_TVS_specified_pulse_clamp_V':35.5,'buck_abs_max_V':40,'bulk_rating_V':50,'input_series_fault_tolerance':'One series resistor; no longer survives that resistor shorting as a guaranteed fault case.','scope':'Unidirectional TVS provides negative surge clamping; not continuous negative signal operation, sustained overvoltage regulation or load-dump qualification.'}
assert stress['pulldown_at30V_W']<.25*(155-85)/(155-70) and stress['pullup_at22V_W']<.125*(155-85)/(155-70)
report={'assumptions':a,'thresholds':limits,'nominal_input':nom,'buck':{'nominal_V':.6*(1+102/13.7),'feedback_resistor_budget_fraction':fb_budget,'DC_reference_divider_and_FB_leakage_budget_V':[vmin,vmax],'with_40mV_regulation_budget_V':[vregmin,vregmax]},'power':power,'current_limiters':switch,'capacitors':cap,'stress':stress,'status':'Numerical assertions passed; physical qualification not performed.'}
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
