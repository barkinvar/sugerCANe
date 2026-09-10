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
# Boost feedback: independent upper 0.1% and lower 1% resistor budgets.
# Datasheet FB bounds 1.230..1.246 V, with an extra +/-5 mV engineering allowance.
v12min=(1.230-.005)*(1+100000*(1-fb_budget)/(11500*(1+budget)))-100e-9*100000*(1+fb_budget)
v12max=(1.246+.005)*(1+100000*(1+fb_budget)/(11500*(1-budget)))+100e-9*100000*(1+fb_budget)
def ilim(k):
 return [.001*25230/(k*(1+budget))**1.016,.001*22980/(k*(1-budget))**.94]
# TPS259620 equation 4; resistor drift budget and full-range +/-10.4% accuracy.
efuse_min=(903/(2610*(1+budget))+.0112)*(1-.104)
efuse_max=(903/(2610*(1-budget))+.0112)*(1+.104)
switch={'12V_output_limit_A':[efuse_min,efuse_max],'5V_limit_A':ilim(59),
        'note':'U9 limits the protected 12 V output after the boost reservoir. U4 and U9 latch on their specified faults. MCU enables allow deliberate CAN reset; no automatic retry.'}
assert efuse_min>.3001 and efuse_max<.41
logic=.15 # Includes 20 mA RGB/buffer allowance; retained 3.3 V logic reserve.
# The removed boost-input switch no longer contributes RON or overload deglitch.
vin_boost_min=vregmin-.12
iboost=v12max*.31/(vin_boost_min*.80)
fault_boost=v12max*efuse_max/(vin_boost_min*.80)
max_buck_load=fault_boost+switch['5V_limit_A'][1]+logic
normal_buck_load=iboost+.31+logic
assert M['U1']['mpn']=='LMR51430XDDCR' and M['L1']['mpn']=='SRP7028A-8R2M' and M['L1']['value']=='8.2uH'
assert max_buck_load<2.0 and normal_buck_load<2.0 # Retained load budget, below the new 3 A device rating.
# Worst normal load, minimum input, cascaded efficiency and connector/fuse budget.
iin=1
for _ in range(100):
 vprot=6-iin*.276
 iin=vregmax*normal_buck_load/(.8*vprot)
assert vregmax/vprot<.95 and iin<1.9
assert vregmin>=4.75 and vregmax<=5.5 and v12min>11.5 and v12max<12.5
assert M['F1']['mpn']=='0451003.MRL'
power={'input_range_V':[6,22],'sensor_load_A_per_rail_shared':.3,'logic_allowance_A':logic,'converter_efficiency_assumptions':[.8,.8],'entry_resistance_assumption_ohm':.276,'input_current_at_6V_A':iin,'protected_input_at_6V_V':vprot,'max_duty_budget':vregmax/vprot,'input_fuse_A':3,'input_fuse_normal_current_fraction':iin/3,'LDO_loss_budget_W':(vregmax-3.3)*logic,'buck_peak_ripple_at22V_A':vregmax*(1-vregmax/22)/(8.2e-6*.8*450e3),'sensor5_min_before_distribution_loss_V':vregmin-.31*.135,'sensor5_max_DC_budget_V':vregmax,'sensor12_DC_budget_V':[v12min-.31*.131,v12max],'boost_PCB_drop_allowance_V':.12,'boost_min_input_V':vin_boost_min,'boost_normal_input_A':iboost,'buck_normal_output_A':normal_buck_load,'buck_both_limiters_max_plus_logic_A':max_buck_load,'boost_fault_input_budget_A':fault_boost,'buck_continuous_rating_A':3.,'note':'Efficiency, wiring resistance and PCB drops are explicit planning allowances. Current sharing, inrush and both simultaneous faults need scope/thermal tests. Below 6V is brownout territory.'}
# Effective output bank from Samsung typical DC-bias curve plus explicit derating factors.
source=R/'sources/datasheets/samsung_CL31A226_characteristics.json'
data=json.loads(source.read_text());points=next(x for x in data if x['graphType']=='DCBias')['selectPartsList'][0]['chartList'][0]['data'];points=sorted((float(p['x']),float(p['y'])) for p in points)
for (x1,y1),(x2,y2) in zip(points,points[1:]):
 if x1<=vregmax<=x2:bias=y1+(y2-y1)*(vregmax-x1)/(x2-x1);break
