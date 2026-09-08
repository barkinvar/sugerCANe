"""Deterministic electrical checks for revision A; not a hardware certification."""
from pathlib import Path
import itertools
import json
import math

OUT = Path(__file__).resolve().parents[1] / "reports/electrical"
OUT.mkdir(parents=True, exist_ok=True)
report = {"assumptions": {
    "resistor_tolerance_initial": 0.01, "resistor_total_budget": 0.0125, "logic_rail_tolerance_budget": 0.03,
    "comparator_offset_V": 0.0055, "comparator_input_bias_A": 50e-9,
    "comparator_output_low_V": [0, 0.55], "comparator_high_leakage_A": 100e-9,
    "comparator_supply": "Protected battery rail, at least 5 V for full offset specification",
    "scope": "DC corner analysis and conservative first-order power estimates; parasitic/transient/thermal behavior requires prototype tests."
}}

def thresholds(low_mode):
    rise, fall = [], []
    # Both 110k series resistors may move together to the extreme; their sum
    # has the same +/-1% bound. All other tolerances are independent.
    nom = (220e3, 20e3, 910e3, 10e3, 100e3, 17.8e3, 7.15e3)
    for signs in itertools.product((-1, 1), repeat=len(nom)):
        rs, rg, rf, rp, rt, rb, rm = [v*(1+0.0125*s) for v,s in zip(nom,signs)]
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

report['input_logic'] = thresholds(True)
report['input_industrial'] = thresholds(False)
assert report['input_logic']['falling_V'][0] > .8
assert report['input_logic']['rising_V'][1] < 2.4
assert report['input_industrial']['falling_V'][0] > 4
assert report['input_industrial']['rising_V'][1] < 7
report['input_guarantee_targets'] = {'logic_low_max_V':.8,'logic_high_min_V':2.4,
    'industrial_low_max_V':4,'industrial_high_min_V':7,'continuous_signal_max_V':30}

rbias_min = 4700*.9875
report['bias_resistor'] = {'value_ohm':4700,'package':'2010','rated_power_W':.75,
    'worst_power_at_30V_W':30**2/rbias_min,
    'PNP_off_voltage_at_0.5mA_V':.0005*4700*1.0125,
    'NPN_release_at_10V_0.5mA_V':(10-.45-.0005*4700*1.0125)/(1+4700*1.0125/(240000*.9875))}
assert report['bias_resistor']['PNP_off_voltage_at_0.5mA_V'] < report['input_industrial']['falling_V'][0]
assert report['bias_resistor']['NPN_release_at_10V_0.5mA_V'] > report['input_industrial']['rising_V'][1]

# TPS2553 datasheet equations use R in kohm and return mA.
r5 = 59.0
report['sensor_5v_current_limit'] = {'resistor_kohm':r5,'usable_target_mA':300,
    'minimum_mA':25230/(r5*1.0125)**1.016,
    'maximum_mA':22980/(r5*.9875)**.94}
# TPS1H200A: I_limit=0.8V *2500/R_CL; +/-15% at nominal limits>=0.5A.
rbat=3900
inom=.8*2500/rbat
report['sensor_vbat_current_limit'] = {'resistor_ohm':rbat,'usable_target_mA':300,
    'nominal_mA':1000*inom,'minimum_mA':1000*inom*.85/1.0125,
    'maximum_mA':1000*inom*1.15/.9875,
    'accuracy_condition':'VS-OUT>=2.5V; current-limit accuracy is not specified in the low-dropout region.',
    'latch_delay_nominal_ms':.4+10e-9*1.45/4.5e-6*1000,
    'latch_delay_note':'10nF delay capacitor, no automatic retry. Timing-current/reference are typical values; bench-check actual delay.'}
assert inom/1.0125>=.5
assert report['sensor_5v_current_limit']['minimum_mA'] > 300
assert report['sensor_vbat_current_limit']['minimum_mA'] > 300

