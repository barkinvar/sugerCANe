"""Reproducible DC/tolerance budgets; expressly not physical prototype qualification."""
from pathlib import Path
import itertools,json,math
R=Path(__file__).resolve().parents[1];M=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
for ref,value in {'R1':'102k','R2':'13.7k','R50':'100k','R51':'5.23k','R101':'220k','R103':'20k','R104':'2.2M','R105':'10k'}.items():assert M[ref]['value']==value
budget=.0175 # 1% initial +100 ppm/C*65C +0.1% extra.
a={'resistors_total_fraction':budget,'logic_rail_fraction':.03,'comparator_offset_V':.0055,'input_bias_A_per_pin':50e-9,'shared_reference_inputs':4,'output_leakage_A':100e-9,'output_low_range_V':[0,.55], 'scope':'Offset includes common-mode/supply margin. TI lists typical bias/leakage, not guaranteed maxima; these allowances require prototype qualification.'}
rise=[];fall=[]
for signs in itertools.product((-1,1),repeat=6):
 rs,rg,rf,rp,rt,rb=[x*(1+budget*s) for x,s in zip([220e3,20e3,2.2e6,10e3,100e3,5230],signs)]
 for vr,off,ibref,ibs in itertools.product((3.3*.97,3.3*1.03),(-.0055,.0055),(-200e-9,200e-9),(-50e-9,50e-9)):
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
# Boost feedback: independent upper 0.1% and lower 1% resistor budgets.
# Datasheet FB bounds 1.230..1.246 V, with an extra +/-5 mV engineering allowance.
v12min=(1.230-.005)*(1+100000*(1-fb_budget)/(11500*(1+budget)))-100e-9*100000*(1+fb_budget)
v12max=(1.246+.005)*(1+100000*(1+fb_budget)/(11500*(1-budget)))+100e-9*100000*(1+fb_budget)
def ilim(k):
 return [.001*25230/(k*(1+budget))**1.016,.001*22980/(k*(1-budget))**.94]
switch={'boost_input_limit_A':ilim(21.5),'5V_limit_A':ilim(59), 'note':'Both TPS2553DBVR-1 switches latch off after overload deglitch. Boost input protection interrupts the inductor/diode DC path. Limits are branch input limits; 12V useful output remains 300mA.'}
logic=.10
# Boost rail has its own switch; 0.135ohm hot RON + 0.12V PCB-drop allowance.
# Pre-order native-route screening finds about 80mV at 1.1A and 85C before
# ground/contact/etch allowances. The former 50mV allowance was insufficient.
vin_boost_min=vregmin-1.10*.135-.12
iboost=v12max*.31/(vin_boost_min*.80)
max_buck_load=sum(q[1] for q in [switch['boost_input_limit_A'],switch['5V_limit_A']])+logic
normal_buck_load=iboost+.31+logic
assert iboost<switch['boost_input_limit_A'][0], (iboost,switch)
assert max_buck_load<2.0
assert normal_buck_load<2.0
# Worst normal load, minimum input, cascaded efficiency and connector/fuse budget.
iin=1
for _ in range(100):
 vprot=6-iin*.276
 iin=vregmax*normal_buck_load/(.8*vprot)
assert vregmax/vprot<.95 and iin<1.9
assert vregmin>=4.75 and vregmax<=5.5 and v12min>11.5 and v12max<12.5
assert M['F1']['mpn']=='0451003.MRL'
power={'input_range_V':[6,22],'sensor_load_A_per_rail_shared':.3,'logic_allowance_A':logic,'converter_efficiency_assumptions':[.8,.8],'entry_resistance_assumption_ohm':.276,'input_current_at_6V_A':iin,'protected_input_at_6V_V':vprot,'max_duty_budget':vregmax/vprot,'input_fuse_A':3,'input_fuse_normal_current_fraction':iin/3,'LDO_loss_budget_W':(vregmax-3.3)*logic,'buck_peak_ripple_at22V_A':vregmax*(1-vregmax/22)/(8e-6*450e3),'sensor5_min_before_distribution_loss_V':vregmin-.31*.135,'sensor5_max_DC_budget_V':vregmax,'sensor12_DC_budget_V':[v12min,v12max],'boost_PCB_drop_allowance_V':.12,'boost_min_input_V':vin_boost_min,'boost_normal_input_A':iboost,'buck_normal_output_A':normal_buck_load,'buck_both_limiters_max_plus_logic_A':max_buck_load,'buck_continuous_rating_A':2.,'note':'Efficiency, wiring resistance and PCB drops are explicit planning allowances. Current sharing, inrush and both simultaneous faults need scope/thermal tests. Below 6V is brownout territory.'}
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

