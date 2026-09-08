**Design sources and regeneration boundaries**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

`circuit.py` is the explicit electrical model: exact pins, nets, values, footprints and selected MPNs. It generates `circuit.json`. `scripts/generate_schematic.py` creates the root and eight child sheets, project symbols and documentation fields. `scripts/sync_pcb_metadata.py` updates component values/metadata in the existing PCB without rerouting. `scripts/check_design_parity.py` compares the model, KiCad-exported schematic netlist and physical pads.

The routed native `hardware/FRC_Sensor_CAN.kicad_pcb` is the **physical layout authority**. The placement/router/refinement scripts record how this prototype was developed. They are not a single deterministic command that reconstructs every later manual route and silkscreen refinement. In particular, `generate_pcb.py` creates an initial placed board, and historical refinement scripts can overwrite newer routing if run blindly. Do not run them on the final board as part of ordinary validation.

Use `scripts/validate_release.sh` for supported regeneration/checking of the current design. It preserves the native PCB and schematic, refreshes exports/BOM/reports, and fails if their electrical content disagrees with the circuit model. Metadata synchronization is a separate deliberate edit. Historical board snapshots remain in the development workspace for audit/recovery and are excluded from the compact release package. All footprints and 161 fitted-component STEP model assignments resolve within `hardware/library`; no global KiCad library path is required to open the finished project.
