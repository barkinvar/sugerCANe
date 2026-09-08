"""Deterministic electrical checks for revision B; not a hardware certification."""
from pathlib import Path
import itertools
import json
import math

OUT = Path(__file__).resolve().parents[1] / "reports/electrical"
OUT.mkdir(parents=True, exist_ok=True)
report = {"assumptions": {
    "resistor_tolerance_initial": 0.01, "resistor_total_budget": 0.0175, "logic_rail_tolerance_budget": 0.03,
    "comparator_offset_V": 0.0055, "comparator_input_bias_A": 50e-9,
    "comparator_output_low_V": [0, 0.55], "comparator_high_leakage_A": 100e-9,
    "comparator_supply": "LM339LV on regulated 3V3; 5.5mV offset includes CMRR/PSRR allowance. Bias and leakage bounds are engineering allowances, not published maxima.",
    "scope": "DC corner analysis and conservative first-order power estimates; parasitic/transient/thermal behavior requires prototype tests."
}}

def thresholds(low_mode):
    rise, fall = [], []
    # Both 110k series resistors may move together to the extreme; their sum
    # has the same bound. Budget1.75% covers1%initial+100ppm/C*65C+0.1%allowance. All other tolerances are independent.
    nom = (220e3, 20e3, 910e3, 10e3, 100e3, 17.8e3, 7.15e3)
    for signs in itertools.product((-1, 1), repeat=len(nom)):
        rs, rg, rf, rp, rt, rb, rm = [v*(1+0.0175*s) for v,s in zip(nom,signs)]
        for vr, voff, ibm, ibp in itertools.product((3.3*.97,3.3*1.03),(-.0055,.0055),(-50e-9,50e-9),(-50e-9,50e-9)):
            g = 1/rt + 1/rb + (1/rm if low_mode else 0)
            vref = (vr/rt - ibm)/g
            vn = vref + voff
            for vol in (0,.55):
                rise.append(vn*(1+rs/rg+rs/rf) - vol*rs/rf + ibp*rs)
            for leak in (0,100e-9):
                voh = (vr/rp+vn/rf-leak)/(1/rp+1/rf)
                fall.append(vn*(1+rs/rg+rs/rf) - voh*rs/rf + ibp*rs)
    return {"rising_V": [min(rise),max(rise)], "falling_V": [min(fall),max(fall)],
            "corners_evaluated":len(rise)+len(fall)}

report['input_logic']=thresholds(True);report['input_industrial']=thresholds(False)
assert report['input_logic']['falling_V'][0]>.8 and report['input_logic']['rising_V'][1]<2.4
assert report['input_industrial']['falling_V'][0]>4 and report['input_industrial']['rising_V'][1]<7
report['input_targets']={'logic_low_max_V':.8,'logic_high_min_V':2.4,'industrial_low_max_V':4,'industrial_high_min_V':7,'positive_signal_max_V':30,'qualification':'Targets supported by stated corner allowances; physical leakage, temperature and transient tests outstanding.'}
# Maximum sense node at 30V, including positive feedback from a high output.
rs=220e3*.9825;rg=20e3*1.0175;rf=910e3*.9825
vsense=(30/rs+(3.3*1.03)/rf)/(1/rs+1/rg+1/rf)
report['comparator']={'part':'LM339LVDR','supply_V':3.3,'maximum_sense_node_at_30V_V':vsense,'minimum_logic_supply_V':3.3*.97,'input_failsafe':'Inputs tolerate up to 5.5V independently of supply, per TI. External 30V always passes through two series 110k resistors and the divider.','offset_allowance_V':.0055,'input_bias_allowance_A':50e-9,'output_leakage_allowance_A':100e-9,'note':'Published LV bias/output leakage values are typical; allowances require bench qualification. 0.55V VOL allowance exceeds the 0.30V LV maximum at 4mA.'}
assert vsense<3.3*.97
vnom=.6*(1+100/17.8)
vmin=.6*.985*(1+100*.9825/(17.8*1.0175))
vmax=.6*1.025*(1+100*1.0175/(17.8*.9825))
report['buck']={'part':'LMR51420XDDCR','nominal_output_V':vnom,'regulation_and_resistor_budget_V':[vmin,vmax],'minimum_operating_input_V':4.5,'UVLO_rising_max_V':4.5,'inductor_uH':10,'inductor_min_uH':8,'frequency_min_kHz':450,'ripple_at_22V_A':vmax*(1-vmax/22)/(8e-6*450e3),'note':'Historical net name V4P2 denotes this approximately 4V intermediate rail.'}
# Both sensor rails loaded, bias/bleed allowance and deliberately generous logic budget.
eta_buck=eta_boost=.80;boost_load=.31+.15;entry_r=.126+.04+.11
iin=1
for _ in range(100):
 vprot=5-iin*entry_r
 iin=.32+5.15*boost_load/(vprot*eta_buck*eta_boost)