one=22*(1+bias/100)*.9*.85*.95*.9
cap={'part':'CL31A226KAHNNNE','count':3,'nominal_uF':66,'bias_voltage_V':vregmax,'typical_bias_change_percent':bias,'additional_factors':[.9,.85,.95,.9],'budgeted_bank_uF':3*one,'two_part_bank_uF':2*one,'target_uF':25,'note':'Manufacturer typical curve and independent engineering budgets, not a guaranteed minimum. Keep all three output capacitors pending measured loop/transient qualification.'}
assert cap['budgeted_bank_uF']>25
stress={'input_signal_range_V':[0,30],'sense_node_at30V_worst_V':vsense,'series_resistor_at30V_W':30**2/(220000*(1-budget)),'pulldown_at30V_W':30**2/(10000*(1-budget)),'pulldown_rating_W':.25,'pullup_at3V3_W':(3.3*1.03)**2/(1000*(1-budget)),'pullup_rating_W':.125,'input_TVS_standoff_V':30,'entry_TVS_standoff_V':22,'entry_TVS_specified_pulse_clamp_V':35.5,'buck_abs_max_V':38,'bulk_rating_V':50,'input_series_fault_tolerance':'One series resistor; no longer survives that resistor shorting as a guaranteed fault case.','scope':'Unidirectional TVS provides negative surge clamping; not continuous negative signal operation, sustained overvoltage regulation or load-dump qualification.'}
assert stress['pulldown_at30V_W']<.25*(155-85)/(155-70) and stress['pullup_at3V3_W']<.125*(155-85)/(155-70)
assert stress['entry_TVS_specified_pulse_clamp_V'] < stress['buck_abs_max_V']
stress['specified_clamp_to_buck_abs_margin_V'] = stress['buck_abs_max_V']-stress['entry_TVS_specified_pulse_clamp_V']
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
assert M['U9']['mpn']=='TPS259620DDAR' and M['U9']['pins']['4']=='BOOST_12V' and M['U9']['pins']['5']=='SENSOR_12V'
assert M['U8']['pins']['6']=='V5_INTERNAL' and M['D4']['pins']=={'1':'BOOST_12V','2':'BOOST_SW'}
report['regulated12']={'nominal_V':1.238*(1+100/11.5),'DC_budget_V':[v12min,v12max],'frequency_nominal_Hz':1.2e6,'inductor_uH':3.3,'inductor_min_uH':2.64,'input_cap_bank':dict(count=1,**cin),'output_cap_bank':dict(count=3,**cout),'compensation_resistor_ohm':13000,'compensation_cap_F':33e-9,'inductor_peak_A':peak,'switch_limit_min_A':2.0,'switch_limit_max_A':3.2,'inductor_saturation_rating_A':8,'diode_average_rating_A':2,'diode_reverse_rating_V':40,'output_ripple_capacitive_budget_V':.31*D/(3*cout['budgeted_each_uF']*1e-6*fsmin),'output_cap_energy_J':.5*66e-6*v12max**2,'scope':'Typical bias curves plus engineering allowances, not guaranteed capacitance. The boost reservoir is upstream of U9. Only C71 and external sensor capacitance can discharge directly into a port short. Test short insertion, hot-plug capacitance, SW overshoot and transient response.'}
# ADC voltage measurement: two series 100k resistors and one 20k bottom leg.
assert all(M[r]['value']=='100k' and M[r]['tolerance']=='0.1%' for r in ['R65','R66','R72','R73'])
assert all(M[r]['value']=='20k' for r in ['R67','R74'])
assert M['U5']['pins']['14']=='ADC_5V' and M['U5']['pins']['15']=='ADC_12V'
assert M['U4']['pins']['3']=='POWER_5V_EN' and M['Q3']['pins']['1']=='POWER_12V_EN'
uvlo_rise=[v*(1+100e3*(1+rs*fb_budget)/(12100*(1+rb*fb_budget))) for v,rs,rb in itertools.product((1.18,1.22),(-1,1),(-1,1))]
uvlo_fall=[v*(1+100e3*(1+rs*fb_budget)/(12100*(1+rb*fb_budget))) for v,rs,rb in itertools.product((1.08,1.13),(-1,1),(-1,1))]
# UVLO +/-100nA input leakage contributes 10mV referred to the raw rail.
uvlo_rise=[min(uvlo_rise)-.0101,max(uvlo_rise)+.0101]
uvlo_fall=[min(uvlo_fall)-.0101,max(uvlo_fall)+.0101]
assert uvlo_rise[1]<v12min and uvlo_fall[0]>9.5
report['rail_monitor']={'type':'ADC8/ADC9, calibrated against factory VREFINT',
 'divider_ratio':11,'divider_thevenin_ohm':200000*20000/220000,
 'ADC_at_30V_max_V':30*(20000*(1+fb_budget))/(200000*(1-fb_budget)+20000*(1+fb_budget)),
 'filter_time_constant_us':200000*20000/220000*10e-9*1e6,
 'ADC_acquisition_cycles':239.5,'firmware_good_windows_mV':[[11100,12900],[4550,5500]],
 'UVLO_rising_budget_V':uvlo_rise,'UVLO_falling_budget_V':uvlo_fall,
 'efuse_max_RON_loss_at_300mA_W':.3**2*.131,
 'efuse_slew_ms_at_12V':[12*47e-9*.9/(2.33e-6*21.5)*1000,12*47e-9*1.1/(1.89e-6*20.31)*1000],
 'note':'Rail ADCs qualify sensor power, not user analog inputs. Precision and transient excursions need measurement. Hardware UVLO, current limit and thermal latch remain independent of software. Startup grace 200ms; healthy 100ms; running low voltage 20ms; deliberate CAN restart only.'}
