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
# Independent 12 V current limit; 5 V retains its latched output switch.
v12min=1.188*(1+100000*(1-fb_budget)/(11100*(1+fb_budget)))-100e-9*100000*(1+fb_budget)
v12max=1.212*(1+100000*(1+fb_budget)/(11100*(1-fb_budget)))+100e-9*100000*(1+fb_budget)
switch={'12V_limit_A':[.048/(.1*(1+budget)),.052/(.1*(1-budget))], '5V_limit_A':[.001*25230/(59*(1+budget))**1.016,.001*22980/(59*(1-budget))**.94], 'note':'12 V automatic current limiting/recovery, not a latch. Hiccup depends on reaching the inductor limit at low output; verify shorts physically. 5 V latched fault requires power cycling.'}
# 300 mA useful per rail +10 mA pulls, 100 mA logic, 100 mA converter gate-bias allocation.
iin=1
for _ in range(100):
 vprot=6-iin*.276
 iin=(v12max*.31/.8+vregmax*(.31+.10+.10)/.8)/vprot
assert vregmax/vprot<.95 and iin<1.8
assert vregmin>=4.75 and vregmax<=5.5
assert M['F1']['mpn']=='0451003.MRL'
power={'input_range_V':[6,22],'sensor_load_A_per_rail_shared':.3,'logic_allowance_A':.1,'converter_5V_bias_allowance_A':.1,'converter_efficiency_assumptions':[.8,.8],'entry_resistance_assumption_ohm':.276,'input_current_at_6V_A':iin,'protected_input_at_6V_V':vprot,'max_duty_budget':vregmax/vprot,'input_fuse_A':3,'input_fuse_normal_current_fraction':iin/3,'LDO_loss_budget_W':(vregmax-3.3)*.1,'buck_peak_ripple_at22V_A':vregmax*(1-vregmax/22)/(8e-6*450e3),'sensor5_min_before_distribution_loss_V':vregmin-.31*.135,'sensor5_max_DC_budget_V':vregmax,'sensor12_DC_budget_V':[v12min,v12max],'note':'Efficiency and entry resistance are planning assumptions, not measured results. Gate-bias allocation is a supply-sizing requirement, not measured idle consumption. Startup/brownout sequencing below the 6 V operating limit requires qualification.'}
# Effective output bank from Samsung typical DC-bias curve plus explicit derating factors.
source=R/'sources/datasheets/samsung_CL31A226_characteristics.json'
data=json.loads(source.read_text());points=next(x for x in data if x['graphType']=='DCBias')['selectPartsList'][0]['chartList'][0]['data'];points=sorted((float(p['x']),float(p['y'])) for p in points)
for (x1,y1),(x2,y2) in zip(points,points[1:]):
 if x1<=vregmax<=x2:bias=y1+(y2-y1)*(vregmax-x1)/(x2-x1);break
one=22*(1+bias/100)*.9*.85*.95*.9
cap={'part':'CL31A226KAHNNNE','count':3,'nominal_uF':66,'bias_voltage_V':vregmax,'typical_bias_change_percent':bias,'additional_factors':[.9,.85,.95,.9],'budgeted_bank_uF':3*one,'two_part_bank_uF':2*one,'target_uF':25,'note':'Manufacturer typical curve and independent engineering budgets, not a guaranteed minimum. Keep all three output capacitors pending measured loop/transient qualification.'}
assert cap['budgeted_bank_uF']>25
stress={'input_signal_range_V':[0,30],'sense_node_at30V_worst_V':vsense,'series_resistor_at30V_W':30**2/(220000*(1-budget)),'pulldown_at30V_W':30**2/(10000*(1-budget)),'pulldown_rating_W':.25,'pullup_at3V3_W':(3.3*1.03)**2/(1000*(1-budget)),'pullup_rating_W':.125,'input_TVS_standoff_V':30,'entry_TVS_standoff_V':22,'entry_TVS_specified_pulse_clamp_V':35.5,'buck_abs_max_V':40,'bulk_rating_V':50,'input_series_fault_tolerance':'One series resistor; no longer survives that resistor shorting as a guaranteed fault case.','scope':'Unidirectional TVS provides negative surge clamping; not continuous negative signal operation, sustained overvoltage regulation or load-dump qualification.'}
assert stress['pulldown_at30V_W']<.25*(155-85)/(155-70) and stress['pullup_at3V3_W']<.125*(155-85)/(155-70)
(R/'reports/electrical').mkdir(parents=True,exist_ok=True)
report={'assumptions':a,'thresholds':limits,'nominal_input':nom,'buck':{'nominal_V':.6*(1+102/13.7),'feedback_resistor_budget_fraction':fb_budget,'DC_reference_divider_and_FB_leakage_budget_V':[vmin,vmax],'with_40mV_regulation_budget_V':[vregmin,vregmax]},'power':power,'current_limiters':switch,'capacitors':cap,'stress':stress,'status':'Numerical assertions passed; physical qualification not performed.'}
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