vprot=5-iin*entry_r
boost_input_min=vmin-.08 # inductor DCR/trace allowance
ripple_allowance=.40
imax=boost_input_min*(1.10-ripple_allowance/2)*eta_boost/5.15
report['power_budget']={'sensor_5V_target_A_shared':.3,'sensor_VBAT_target_A_shared':.3,'logic_5V_allowance_A':.15,'total_boost_load_with_bias_A':boost_load,'buck_efficiency_assumption':eta_buck,'boost_efficiency_assumption':eta_boost,'entry_resistance_allowance_ohm':entry_r,'fuse_hot_resistance_allowance_ohm':.126,'pmos_hot_resistance_allowance_ohm':.04,'trace_connector_allowance_ohm':.11,'input_current_at_5V_estimate_A':iin,'protected_input_at_5V_estimate_V':vprot,'buck_max_output_to_input_ratio':vmax/vprot,'LDO_loss_at_logic_allowance_W':(5.15-3.3)*.15,'note':'Efficiencies, hot resistances and current allocations are engineering assumptions, not measured guarantees. Input specification applies at J1 under load.'}
assert vprot>4.5 and vmax/vprot<.95 and iin<1.2
report['boost']={'part':'TPS613222ADBVR','fixed_output_range_V':[4.85,5.15],'minimum_peak_current_limit_A':1.10,'maximum_peak_current_limit_A':2.50,'ripple_allowance_A':ripple_allowance,'input_voltage_after_DCR_allowance_V':boost_input_min,'estimated_output_capability_A':imax,'required_output_A':boost_load,'inductor_min_saturation_A':3.5,'inductor_rms_A':2.6,'inductor_max_DCR_ohm':.105,'output_capacitance_nominal_uF':44,'output_capacitance_simulation_uF':30,'note':'TI equation 1, conservative 80% efficiency and 400mA ripple allowance. Not a guaranteed output current rating. Verify capacitor DC bias and cascaded converter interaction.'}
assert imax>boost_load
report['sensor_switches']={'5V_limit_min_mA':25230/(59*1.0175)**1.016,'5V_limit_max_mA':22980/(59*.9825)**.94,'VBAT_limit_min_mA':1000*.8*2500/3900*.85/1.0175,'VBAT_limit_max_mA':1000*.8*2500/3900*1.15/.9825,'VBAT_latch_delay_typ_ms':.4+33e-9*1.45/4.5e-6*1000,'5V_switch_Ron_max_ohm':.135,'5V_voltage_after_switch_at_310mA_min_V':4.85-.31*.135,'note':'Subtract actual copper, connector and shunt losses from port voltage. VBAT current-limit accuracy requires VS-OUT >=2.5V. Fault timing is typical.'}
report['protection']={'continuous_input_V':[5,22],'TVS_standoff_V':22,'TVS_specified_pulse_clamp_V':35.5,'buck_absolute_max_V':40,'pmos_VDS_absolute_max_V':40,'bulk_capacitor_rating_V':50,'gate_resistor_power_at_clamp_W':(35.5-12)**2/10000,'port_pullup_fault_power_at_22p7V_W':22.7**2/(4700*.9825),'port_pullup_resistor_rating_W':.125,'pulldown_power_at_30V_W':30**2/(4700*.9825),'pulldown_rating_W':.75,'limitation':'Not sustained overvoltage protection, automotive load-dump qualification or reverse-current isolation. TVS overshoot and energy require physical tests.'}
assert report['protection']['port_pullup_fault_power_at_22p7V_W']<.125
report['startup']={'VBAT_example_sensor_capacitance_uF':40,'VBAT_board_capacitance_allowance_uF':1.1,'VBAT_full_load_A':.32,'VBAT_charge_time_at22V_ms':41.1e-6*22/(report['sensor_switches']['VBAT_limit_min_mA']/1000-.32)*1000,'note':'Compare to typical 11.0ms latch delay; startup inrush can exceed steady load and needs measurement. Firmware ADC undervoltage blanking is 5ms.'}
report['result']='DC and corner assertions passed for the explicit engineering assumptions. No physical qualification performed.'
(OUT/'calculations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
