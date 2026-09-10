# Rev H compact layout

This branch reduces the PCB from **52 × 74 mm to 52 × 70 mm**, saving **208 mm² (5.4%)**. It retains four copper layers, 1.6 mm thickness and 1.5 mm corner radii. Factory assembly is now **114 top + 15 bottom SMT parts**. The user-fitted MCU, ten through-hole parts and three jumper caps are unchanged.

Work is isolated on `codex/compact-board` in `/home/neuro/candi-compact-board`. The original `/home/neuro/candi-clone` checkout stays on its original branch. The baseline is commit `1c03fd1`, a snapshot of the saved Rev H work including the in-progress buck/component review; [snapshot provenance](../reports/compact/source_snapshot.json) records its sources. No original simulation process was stopped or restarted.

## Geometry and assembly

The sensor terminals and voltage headers move 4 mm toward the center. Sensor terminal pad rows are Y=61 and 68 mm; voltage-header pads are Y=56.4 mm. Mounting holes stay at (3.5, 4) and (48.5, 46.5) mm, measured from the top-left corner. The power/CAN terminals, service socket, LED/duct space and power stages retain their positions. The nominal connector-body envelope becomes 52 × 78.1 mm, before wires and access clearance.

The underside parts are C101; Q101/Q102, Q201/Q202, Q301/Q302; R111/R112, R210/R211/R212, R311/R312; and R52. The bias transistors lie between the sensor-terminal pin rows. The artwork is resized to clear the added components. Enclosure clearance must accommodate components and solder tails on both sides.

The [layout contract](../hardware/design/layout_contract.json) specifies dimensions, sides and key rows. [Top assembly](../output/assembly/top_assembly.pdf) and [bottom assembly](../output/assembly/bottom_assembly.pdf) show the finished board. The CPL includes both sides; the factory stencil omits U5's 32 apertures and retains 289 top plus 36 bottom apertures. A new two-sided assembly/reflow quotation is required; the smaller PCB is not evidence of a lower assembled price.

## Routing and checks

There are **1,676 straight track segments and 223 through vias**. Routing uses top, bottom and selected In2 tracks; In1 remains the ground plane. Connector signal and supply routes on In2 stay below Y=52 mm. INPUT1 may also use the right-hand logic corridor (X≥30 mm), clear of the left-side power stage. Critical clock, converter and input-power copper is preserved exactly: [248 tracks/vias on 15 critical nets](../reports/compact/layout_verification.json). Circuit values, pin mappings, schematics, native DRC rules and firmware are unchanged.

The following checks passed on the saved compact board:

- Native ERC/DRC: zero violations and zero unconnected pads; model/schematic/PCB parity.
- Strict routing gate and its regression tests: widths, straight 45/90-degree geometry, redundant copper, short jogs and branch shapes.
- Independent Gerber connectivity: no opens, shorts or unassigned copper across four layers and plated barrels.
- Independent Gerber geometry: copper/edge/mount clearance, drill web, annular rings, mask/paste, ground-pour gaps and narrow-neck screening. Existing clearance and width thresholds were retained.
- Native constraints, compact preservation audit, manifest/export/BOM/CPL parity and both-side stencil checks.
- Routed-copper DC screen, electrical and component margins, converter-loop screen, all ten input SPICE cases, firmware tests, drivers and the 2027 bridge build.
- Firmware power-monitor replay: four existing completed power traces at four ADC-error corners, using the compact board's updated voltage drop. Exact trace hashes were checked before replay; this did not start new power simulations.

See [release checks](../reports/release_checks.json), [routing evidence](../reports/routing_rules.json), [exported copper review](../output/assembly/gerber_copper_review.pdf), [Gerber geometry](../reports/manufacturing/gerber_geometry.json) and [connectivity](../reports/manufacturing/gerber_connectivity.json).

**Full release remains on HOLD.** The long combined power-startup simulations in the original checkout are unresolved in this snapshot. Completed standalone power evidence is retained with its original provenance. The package is for review/quotation only; physical thermal, EMC, assembly, sensor-startup and enclosure-fit qualification remain pending. Passing CAD checks does not establish physical perfection.

## Recheck without starting power simulations

From `current/`, source `tools/env.sh`. Run `kicad-python scripts/check_compact_layout.py`, `kicad-python scripts/check_board_constraints.py`, `python scripts/check_routing.py`, `bash scripts/export_manufacturing.sh`, then the manifest, factory and independent Gerber checks listed in `scripts/validate_release.sh`. Run `python scripts/check_order_readiness.py --allow-incomplete` and refresh the waveform replay from hash-matching completed traces before `python scripts/write_validation_summary.py --allow-incomplete`. That mode preserves the release HOLD; it does not approve missing simulation cases.

The saved native PCB is authoritative. Retained copper remains locked against automatic rerouting; unlock deliberately before editing those paths. Layout exploration scripts were used on temporary copies; they must not be reapplied to the final routed board. Pre-compaction routing contact/ground-detail images retained elsewhere are historical; the current four-layer Gerber previews and 3D views depict this variant.