# Use the manufacturer's measured typical curves with separate tolerance/temperature/aging budgets.
def effective_1210(voltage):
 data=json.loads((R/'sources/datasheets/samsung_CL32B106_characteristics.json').read_text())
 pts=next(x for x in data if x['graphType']=='DCBias')['selectPartsList'][0]['chartList'][0]['data']
 pts=sorted((float(p['x']),float(p['y'])) for p in pts)
 for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
  if x1<=voltage<=x2:
   bias=y1+(y2-y1)*(voltage-x1)/(x2-x1)
   return {'voltage_V':voltage,'typical_bias_percent':bias,'budgeted_each_uF':10*(1+bias/100)*.9*.85*.95*.9}
 raise ValueError(voltage)
cin=effective_1210(22);cout=effective_1210(v12max);cvcc=effective_1210(vregmax)
assert 2*cin['budgeted_each_uF']>=4.7
assert 3*cout['budgeted_each_uF']>=10
assert cvcc['budgeted_each_uF']>=4.7
fsw=1000/(.05*24900+35)*1e6
assert 3.3*.8 > 1.2/(fsw*.9/1e6)
report['regulated12']={'nominal_V':1.2*(1+100/11.1),'DC_budget_V':[v12min,v12max],'frequency_nominal_Hz':fsw,'inductor_uH':3.3,'inductor_min_uH':2.64,'inner_loop_min_uH':1.2/(fsw*.9/1e6),'input_cap_bank':dict(count=2,**cin),'output_cap_bank':dict(count=3,**cout),'gate_bias_cap':dict(count=1,**cvcc),'compensation_resistor_ohm':10000,'compensation_cap_F':33e-9,'scope':'Typical bias curves plus engineering allowances are not guaranteed minimum capacitances. Validate substitutes and transient behavior on hardware.'}
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['regulated12'],indent=2))

# Software bias: qualify sensor off-state leakage and cable capacitance separately.
for ch in range(1,4):
 assert M[f'R{ch}10']['value']=='1k' and M[f'R{ch}09']['value']=='10k'
 assert M[f'Q{ch}01']['mpn']=='AO3401A' and M[f'Q{ch}02']['mpn']=='BSS138BK,215'
 assert f'JP{ch}03' not in M
assert M['R52']['value']=='10k'
source_min=3.3*.97-.55-.02 # BAT forward engineering allowance + PMOS drop
rup=1000*(1+budget);rdown=10000*(1+budget)
# Conservative input network load: SIG/(220k+20k), ignoring positive feedback help.
npn_high=(source_min-100e-6*rup)/(1+rup/(240000*(1-budget)))
pnp_low=101e-6*(rdown+15) # includes 1uA switch allowance, 15ohm hot on-resistance allowance
assert npn_high>=2.4+.1 and pnp_low<=1.2-.1
bias=dict(pullup_rail_V=3.3,pullup_ohm=1000,pulldown_ohm=10000,npn_off_leakage_budget_A=100e-6,pnp_off_leakage_budget_A=100e-6,npn_inactive_min_V=npn_high,pnp_inactive_max_V=pnp_low,npn_max_sink_A=3.3*1.03/(1000*(1-budget)),unpowered_rail_max_V_at_60C=3*20e-6*10000*(1+budget),probe_settle_ms=2,classification_confirmation_pairs=2,estimated_floating_discharge_10nF_ms=10000*10e-9*math.log(3.3/1.3)*1000,limitations='Sensor residual LOW must be <=1.2 V at ~3.5 mA. Leakage budgets are compatibility limits, not measured guarantees. BAT46W 20uA reverse limit is specified at 60C/75V; 10k rail bleed is not galvanic isolation. Forward .55V and hot MOSFET 15ohm are engineering allowances requiring bench/temperature verification. Float mode for slow signals only; test actual cable capacitance and sensor leakage.')
report['software_bias']=bias
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(bias,indent=2))
