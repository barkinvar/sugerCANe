# Rev H compact layout

This branch reduces the PCB from **52 × 74 mm to 44 × 48 mm**, saving **1,736 mm² (45.1%)**. It retains four copper layers, 1.6 mm thickness and 1.5 mm corner radii. Factory assembly is **50 top + 79 bottom SMT parts**. The user-fitted MCU, ten through-hole parts and three jumper caps are unchanged. Compared with the first 52 × 70 mm compact revision, area falls another 42.0%.

Work is isolated on `codex/compact-board` in `/home/neuro/candi-compact-board`. The original `/home/neuro/candi-clone` checkout stays on its original branch. The baseline is commit `1c03fd1`, a snapshot of the saved Rev H work including the in-progress buck/component review; [snapshot provenance](../reports/compact/source_snapshot.json) records its sources. No original simulation process was stopped or restarted.

[Compare the PCB outlines at the same scale](../output/review/size_comparison.png).

## Geometry and assembly

Sensor terminal pad rows are Y=39 and 46 mm; voltage-header pads are Y=34.4 mm. Mounting holes are at (3.5,4) and (40.5,33) mm, measured from the top-left corner. The power/CAN terminals are at the opposite edge. J8 is now vertical: pin 1 is (16.8,2.5) mm, odd pins run down the left column and even pins down the right column. Electrical pin assignments remain unchanged. D10 is centered at (40,18.5) mm with a 6 mm duct reservation. The conservative connector-body envelope is 44 × 56.1 mm, before wires and access clearance. **The enclosure and harness access must be revised for these positions.**

The buck, boost, protected 12 V output stage and much of the input conditioning move underneath. There are 61 fitted parts on top and 79 underneath. The original large underside illustration gives way to a small wordmark and TERM/GND labels. Enclosure clearance and assembly fixtures must accommodate parts and solder tails on both sides.

The MCU and its original crystal network move together to free signal escape paths. U4 sits underneath the left sensor terminal, with 0.8 mm input and 0.5 mm output connections. Moving C72 beside the lower MCU pins frees the right-edge signal escapes. An unloaded supply branch from the old U4 position is removed; the routed-power DC screen verifies the retained power paths. The 0.18 mm control routing uses the existing fabrication minimum; power and ground widths retain their separate requirements.

