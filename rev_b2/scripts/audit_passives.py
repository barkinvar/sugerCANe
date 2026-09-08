"""Document why each capacitor is fitted; do not infer removability from net names."""
from pathlib import Path
import json, csv
R=Path(__file__).resolve().parents[1]
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
groups=[
 ('C1 C2 C3','Battery/input filtering','Keep','Bulk input energy and local high-frequency input bypass; the remote bulk capacitor does not replace the bypass at U1.','LMR51420 datasheet sections 9.2.2.6, 10 and 11'),
 ('C4 C5 C13','Buck output reservoir','Keep; C13 is a bench optimization candidate','Three 22uF capacitors compensate for effective capacitance loss. The nominal 66uF is not a claim of 66uF effective capacitance. Removing C13 requires DC-bias, load-transient and cascaded-regulator stability verification.','LMR51420 datasheet Table 9-1 and section 9.2.2.5'),
 ('C6','Buck bootstrap','Keep','Provides the high-side MOSFET gate-drive supply; it is not an extra rail decoupler.','LMR51420 sections 8.3 and 9.2.2.7'),
 ('C7 C8','3.3V regulator input/output','Keep','Local input bypass and output capacitance support the LDO and its transient response.','AP2112 recommended input/output application capacitors'),
 ('C9 C10','Battery sensor switch bypass/output','Keep','Local switch input bypass and controlled sensor-rail output capacitance; included in the inrush budget.','TPS1H200A-Q1 application guidance and Rev B-2 startup budget'),
 ('C11 C12','5V sensor switch bypass/output','Keep','Input bypass and output charge reservoir reduce disturbances as sensor loads change.','TPS2553 sections on input/output capacitance and layout'),
 ('C14','Hardware fault timing','Keep','Sets the battery-switch current-limit latch delay; deleting it changes fault behavior.','TPS1H200A-Q1 latch-off mode'),
 ('C15 C16 C17','Boost output reservoir/bypass','Keep','The two 22uF capacitors supply the modeled boost output capacitance; 100nF provides local high-frequency bypass.','TPS61322 output-capacitor selection and supplied startup decks'),
 ('C20 C21 C22 C23','Microcontroller supply bypass','Keep','Separate local bypass at digital, I/O and analog supply connections. Shared net names do not make physically separated decouplers redundant.','STM32F042 power-supply scheme'),
 ('C24','Microcontroller local bulk','Keep; bench optimization candidate','Provides a local charge reservoir beyond the three small supply bypass capacitors. Possible reduction depends on measured rail transients and layout impedance.','STM32F042 power-supply scheme and board layout'),
 ('C25 C26','Crystal load','Keep','Set the external crystal load capacitance and affect oscillator startup/frequency.','Abracon ABM3B 18pF load and STM32 oscillator design'),
 ('C27','Reset filtering','Keep','Suppresses short reset-pin disturbances; removal needs reset/noise qualification.','STM32F042 reset application circuit'),
 ('C28 C29','Supply measurement filtering','Keep','Together with ADC resistor dividers, filter switched-rail measurements used for fault decisions.','Rev B-2 rail diagnostics and ADC sampling implementation'),
 ('C40 C41','CAN supply bypass','Keep','U6 has separate VCC and VIO supply pins. TI calls for local bypass at both even when both use 3.3V.','TCAN3413 datasheet section 8.4'),
 ('C42','CAN local bulk','Keep; bench optimization candidate','Extra local energy reservoir. It is not a substitute for C40/C41 and is not independently proven necessary by DC checks.','TCAN3413 power supply/layout guidance'),
 ('C50','Comparator supply bypass','Keep','Prevents supply disturbances causing false sensor transitions.','LM339LV power-supply recommendations'),
 ('C101 C201 C301','Sensor input filtering','Keep','Each capacitor filters its own divided input; reducing it changes noise rejection and pulse response.','Rev B-2 front-end timing and hysteresis model'),
]
rows=[]
for refs,role,decision,reason,source in groups:
 for ref in refs.split():
  c=parts[ref]
  rows.append(dict(reference=ref,value=c['value'],role=role,decision=decision,reason=reason,source=source))
assert {r['reference'] for r in rows}=={k for k,c in parts.items() if c['kind'] in ['C','CP']}
report={'capacitor_count':len(rows),'decision':'Retain all fitted capacitors for this unbuilt prototype. C13/C24/C42 are optimization candidates, not approved deletions.', 'rows':rows}
(R/'reports/electrical/passive_audit.json').write_text(json.dumps(report,indent=2)+'\n')
with (R/'bom/capacitor_audit.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines=['# Why the small components are fitted','',f'This design has {len(rows)} capacitors. They are not all interchangeable filtering capacitors, and the present count is not proven to be the absolute minimum. This audit retains them until a reduction has measurement evidence.','',
'| References | Job | Decision |','|---|---|---|']
for refs,role,decision,reason,source in groups:lines.append(f'| {refs} | {role} | {decision} |')
lines += ['', 'Several 100 nF capacitors share a supply net because they sit beside different chips or supply pins. Copper traces have inductance: one distant large capacitor cannot supply every fast local current pulse. Other capacitors are part of the converter, crystal, fault timer or input filter rather than rail bypass.', '',
'C13, C24 and C42 are candidates for a measured reduction experiment. Test supply extremes, both sensor rails loaded, startup, load steps, ripple, CAN traffic, reset behavior and temperature before approving their removal. No capacitor has been removed on the basis of appearance or a DC continuity check.', '',
'Most small resistors set input thresholds/hysteresis, sensor pull-up or pull-down current, regulator output voltage, fault current limits, safe enable states, ADC scaling or LED current. Many small black parts in the render are resistors, not capacitors. A factory-assembly variant can use lower-cost stocked equivalents without deleting these functions.', '',
'The larger simplification opportunities are the input-configuration network and the two-stage 5 V supply architecture. These require a circuit redesign and validation; changing to smaller package sizes alone does not remove their functions. See capacitor_audit.csv in the BOM folder for every capacitor and its reason.','']
(R/'docs/PASSIVE_REVIEW.md').write_text('\n'.join(lines))
print('Audited',len(rows),'capacitors; no unsupported removals.')
