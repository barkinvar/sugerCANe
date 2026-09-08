# Rev B-2 validation evidence

These results apply to the supplied Rev B-2 native board and its exported files. They are computational evidence for an unbuilt prototype. Physical soldering, temperature, surge behavior, real sensor/CAN traffic and programming-cable mating remain untested.

| Check | Result | Evidence |
|---|---|---|
| Native KiCad 10.0.6 ERC / DRC | No reported violations or unconnected items under the saved project rules | `reports/erc/final.json`, `reports/drc/final.json` |
| Model / schematic / board parity | 154 modeled components, 403 model pins, 87 named functional nets; no mismatches | `reports/design_parity.json` |
| Fabrication and assembly parity | Nine graphic layers, 307 plated and seven nonplated drills, 144 purchased placements and 144 local model assignments | `reports/manufacturing/verification.json` |
| Independent copper reconstruction | No shorts, opens or unidentified copper islands | `reports/manufacturing/gerber_connectivity.json` |
| Independent manufacturing geometry | Copper clearance, edge/mount spacing, annular rings, hole web, mask/paste checks passed | `reports/manufacturing/gerber_geometry.json` |
| Programming contact geometry | Ten contacts, no paste, minimum foreign trace/via clearance 0.751 mm versus 0.508 mm requirement | `reports/programming_geometry.json` |
| Electrical component corners | 8,192 evaluations in each input mode, power/protection assertions passed | `reports/electrical/calculations.json` |
| Ground-loaded input thresholds | All channels and both modes pass 108 supply/load allocations with correlated ground potentials | `reports/electrical/loaded_input_thresholds.json` |
| Ground sheet estimate | 0.10 / 0.075 mm meshes, analytic calibration and reciprocity/residual checks | `reports/electrical/ground_return_model.json` |
| Boost startup model | Approximately 4.99 V at 420 mA and 462 mA modeled loads | `reports/boost_simulation.json` |
| Firmware | Builds for STM32F042; 2,190,989 core assertions plus 19 application fault/startup scenarios pass with sanitizers | `reports/firmware-build.log`, `reports/firmware-tests.log` |
| Host / robot drivers | 232,928 Java assertions, 75,828 C++ assertions, five Python tests; WPILib 2026.2.1 compile checks | `reports/driver-tests.log` |

## Electrical results

| Mode / channel | Rising threshold range (V) | Falling threshold range (V) |
|---|---|---|
| Logic / 1 | 1.569–2.261 | 0.937–1.447 |
| Logic / 2 | 1.496–2.240 | 0.863–1.425 |
| Logic / 3 | 1.529–2.240 | 0.896–1.425 |
| Industrial / 1 | 5.349–6.784 | 4.715–5.966 |
| Industrial / 2 | 5.336–6.779 | 4.702–5.961 |
| Industrial / 3 | 5.215–6.778 | 4.581–5.959 |

The fine-grid estimate gives a worst sensor-ground-to-input-ground resistance of 20.28 mΩ at 85 °C copper temperature. The maximum route change between the last two meshes is 2.43%. Loaded-threshold analysis inflates the modeled ground potentials by 15%, tests both rail load extremes at all port allocations and uses 5, 12 and 22 V inputs. It includes a conservative 150 mA logic allocation and 80% conversion-efficiency assumptions. Switching-frequency ground bounce, external wiring drop and hardware tolerances outside the stated allowances are not represented.

The nominal 5 V output budget includes the converter minimum, actual routed positive-trace resistance, 135 mΩ switch resistance and 100 mΩ for contact/shunt/ground allowance. Its estimated minimum is approximately 4.75 V at a port carrying the whole 300 mA shared load. The input calculation uses 110 mΩ for trace/connector/return allowance in addition to the fuse and MOSFET. These are budgets requiring measurement, not production limits.

The boost runs use TI’s typical transient model and a finite-resistance upstream source. The 3.80 V / 462 mA case reports 4.990 V average, about 3.1 mV modeled steady-state ripple and 0.753 A peak inductor current. It does not establish stability of the complete cascaded converters or thermal performance. The original vendor model, syntax adaptation, decks, sampled data and plots are included.

## Interpretation and configured checks

Native DRC keeps clearance, connectivity, courtyard overlap, holes, mask and silkscreen checks enabled. Informational/model-category checks disabled in the project are: missing_courtyard, track_not_centered_on_via, tuning_profile_track_geometries, footprint_filters_mismatch, footprint_type_mismatch. Native ERC disables: single_global_label, four_way_junction, simulation_model_issue, footprint_filter. The separate parity and fabrication checks complement these settings. No clearance or unconnected-net violation is waived.

Excellon output rounds coordinates and diameters to 0.001 mm. The independent audit accepts at most half that unit and records the actual rounding error. Gerbonara reports KiCad’s G90 header-placement warning; drill positions, diameters and plating types still match. Polygon arc approximation is 1 µm; reported annular-ring minima are interpreted within that numerical tolerance.

Firmware occupies 7,148 bytes of flash and 1,832 bytes of RAM including the reserved stack allocation. Host tests execute the application with controlled peripheral substitutes; they do not emulate all STM32 electrical behavior. The fourth protocol slot remains reserved and zero on this three-channel board. Actual SWD flashing, roboRIO traffic, fault currents and sustained timing must be checked on hardware.

Historical draft reports and routing experiments in the development workspace may contain failures. The delivery archive includes the final reports identified here. Complete `docs/QUALIFICATION.md` before promoting the design from prototype to a qualified product.


## B-2 variant and assembly checks

`reports/variant_verification.json` checks the frozen horizontal Rev B signature against B-2. Copper tracks, vias, filled zones, footprint positions and pad geometry are identical. Firmware source/header files and delivered ELF/HEX/BIN hashes are identical. The existing firmware and robot-driver tests are inherited on that basis; these are not physical factory tests.

The schematic, native DRC/ERC, Gerbers, drill/placement parity, ground model and loaded input-threshold checks were regenerated for B-2. Exactly 49 fitted MPNs change (37 resistors and 12 capacitors); their values, tolerances and circuit connections remain fixed, and the capacitors' voltage rating increases. `PART_CHANGES.md` records the specification review.

`reports/factory_placement.json` verifies the 144-reference BOM/CPL mapping, coordinates, and six horizontal connector drill patterns. There are 128 SMT parts/338 solder joints and 16 THT parts/65 solder joints. The CPL uses a lower-left origin and explicit through-hole body-center offsets. Factory library rotation, rail/tab design, sourcing and build-process approval have not been performed by a supplier.
