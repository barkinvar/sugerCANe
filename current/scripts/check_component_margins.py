"""Independent datasheet screens for the upstream buck and crystal margins.

These calculations expose assumptions; they are not vendor transient models.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math

R = Path(__file__).resolve().parents[1]
parts = json.loads((R / 'hardware/design/circuit.json').read_text())['parts']
electrical = json.loads((R / 'reports/electrical/electrical_checks.json').read_text())
assert parts['U1']['mpn'] == 'LMR51430XDDCR'
assert parts['L1']['value'] == '8.2uH' and parts['L1']['mpn'] == 'SRP7028A-8R2M'
assert parts['U5']['mpn'] == 'STM32F042K6T6'
assert parts['Y1']['mpn'] == 'ABM3B-8.000MHZ-B2-T'
assert parts['R20']['value'] == '0'
assert parts['C25']['value'] == parts['C26']['value'] == '20pF'

# TI SLUSEF4A tables 7.5 / 9.1: both peak AND valley limits matter.
# A converter's nominal 2 A rating alone does not establish fault headroom.
power = electrical['power']
vout = electrical['buck']['with_40mV_regulation_budget_V'][1]
def buck_rows(inductance, valley_limit, peak_limit):
    rows = []
    for vin in [power['protected_input_at_6V_V'], 12., 22.]:
        ripple_min = vout * (1 - vout / vin) / (inductance * 1.2 * 560e3)
        ripple_max = vout * (1 - vout / vin) / (inductance * .8 * 450e3)
        for condition, load in [('normal', power['buck_normal_output_A']),
                                ('12V_max_charging_5V_normal', power['boost_fault_input_budget_A'] + .3 + power['logic_allowance_A']),
                                ('both_limiters_max', power['buck_both_limiters_max_plus_logic_A'])]:
            valley = load - ripple_min / 2
            peak = load + ripple_max / 2
            rows.append(dict(protected_input_V=vin, condition=condition,
                             output_load_A=load, worst_valley_A=valley, worst_peak_A=peak,
                             valley_limit_min_A=valley_limit, peak_limit_min_A=peak_limit,
                             inductor_rms_A=math.sqrt(load**2 + ripple_max**2 / 12),
                             below_both_minimum_limits=valley < valley_limit and peak < peak_limit))
    return rows
rows = buck_rows(8.2e-6, 2.75, 3.67)
previous_rows = buck_rows(10e-6, 1.7, 2.7)
normal_pass = all(row['below_both_minimum_limits'] for row in rows if row['condition'] == 'normal')
assert normal_pass and all(row['below_both_minimum_limits'] for row in rows)
assert max(row['inductor_rms_A'] for row in rows) < 4.0
assert 7.5 > 6.68  # Published L1 saturation rating versus U1 maximum peak limit.
nominal_ripple = electrical['buck']['nominal_V'] * (1 - electrical['buck']['nominal_V'] / 22) / (8.2e-6 * 500e3)
assert .2 < nominal_ripple / 3 < .6  # TI section 9.2.2.4 design range at maximum application input.
capacitive_ripple = power['buck_peak_ripple_at22V_A'] / (8 * 450e3 * electrical['capacitors']['budgeted_bank_uF'] * 1e-6)
assert capacitive_ripple < .03

# ST DS10009 table 36 + AN2867: gmcrit = 4 ESR w^2 (C0 + CL)^2.
# Abracon ABM3B revision U: max ESR 200 ohm at 8 MHz; max C0 7 pF.
# 3 pF is the original CL=18 pF design assumption; 10 pF is ST's rough
# combined pin/PCB estimate. Neither is a measurement of this board.
oscillator = []
for stray, tolerance in itertools.product([3., 5., 10.], [-.05, .05]):
    load_pF = 20 * (1 + tolerance) / 2 + stray
    gmcrit = 4 * 200 * (2 * math.pi * 8e6) ** 2 * ((7 + load_pF) * 1e-12) ** 2
    oscillator.append(dict(assumed_stray_pF=stray, capacitor_tolerance=tolerance,
                           effective_load_pF=load_pF, gmcrit_mA_per_V=1000 * gmcrit,
                           gm_min_mA_per_V=10., gain_margin=.010 / gmcrit,
                           exceeds_ST_gain_margin_5=.010 / gmcrit > 5))
maximum_stray = math.sqrt(.010 / (5 * 4 * 200 * (2 * math.pi * 8e6) ** 2)) * 1e12 - 7 - 20 * 1.05 / 2
assert all(row['exceeds_ST_gain_margin_5'] for row in oscillator)
report = dict(
    result='PASS buck current-limit, inductor and crystal gain screens; physical qualification pending',
    sources=[
        dict(url='https://www.ti.com/lit/ds/symlink/lmr51430.pdf', section='SLUSEF4A tables 7.5, 9.1; sections 8.3.6 and 9.2.2'),
        dict(url='https://www.ti.com/lit/ds/symlink/lmr51420.pdf', section='SLUSEF6C table 7.5; previous-part comparison only'),
        dict(url='https://www.bourns.com/docs/product-datasheets/srp7028a.pdf', section='June 2024 electrical table and inductance/current curves'),
        dict(url='https://www.st.com/resource/en/datasheet/stm32f042t6.pdf', section='DS10009 Rev 5 table 36 and crystal loading guidance'),
        dict(url='https://www.st.com/resource/en/application_note/cd00221665.pdf', section='AN2867 critical transconductance and gain margin'),
        dict(url='https://abracon.com/Resonators/abm3b.pdf', section='ABM3B Rev U electrical specifications')],
    buck=dict(corners=rows, normal_load_pass=normal_pass,
              all_current_limit_corners_pass=True,
              previous_design=dict(mpn='LMR51420XDDCR',inductor_mpn='SRP7028A-100M',corners=previous_rows),
              inductor=dict(mpn='SRP7028A-8R2M',inductance_uH=8.2,tolerance_fraction=.2,
                            RMS_rating_A=4.,saturation_rating_A=7.5,maximum_DCR_ohm=.068,
                            buck_maximum_peak_limit_A=6.68,nominal_ripple_ratio_at22V=nominal_ripple/3,
                            worst_capacitive_ripple_V=capacitive_ripple,
                            scope='Published ratings; saturation is the specified inductance-drop point, not a hot guarantee. Ripple calculation excludes capacitor ESR/ESL and control-loop transients.'),
              simultaneous_faults_regulation_guaranteed=False,
              interpretation='The original 2 A buck failed minimum-current-limit headroom at the low-input maximum-charging corner and some simultaneous-fault corners. The 3 A buck with 8.2 uH L1 passes all nine current-limit corners. This does not establish dropout, source-impedance, closed-loop or thermal behavior; fault-free MCU/CAN operation still requires bench qualification.'),
    oscillator=dict(corners=oscillator, maximum_stray_pF_for_gain_margin_5=maximum_stray,
                    fitted_capacitors_pF=20, previous_capacitors_pF=30,
                    crystal_specified_load_pF=18, all_gain_corners_pass=True,
                    previous_gain_at_10pF_stray_and_max_caps=4.612620169021409,
                    interpretation='20 pF capacitors exceed gain margin 5 at all stated stray/tolerance corners, including the former failing 10 pF stray corner. Actual stray capacitance, frequency pulling, drive and startup remain unmeasured. R20 permits drive adjustment on the prototype.'),
    input_hashes={name: hashlib.sha256((R / name).read_bytes()).hexdigest() for name in [
        'hardware/design/circuit.json', 'hardware/FRC_Sensor_CAN.kicad_pcb',
        'reports/electrical/electrical_checks.json', 'scripts/check_component_margins.py']},
    limitations='No switching simulation of the upstream buck; the downstream simulations retain an idealized upstream source. No extracted crystal parasitics, motional parameters, oscillator silicon model, drive-level or board thermal measurements. Calculations use the stated component and engineering bounds; current-limit headroom alone is not a transient/dropout guarantee.')
(R / 'reports/electrical/component_margins.json').write_text(json.dumps(report, indent=2) + '\n')
print(report['result'])
print('Maximum modeled stray capacitance for crystal gain margin 5:', round(maximum_stray, 3), 'pF')