C73 moves underneath at (28.325,29.5) mm to free the MCU's lower signal escapes. C62 shifts 0.075 mm right and 0.15 mm upward to keep the adjacent courtyards clear. C70 rotates in place so its eFuse timing connection is direct. Dense signal routing uses 0.50 mm copper / 0.20 mm drilled through vias, retaining a 0.15 mm annulus. This is within [JLCPCB's published multilayer capability](https://jlcpcb.com/capabilities/Capabilities). The native minimum through-hole diameter changes from 0.30 to 0.20 mm; the compact audit permits only this documented project-setting change and checks the actual annular rings. Copper clearances, drill separation and power-width requirements remain in force.

The [layout contract](../hardware/design/layout_contract.json) specifies every footprint pose, side and critical routing transform. [Top assembly](../output/assembly/top_assembly.pdf) and [bottom assembly](../output/assembly/bottom_assembly.pdf) show the finished board. The CPL includes both sides; the factory stencil omits U5's 32 apertures. A new two-sided assembly/reflow quotation is required; the smaller PCB does not establish a lower assembled price.

## Routing and checks

The [routing report](../reports/routing_rules.json) lists the current segment/via inventory and every routed width. Routing uses F.Cu, B.Cu and In2.Cu; In1.Cu remains an unrouted ground plane. Seven In2 keepouts follow the local switching, bootstrap, feedback and compensation copper, preserving an uninterrupted adjacent ground reference. The [critical-copper audit](../reports/compact/layout_verification.json) checks 51 tracks preserved under rigid transforms plus three adjusted tracks and one added track in the reviewed U8.5 repair. At bottom Gerber X=32, Y=−20 mm, the BOOST_SW route now enters the pad centrally instead of grazing its corner. The redundant parallel loop is removed; 0.30 mm pin escapes connect to 0.50 mm inductor/diode legs, with the adjacent In2 ground reference protected. All 11 critical nets remain audited. [Before/after copper detail](../output/review/u8_switch_route_fix.png).

The subsequent [full-board pad-contact sweep](../reports/compact/pad_contact_sweep.json) found two stray contacts from one VIN_PROT branch onto Q1 pin 2. The branch now enters pin 3 directly, retaining its 0.80 mm width and clearing pin 2 by at least 0.216 mm. All 561 native pad/layer shapes and 493 same-net pad/track contact pairs are checked; zero incidental contacts remain. Nineteen connected approach-bend contacts are normal entries into their intended pads. [Q1 before/after detail](../output/review/pad_contact_sweep.png).

Main power distribution and signals are rerouted for the new placement. Circuit values, pad geometry and pin mappings, schematics, custom DRC rules and firmware are unchanged; the project drill-size setting changes as described above.

### Comparison with the completed original-board simulations

The completed `main` design at `6862984` has the same circuit model, power/input simulation harnesses and firmware power logic. Its completed circuit-level SPICE results therefore remain applicable to this variant. They do not model the relocated PCB's switching-loop inductance, ground impedance, coupling or cooling.

The clock and converter feedback routes retain their original geometry under translation or mirroring. BOOST_SW has the separately reviewed pad-entry repair above. Supply routing and ground pours differ. C63/C64 retain their positions relative to the boost IC; C62 is approximately 7.08 mm from its position under a rigid mirror of the original circuit, so the output-capacitor layout is not identical.

The grounding review found that U8.4's bottom copper island originally had only one ground via, 6.86 mm away. An additional **0.50 mm / 0.20 mm ground via at (36.2,22.85) mm** reduces the nearest spacing to **3.07 mm**, without moving a component or changing a routed trace. The original board has a via 0.91 mm from that pin. These are straight-line pad-to-via spacings, not measured return-path lengths or inductances. The compact audit now requires a through via within 3.2 mm in the same filled bottom-copper polygon and the adjacent In2 ground plane; its regression tests reject removal of that return or a via that does not reach those layers.

This change was reviewed from [455e8cb](https://github.com/barkinvar/sugerCANe/commit/455e8cb27c173d665ca2954342671e62ad56bb67) and applied to the newer compact board after the Q1 pad-contact sweep. Both Q1 and U8 contact repairs remain intact. Checks, renders and review packages were regenerated for the combined board; the older branch's generated reports are not used as evidence for this version.

| Routed positive-copper DC screen | Original 52 × 74 mm | Compact 44 × 48 mm |
| --- | ---: | ---: |
| Buck-to-boost drop, defined 1.3 A load case | 51.14 mV | 43.69 mV |
| Boost-to-eFuse drop | 12.30 mV | 6.66 mV |
| Worst sensor positive path at 300 mA | 44.01 mV | 14.04 mV |

These screens use 85 °C copper resistance, nominal 35 µm copper and 20 µm via plating; they exclude ground return, component and connector drops. See the [current DC report](../reports/electrical/order_readiness.json). The smaller board has less copper for heat spreading, especially around the eFuse, although its six required local thermal vias remain. Comparable circuit simulations and passing geometry checks **do not establish identical ripple, temperature or EMC behavior**; those require first-board measurements with the intended loads and enclosure. Manufacturer references: [TPS61085 layout guidance](https://www.ti.com/lit/ds/symlink/tps61085.pdf) and [LMR51430 layout guidance](https://www.ti.com/lit/ds/symlink/lmr51430.pdf).

The following checks passed on the saved compact board:

- Native ERC/DRC: zero violations and zero unconnected pads; model/schematic/PCB parity.
- Strict routing gate and its regression tests: widths, straight 45/90-degree geometry, redundant copper, short jogs and branch shapes.
- Independent Gerber connectivity: no opens, shorts or unassigned copper across four layers and plated barrels.
- Independent Gerber geometry: copper/edge/mount clearance, drill web, annular rings, mask/paste, ground-pour gaps and narrow-neck screening. Existing clearance and screening thresholds were retained; outer ground-pour minimum width increases to 0.30 mm, with small pour clearances removing narrow same-net slots. The In1 minimum also increases to 0.30 mm; In2 remains 0.25 mm. Thermal-spoke width and gap remain unchanged.
- Native constraints, compact preservation audit, manifest/export/BOM/CPL parity and both-side stencil checks.
- Routed-copper DC screen, electrical and component margins, converter-loop screen, all ten input SPICE cases, firmware tests, drivers and the 2027 bridge build.
- Firmware power-monitor replay: four existing completed power traces at four ADC-error corners, using the compact board's updated voltage drop. Exact trace hashes were checked before replay; this did not start new power simulations.

See [release checks](../reports/release_checks.json), [routing evidence](../reports/routing_rules.json), [exported copper review](../output/assembly/gerber_copper_review.pdf), [Gerber geometry](../reports/manufacturing/gerber_geometry.json) and [connectivity](../reports/manufacturing/gerber_connectivity.json).

**Full release remains on HOLD.** The original checkout's power simulations completed without interruption: all nine cases and required timestep/solver repeats pass their screening criteria. Circuit, simulator-script and model hashes match this branch; [completed-evidence provenance](../reports/compact/completed_simulation_sources.json) records the copied reports. The package is for review/quotation only; physical thermal, EMC, assembly, sensor-startup and enclosure-fit qualification remain pending. Passing CAD checks does not establish physical perfection.

## Recheck without starting power simulations

From `current/`, source `tools/env.sh`. Run `kicad-python scripts/test_compact_layout.py`, `kicad-python scripts/check_compact_layout.py`, `kicad-python scripts/check_board_constraints.py`, `python scripts/check_routing.py`, `bash scripts/export_manufacturing.sh`, then the manifest, factory and independent Gerber checks listed in `scripts/validate_release.sh`. Run `python scripts/check_boost_spice.py --verify-report --require-pass`, `python scripts/check_order_readiness.py` and refresh the waveform replay from hash-matching completed traces before `python scripts/write_validation_summary.py`. Factory process confirmation and physical qualification still govern release.

The saved native PCB is authoritative. Layout exploration scripts were used on temporary copies; they must not be reapplied to the final routed board. Pre-compaction routing contact/ground-detail images retained elsewhere are historical; the current four-layer Gerber previews and 3D views depict this variant.