# LMR51420 500 kHz reference application, 100k/13.7k output divider.
vnom=.6*(1+100/13.7)
vmin=.6*.985*(1+(100*.998)/(13.7*1.002))
vmax=.6*1.025*(1+(100*1.002)/(13.7*.998))
report['buck']={'output_nominal_V':vnom,'feedback_resistor_initial_tolerance':0.001,'feedback_resistor_total_budget':0.002,'operating_mode':'PFM, system regulation -1.5/+2.5%' ,'dc_reference_and_divider_only_V':[vmin,vmax],
    'inductor_uH':10,'minimum_inductance_uH':8,'minimum_switch_frequency_kHz':450,
    'peak_to_peak_ripple_at_18V_A':vnom*(1-vnom/18)/(8e-6*450e3),
    'required_saturation_current_A':4.2,
    'output_capacitors':'3 x 22 uF, 25 V X5R, Samsung CL31A226KAHNNNE; measured manufacturer typical DC-bias curve stored with sources',
    'minimum_effective_output_capacitance_target_uF':25,
    'max_duty_cycle_check':'Datasheet typical off-time150ns, maximum duty98%, foldback as low as133kHz. At6V input,0.75V diode drop leaves5.25V; nominal4.98V needs94.85% plus conduction loss. Low-input regulation still requires bench characterization.'}
input_a=.3+(vmax*(.3+.15))/((6-.75)*.8)
report['power_budget']={'sensor_vbat_A':.3,'sensor_5V_A':.3,'logic_5V_budget_A':.15,
    'estimated_max_input_A_at_6V_80pct_efficiency':input_a,
    'input_fuse_nominal_A':1.5,
    'AP2112_dissipation_W_at_150mA':(vmax-3.3)*.15,
    'reverse_diode_drop_budget_V':.75,'reverse_diode_dissipation_budget_W':input_a*.75}
report['logic_open_drain']={'pullup_source_min_V':3.3*.97,'bias_diode_drop_budget_V':.45,
 'maximum_off_leakage_target_uA':50,
 'released_signal_min_V':(3.3*.97-.45-50e-6*4700*1.0125)/(1+4700*1.0125/(240000*.9875))}
assert report['logic_open_drain']['released_signal_min_V']>report['input_logic']['rising_V'][1]
report['adc']={'vbat_divider': [100000,10000],
    'vbat_ADC_at_30V_with_1pct_tolerance_V':30*(10000*1.01)/(100000*.99+10000*1.01),
    'sensor5V_divider':[10000,10000],
    'sensor5V_ADC_at_5.25V_with_1pct_tolerance_V':5.25*1.01/2}
report['can']={'clock_Hz':48_000_000,'prescaler':3,'segment1_TQ':13,'segment2_TQ':2,
    'bitrate':48_000_000/(3*(1+13+2)), 'sample_point':(1+13)/16,
    'planned_periodic_frames_per_second':131,
    'pessimistic_bits_per_extended_8byte_frame':160,
    'planned_bus_load_fraction':131*160/1_000_000}
assert report['can']['bitrate']==1_000_000
report['bias_misconfiguration']={'separate_resistors_per_branch':True,
 'port_pullup_resistor_W_at_18V_plus_0p7V_negative_clamp':18.7**2/(4700*.9875),
 'port_pullup_rated_W':.125,'pulldown_rated_W':.75,
 'all_bias_shunts_fitted':'Incorrect input threshold behavior, but each source is current-limited by4.7k. No direct short through a diode.'}
assert report['bias_misconfiguration']['port_pullup_resistor_W_at_18V_plus_0p7V_negative_clamp'] < .125
report['crystal']={'frequency_Hz':8e6,'ESR_max_ohm':200,'C0_max_pF':7,'load_pF':18,
 'gm_critical_mS':4*200*(2*math.pi*8e6)**2*((7+18)*1e-12)**2*1000,
 'MCU_gm_min_mS':10,'startup_margin':10/(4*200*(2*math.pi*8e6)**2*((7+18)*1e-12)**2*1000),
 'load_capacitors_pF':[30,30],'assumed_stray_pF':3,'maximum_drive_uW':100,
 'verification':'Measure startup over voltage and temperature, actual frequency, and crystal drive on first hardware.'}
assert report['crystal']['startup_margin']>5
report['result']='All implemented DC/corner assertions passed; unmodeled limits remain pending.'
(OUT/'calculations.json').write_text(json.dumps(report,indent=2)+'\n')
for key in ('input_logic','input_industrial','sensor_5v_current_limit','sensor_vbat_current_limit','buck','power_budget','can'):
    print(key,json.dumps(report[key]))