# Three 22uF capacitors derated at 12V; same exact MPN/curve as the 5V bank.
def effective_22(voltage):
 for (x1,y1),(x2,y2) in zip(points,points[1:]):
  if x1<=voltage<=x2:
   bias=y1+(y2-y1)*(voltage-x1)/(x2-x1)
   return {'voltage_V':voltage,'typical_bias_percent':bias,'budgeted_each_uF':22*(1+bias/100)*.9*.85*.95*.9}
 raise ValueError(voltage)
cin=effective_22(vregmax);cout=effective_22(v12max)
assert cin['budgeted_each_uF']>=8 and 3*cout['budgeted_each_uF']>=9
Lmin=3.3e-6*.8;fsmin=.9e6
D=1-vin_boost_min/(v12max+.5)
ripple=vin_boost_min*D/(Lmin*fsmin);peak=iboost+ripple/2
assert peak<2.0 # guaranteed minimum converter switch limit, not typical 2.6A
# Inductor remains above the maximum (3.2A) switch threshold under faults.
assert M['L2']['mpn']=='SRP5030TA-3R3M'
assert M['U9']['mpn']=='TPS2553DBVR-1' and M['U9']['pins']['1']=='V5_INTERNAL'
assert M['U8']['pins']['6']=='V5_BOOST' and M['D4']['pins']=={'1':'SENSOR_12V','2':'BOOST_SW'}
report['regulated12']={'nominal_V':1.238*(1+100/11.5),'DC_budget_V':[v12min,v12max],'frequency_nominal_Hz':1.2e6,'inductor_uH':3.3,'inductor_min_uH':2.64,'input_cap_bank':dict(count=1,**cin),'output_cap_bank':dict(count=3,**cout),'compensation_resistor_ohm':13000,'compensation_cap_F':33e-9,'inductor_peak_A':peak,'switch_limit_min_A':2.0,'switch_limit_max_A':3.2,'inductor_saturation_rating_A':8,'diode_average_rating_A':2,'diode_reverse_rating_V':40,'output_ripple_capacitive_budget_V':.31*D/(3*cout['budgeted_each_uF']*1e-6*fsmin),'output_cap_energy_J':.5*66e-6*v12max**2,'scope':'Typical bias curves plus engineering allowances, not guaranteed capacitance. The charged output bank can discharge before U9 interrupts a short. Test short insertion, hot-plug capacitance, SW overshoot and transient response.'}
# U7D rail monitor shares REF_LOGIC and is wire-ANDed with U9 fault.
pg_rise=[];pg_fall=[]
for sr,sg,sf,st,sb,rail,off in itertools.product((-1,1),repeat=7):
 rs,rg,rf,rt,rb=[v*(1+budget*x) for v,x in zip([100000,1800,2200000,100000,5230],[sr,sg,sf,st,sb])]
 for ib in (-200e-9,200e-9):
  vr=(3.3*(1+.03*rail)/rt-ib)/(1/rt+1/rb)+.0055*off
  for vo in (0,.55):pg_rise.append(vr*(1+rs/rg+rs/rf)-vo*rs/rf)
  pg_fall.append(vr*(1+rs/rg+rs/rf)-3.3*(1+.03*rail)*rs/rf)
assert max(pg_rise)<v12min and min(pg_fall)>7.5
report['rail_monitor']={'nominal_rising_V':vref*(1+100000/1800+100000/2200000)-.15*100000/2200000,'rising_budget_V':[min(pg_rise),max(pg_rise)],'falling_budget_V':[min(pg_fall),max(pg_fall)],'note':'Healthy-rail indicator only. Not a 12V tolerance monitor or ADC. U9 active fault also forces PG low.'}
# LDO output retains 4.7uF X7R/25V; reserve 50% for DC bias at 3.3V,
# then separate tolerance/temperature/aging factors. Qualify replacement lots.
ldo_cmin=4.7*.5*.9*.85*.95
assert ldo_cmin>1.
report['passive_substitutions']={'LDO_effective_output_cap_budget_uF':ldo_cmin,'LDO_required_output_uF':1.,'assumed_DC_bias_retention':.5,'scope':'Engineering screening allowance, not a measured curve. Same nominal voltage, capacitance, dielectric and footprint; verify effective capacitance/ESR on prototype.'}
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n')

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
