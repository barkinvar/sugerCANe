from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
drc=read('reports/drc/final.json');erc=read('reports/erc/final.json');par=read('reports/design_parity.json');man=read('reports/manufacturing/verification.json');geo=read('reports/manufacturing/gerber_geometry.json');con=read('reports/manufacturing/gerber_connectivity.json');loaded=read('reports/electrical/loaded_input_thresholds.json');ground=read('reports/electrical/ground_return_model.json');pogo=read('reports/programming_geometry.json')
assert not drc['violations'] and not drc['unconnected_items'] and all(not s['violations'] for s in erc['sheets'])
assert par['pass'] and all(q['result']=='PASS' for q in [man,geo,con,loaded,pogo])
lines=['# Rev B-2 validation evidence','', 'These results apply to the supplied Rev B-2 native board and its exported files. They are computational evidence for an unbuilt prototype. Physical soldering, temperature, surge behavior, real sensor/CAN traffic and programming-cable mating remain untested.', '', '| Check | Result | Evidence |','|---|---|---|',
'| Native KiCad 10.0.6 ERC / DRC | No reported violations or unconnected items under the saved project rules | `reports/erc/final.json`, `reports/drc/final.json` |',
f"| Model / schematic / board parity | {par['physical_components']} modeled components, {par['model_pin_count']} model pins, {par['unique_named_nets']} named functional nets; no mismatches | `reports/design_parity.json` |",
f"| Fabrication and assembly parity | Nine graphic layers, {man['plated_drills']} plated and seven nonplated drills, 144 purchased placements and 144 local model assignments | `reports/manufacturing/verification.json` |",
'| Independent copper reconstruction | No shorts, opens or unidentified copper islands | `reports/manufacturing/gerber_connectivity.json` |',
'| Independent manufacturing geometry | Copper clearance, edge/mount spacing, annular rings, hole web, mask/paste checks passed | `reports/manufacturing/gerber_geometry.json` |',
f"| Programming contact geometry | Ten contacts, no paste, minimum foreign trace/via clearance {pogo['minimum_contact_to_foreign_track_or_via_clearance_mm']:.3f} mm versus 0.508 mm requirement | `reports/programming_geometry.json` |",
'| Electrical component corners | 8,192 evaluations in each input mode, power/protection assertions passed | `reports/electrical/calculations.json` |',
'| Ground-loaded input thresholds | All channels and both modes pass 108 supply/load allocations with correlated ground potentials | `reports/electrical/loaded_input_thresholds.json` |',
'| Ground sheet estimate | 0.10 / 0.075 mm meshes, analytic calibration and reciprocity/residual checks | `reports/electrical/ground_return_model.json` |',
'| Boost startup model | Approximately 4.99 V at 420 mA and 462 mA modeled loads | `reports/boost_simulation.json` |',
'| Firmware | Builds for STM32F042; 2,190,989 core assertions plus 19 application fault/startup scenarios pass with sanitizers | `reports/firmware-build.log`, `reports/firmware-tests.log` |',
'| Host / robot drivers | 232,928 Java assertions, 75,828 C++ assertions, five Python tests; WPILib 2026.2.1 compile checks | `reports/driver-tests.log` |', '',
'## Electrical results', '', '| Mode / channel | Rising threshold range (V) | Falling threshold range (V) |','|---|---|---|']
for q in loaded['results']:lines.append(f"| {q['mode'].capitalize()} / {q['channel']} | {q['rising_V'][0]:.3f}–{q['rising_V'][1]:.3f} | {q['falling_V'][0]:.3f}–{q['falling_V'][1]:.3f} |")
worst=max(q['to_input_ground_ohm'] for q in ground['results'][-1]['routes'])
lines+=['',f"The fine-grid estimate gives a worst sensor-ground-to-input-ground resistance of {worst*1000:.2f} mΩ at 85 °C copper temperature. The maximum route change between the last two meshes is {ground['maximum_route_change_fraction']*100:.2f}%. Loaded-threshold analysis inflates the modeled ground potentials by 15%, tests both rail load extremes at all port allocations and uses 5, 12 and 22 V inputs. It includes a conservative 150 mA logic allocation and 80% conversion-efficiency assumptions. Switching-frequency ground bounce, external wiring drop and hardware tolerances outside the stated allowances are not represented.", '',
'The nominal 5 V output budget includes the converter minimum, actual routed positive-trace resistance, 135 mΩ switch resistance and 100 mΩ for contact/shunt/ground allowance. Its estimated minimum is approximately 4.75 V at a port carrying the whole 300 mA shared load. The input calculation uses 110 mΩ for trace/connector/return allowance in addition to the fuse and MOSFET. These are budgets requiring measurement, not production limits.', '',
'The boost runs use TI’s typical transient model and a finite-resistance upstream source. The 3.80 V / 462 mA case reports 4.990 V average, about 3.1 mV modeled steady-state ripple and 0.753 A peak inductor current. It does not establish stability of the complete cascaded converters or thermal performance. The original vendor model, syntax adaptation, decks, sampled data and plots are included.', '',
'## Interpretation and configured checks', '',
'Native DRC keeps clearance, connectivity, courtyard overlap, holes, mask and silkscreen checks enabled. Informational/model-category checks disabled in the project are: '+', '.join(q['key'] for q in drc['ignored_checks'])+'. Native ERC disables: '+', '.join(q['key'] for q in erc['ignored_checks'])+'. The separate parity and fabrication checks complement these settings. No clearance or unconnected-net violation is waived.', '',
'Excellon output rounds coordinates and diameters to 0.001 mm. The independent audit accepts at most half that unit and records the actual rounding error. Gerbonara reports KiCad’s G90 header-placement warning; drill positions, diameters and plating types still match. Polygon arc approximation is 1 µm; reported annular-ring minima are interpreted within that numerical tolerance.', '',
'Firmware occupies 7,148 bytes of flash and 1,832 bytes of RAM including the reserved stack allocation. Host tests execute the application with controlled peripheral substitutes; they do not emulate all STM32 electrical behavior. The fourth protocol slot remains reserved and zero on this three-channel board. Actual SWD flashing, roboRIO traffic, fault currents and sustained timing must be checked on hardware.', '',
'Historical draft reports and routing experiments in the development workspace may contain failures. The delivery archive includes the final reports identified here. Complete `docs/QUALIFICATION.md` before promoting the design from prototype to a qualified product.','']
(R/'docs/VALIDATION.md').write_text('\n'.join(lines))
with (R/'docs/VALIDATION.md').open('a') as f:
    f.write('''

## B-2 variant and assembly checks

`reports/variant_verification.json` checks the frozen horizontal Rev B signature against B-2. Copper tracks, vias, filled zones, footprint positions and pad geometry are identical. Firmware source/header files and delivered ELF/HEX/BIN hashes are identical. The existing firmware and robot-driver tests are inherited on that basis; these are not physical factory tests.

The schematic, native DRC/ERC, Gerbers, drill/placement parity, ground model and loaded input-threshold checks were regenerated for B-2. Exactly 49 fitted MPNs change (37 resistors and 12 capacitors); their values, tolerances and circuit connections remain fixed, and the capacitors' voltage rating increases. `PART_CHANGES.md` records the specification review.

`reports/factory_placement.json` verifies the 144-reference BOM/CPL mapping, coordinates, and six horizontal connector drill patterns. There are 128 SMT parts/338 solder joints and 16 THT parts/65 solder joints. The CPL uses a lower-left origin and explicit through-hole body-center offsets. Factory library rotation, rail/tab design, sourcing and build-process approval have not been performed by a supplier.
''')
