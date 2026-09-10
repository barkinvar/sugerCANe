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
| No incidental pad contacts | A passing same-net trace must not graze a pad corner. A connected bend immediately leading into that pad is valid; a remote connection elsewhere on the net does not excuse the contact. All native pad/track copper layers are scanned. |
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

Both `validate_release.sh` and `export_manufacturing.sh` enforce the routing gate. The validation summary rejects a routing report with an outdated PCB, checker or width-policy hash. Twenty-six routing fixtures cover invalid curves, angles, duplicates, overlaps, tiny jogs, sharp bends, implicit side taps and acute/perpendicular branches, plus contact overshoots, offset parallel overlap, end-cap-only joins, filled-zone entries, valid contacts, chamfered branches, unreviewed widths, layer-specific widths and stale transition approvals. Five additional fixtures cover passing pad grazes, independent pad entries, connected approach bends, remote connections and layer isolation. The checks report failures without modifying the board.

Four additional ground-pour fixtures check narrow same-net gaps and thin/wide connections. The same test command also runs six DC-network fixtures. Pad/via contacts and overlaps must remain electrically connected after redundant centerline pieces are removed; real gaps and isolated layers must remain open. The local bypass check counts distance through pad copper without relaxing its path-length limits.

In KiCad, use the straight 45° routing posture. `Ctrl+W` switches straight 45°/90° postures; avoid the curved posture. See the [KiCad PCB Editor manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html).

The 44 × 48 mm compact board uses 0.18 mm low-current logic, monitor, bias and control traces, retaining the native 0.18 mm fabrication minimum and 0.20 mm general clearance. CAN and +3V3 remain 0.25 mm; power, ground and local converter/clock copper have separate width rules. Protected 5 V and 12 V distribution use 0.5 mm traces. Its [layout audit](../reports/compact/layout_verification.json) checks unchanged circuit and pad geometry, the documented 0.20 mm minimum drill setting, at least 0.15 mm via annulus and 51 preserved critical clock/converter copper objects plus four exact adjusted/added U8.5 repair objects across 11 nets. Two location-specific 0.30/0.50 mm transitions preserve clearance at the centered U8.5 connection. Main power and signal interconnects are rerouted for the new placement. The [routing report](../reports/routing_rules.json) gives the current segment/via inventory and width audit. Older contact, branch and ground-detail images linked above illustrate the pre-compaction cleanup; the current [four-layer review](../output/assembly/gerber_copper_review.pdf) depicts this compact board.
