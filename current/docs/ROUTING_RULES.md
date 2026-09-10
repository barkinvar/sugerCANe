# Routing rules

The saved Rev H PCB uses straight horizontal, vertical and 45° track centerlines. [Routing results](../reports/routing_rules.json) are a required export gate, alongside native DRC and independent Gerber verification.

| Rule | Enforcement |
|---|---|
| No curved tracks or arbitrary directions | Reject PCB arcs and non-octilinear centerlines; 0.00002 mm tolerance covers native coordinate rounding only. |
| No redundant copper segments | Reject exact duplicates, overlapping collinear or offset parallel runs outside contacts, and unnecessary equal-width collinear joints. |
| No tiny free-space jogs | Free segments must be at least 0.10 mm. Short pad/via escapes are permitted only inside the actual contact copper. Expanding a contact by the trace radius is not allowed. |
| Consistent bends | Free bends have an included angle of at least 135°: a 45° change of direction. Transitions within pad/via contact copper are permitted. |
| Explicit branch connections | Free-space branches must meet at shared segment endpoints. The checker also finds taps and crossings inside a segment, so subdivision cannot hide a junction. |
| Chamfered branches | Three-way free-space junctions use 90°/135°/135° sectors; four-way junctions use four 90° sectors. Perpendicular T shapes and acute side taps are rejected outside pad/via contacts. |
| Reviewed track widths | Check every segment against the [width policy](../hardware/design/routing_widths.json). Free-space width changes require an explicit location and engineering reason; stale approvals fail. Contact transitions retain separately sized branches. |
| No disconnected ends | Every endpoint must reach pad/via copper, another trace centerline or an actual filled zone. End-cap overlap alone is rejected. Native `track_dangling` and `via_dangling` checks are errors. Exports require zero DRC violations and zero unconnected items. |
| Preserve electrical requirements | Native net classes, local converter/decoupling path limits, layer restrictions, edge clearances and routed-copper DC-drop limits remain mandatory. |

Same-net branches are normal: several loads must join their supply, and grounds must join the ground network. Different nets crossing on separate copper layers are also normal. Shorts between different nets on the same layer fail clearance/connectivity checks. Rounded copper end caps are normal fabrication geometry; they do not mean the track centerline is curved.

The branch shape is a project layout convention, not evidence that an ordinary T junction would cause a short. Three paths cannot all meet with 135° separation: a Y junction necessarily includes a 90° sector. A route may consist of multiple straight segments, provided its bends and junctions satisfy the rules. [Before/after junction details](../output/review/routing_junctions.png).

From `current/`, with the tool environment loaded:

```sh
source tools/env.sh
python scripts/test_routing.py
python scripts/check_routing.py
kicad-python scripts/check_board_constraints.py
bash scripts/export_manufacturing.sh
```

Both `validate_release.sh` and `export_manufacturing.sh` enforce the routing gate. The validation summary rejects a routing report with an outdated PCB, checker or width-policy hash. Twenty-one routing fixtures cover invalid curves, angles, duplicates, overlaps, tiny jogs, sharp bends, implicit side taps and acute/perpendicular branches, plus contact overshoots, offset parallel overlap, end-cap-only joins, filled-zone entries, valid contacts, chamfered branches, unreviewed widths, layer-specific widths and stale transition approvals. The checks report failures without modifying the board.

Four additional ground-pour fixtures check narrow same-net gaps and thin/wide connections. The same test command also runs six DC-network fixtures. Pad/via contacts and overlaps must remain electrically connected after redundant centerline pieces are removed; real gaps and isolated layers must remain open. The local bypass check counts distance through pad copper without relaxing its path-length limits.

In KiCad, use the straight 45° routing posture. `Ctrl+W` switches straight 45°/90° postures; avoid the curved posture. See the [KiCad PCB Editor manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html).

The compact board uses **1,676 segments and 223 vias**, with a 0.18 mm minimum track width. Its [layout audit](../reports/compact/layout_verification.json) preserves the circuit, DRC settings and 248 critical clock/converter/input-power copper objects from the frozen pre-compaction snapshot. The [cleanup report](../reports/routing_cleanup.json) records the current comparison. Older contact, branch and ground-detail images linked above illustrate the pre-compaction cleanup; the current [four-layer review](../output/assembly/gerber_copper_review.pdf) depicts the compact board.

Existing width limits remain mandatory, including the 0.7 mm VIN_RAW/VIN_FUSED routes and the reviewed narrow local pin/clearance sections. Low-current feedback and enable branches retain their separate width policy. The routed-copper DC screen includes input copper and jumper-to-connector paths using nominal 35 µm copper on all four layers. Width depends on current, permitted drop/heating, copper thickness and route length; voltage also sets required clearance. A DC drop calculation does not establish a thermal rating.

Ground pours retain a 0.25 mm minimum width, solid outer-layer SMT connections, through-hole thermal relief and the original local cutouts. Independent Gerber checks require at least 0.25 mm between separate ground regions. A 0.24 mm erosion screen rejects narrow connections that split substantial ground areas (remaining cores over 0.025 mm²). New ground stitches connect the relocated underside parts and the comparator's local ground pour. Intended thermal slots and ordinary concave corners remain; this is not a ground-return impedance or heating simulation.

In1 has no routed segments and remains a ground plane. In2 carries selected signals and supply routes with ground fill; connector routes stay in the lower board region, and INPUT1 may use the right-hand logic corridor. [Native constraints](../scripts/check_board_constraints.py) enforce those regions and preserve top-only, via-free critical clock and switching paths. Every layer undergoes exported connectivity, clearance and ground-gap/neck checks.

These checks cover CAD geometry and the stated electrical models. The [full-power release HOLD and physical qualification requirements](VALIDATION.md) remain in effect.