# LDO output retains 4.7uF X7R/25V; reserve 50% for DC bias at 3.3V,
# then separate tolerance/temperature/aging factors. Qualify replacement lots.
ldo_cmin=4.7*.5*.9*.85*.95
assert ldo_cmin>1.
# Health indications must tolerate ADC gain/offset error at normal rail corners.
# ST DS tables 4/25/50/56: +/-10mV calibration supply, 10mV VREF drift,
# +/-4 LSB ADC characterization and 0.2uA analog leakage. The 18.2kohm source
# exceeds the accuracy table's 10kohm condition; long acquisition plus 10nF
# is screened here with additional allowances, not a guaranteed ADC accuracy.
adc_gain=.025;adc_offset=.09;rail_copper=.06
predicted12=[(power['sensor12_DC_budget_V'][0]-rail_copper)*(1-adc_gain)-adc_offset,v12max*(1+adc_gain)+adc_offset]
predicted5=[(power['sensor5_min_before_distribution_loss_V']-rail_copper)*(1-adc_gain)-adc_offset,vregmax*(1+adc_gain)+adc_offset]
assert 11.1<predicted12[0] and predicted12[1]<12.9
assert 4.55<predicted5[0] and predicted5[1]<5.5
report['rail_monitor']['ADC_error_budget']=dict(gain_fraction=adc_gain,offset_V_at_sensor_rail=adc_offset,post_switch_copper_allowance_V=rail_copper,predicted_normal_readings_12V=predicted12,predicted_normal_readings_5V=predicted5,scope='Engineering budget including divider drift, VREF calibration/drift, ADC reference/channel errors, input leakage and settling. Requires meter/temperature correlation; health flags are not precision voltage compliance.')
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
bias=dict(pullup_rail_V=3.3,pullup_ohm=1000,pulldown_ohm=10000,npn_off_leakage_budget_A=100e-6,pnp_off_leakage_budget_A=100e-6,npn_inactive_min_V=npn_high,pnp_inactive_max_V=pnp_low,npn_max_sink_A=3.3*1.03/(1000*(1-budget)),bias_diodes_only_unpowered_rail_V_at_60C=3*20e-6*10000*(1+budget),probe_settle_ms=2,classification_confirmation_pairs=2,estimated_floating_discharge_10nF_ms=10000*10e-9*math.log(3.3/1.3)*1000,limitations='Sensor residual LOW must be <=1.2 V at ~3.5 mA. Leakage budgets are compatibility limits, not measured guarantees. BAT46W 20uA reverse limit is specified at 60C/75V; 10k rail bleed is not galvanic isolation. Forward .55V and hot MOSFET 15ohm are engineering allowances requiring bench/temperature verification. Float mode for slow signals only; test actual cable capacitance and sensor leakage.')
report['software_bias']=bias
# Conservative residual-charge bound: ignore ADC ground legs and diode drops.
# This is temporary backfeed from stored charge, not a supported reverse supply.
adc_backfeed=(v12max+vregmax)/(200000*(1-fb_budget))
report['rail_monitor']['charged_rail_ADC_injection_upper_bound_A']=adc_backfeed
report['rail_monitor']['bias_plus_charged_rails_bleed_upper_bound_V']=(adc_backfeed+3*20e-6)*10000*(1+budget)
report['rail_monitor']['unpowered_scope']='Stored sensor-rail charge can feed the MCU clamp through the 200kohm series ADC paths. Bound ignores diode drops and divider ground legs; no energized reverse-output support or unpowered functional guarantee.'
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(bias,indent=2))

# Default-off 12 V stage: raw rail -> R70 -> Q2 gate; Q3 shunts that gate.
assert M['Q2']['pins']=={'1':'EFUSE_INHIBIT','2':'GND','3':'EFUSE_EN'}
assert M['Q3']['pins']=={'1':'POWER_12V_EN','2':'GND','3':'EFUSE_INHIBIT'}
assert M['R70']['pins']=={'1':'BOOST_12V','2':'EFUSE_INHIBIT'}
assert M['R75']['pins']=={'1':'POWER_12V_EN','2':'GND'}
# Conservative 20 uA combined off-state gate/drain leakage allowance at R70.
r70max=100000*1.025
inhibit_gate_min=uvlo_rise[0]-20e-6*r70max
q3_on_gate_max=v12max/(100000*.975)*15
assert M['R75']['value']==M['R71']['value']=='10k'
mcu_reset_gate_max=2e-6*10000*1.025 # MCU input + low-voltage gate-leakage planning allowance
assert inhibit_gate_min>4.5 and q3_on_gate_max<.01 and mcu_reset_gate_max<.48
# 100 uF total external load, +20% capacitance, 1.2uF local output, and full 300mA.
charge_margin=efuse_min-.3001
max_charge_ms=(120e-6+1.2e-6)*v12max/charge_margin*1000
assert max_charge_ms+max(report['rail_monitor']['efuse_slew_ms_at_12V'])<180
report['startup_and_default_off']={
 'external_12V_capacitance_design_limit_uF':100,'external_capacitance_tolerance_budget':.2,
 'worst_constant_load_charge_ms':max_charge_ms,'firmware_startup_grace_ms':200,
 'inhibit_gate_min_at_UVLO_V':inhibit_gate_min,'Q3_on_inhibit_gate_max_V':q3_on_gate_max,
 'MCU_reset_gate_max_allowance_V':mcu_reset_gate_max,'Q2_normal_gate_max_V':v12max,
 'MOSFET_gate_absolute_max_V':20,'R70_leakage_allowance_A':20e-6,
 'scope':'Steady resistor/leakage bounds and constant-current capacitor charging. Hot RDS(on)=15ohm and MCU/low-VGS gate leakage are engineering allowances; qualify over intended temperature. 470uF standalone SPICE is a typical diagnostic beyond the 100uF supported design envelope. No fast transient, single-fault or PCB thermal qualification.'}
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n')
# The 5 V latch-off switch has a 5ms minimum current-limit deglitch delay.
# Reserve its maximum 1.5ms output rise-time allowance as well as C12 +20%.
cap5_charge_ms=(22e-6*1.2+22e-6*1.2)*vregmax/(switch['5V_limit_A'][0]-.3001)*1000
assert cap5_charge_ms+1.5<5
report['startup_and_default_off'].update(external_5V_capacitance_design_limit_uF=22,
    five_volt_charge_budget_ms=cap5_charge_ms,five_volt_rise_allowance_ms=1.5,
    five_volt_fault_deglitch_min_ms=5)
(R/'reports/electrical/electrical_checks.json').write_text(json.dumps(report,indent=2)+'\n')
