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

The current board uses **1,530 segments and 242 vias**, with a 0.18 mm minimum track width. The preceding all-layer pass removed pad overshoots, tiny stair steps, duplicate loops, overlapping routes and an unnecessary ground stub. Connections now reach real pad/via copper or shared trace endpoints. Eleven remaining free centerline ends enter verified filled ground copper. Three redundant signal vias were removed: each now coincides with a same-layer bend and served no layer transition. [Before/after contact details](../output/review/routing_contacts.png).

The preceding width review covered all 77 routed nets and widened 68 segments without narrowing any. That width policy remains enforced. There are now 13 shared-endpoint width junctions: seven at contacts and six documented free transitions. The extra explicit contact junction reflects the new routing representation. Historical [width details](../output/review/routing_widths.png), the current per-net [routing results](../reports/routing_rules.json), and the [cleanup report](../reports/routing_cleanup.json) record both passes.

Intentional narrow sections include the 3.3 V programming-reference branch around J8, the boost IC pin approach, constrained 5 V sensor-power sections, and the LED data routes on inner/bottom copper. Low-current feedback/enable branches can be narrower than their supply trunks. The internal 5 V route retains a 0.81 mm-long, 0.48 mm-wide clearance neck and the previously consolidated 0.9895 mm bottom section. Widening the constrained paths without moving them would violate the existing 0.2 mm clearance rule. Fresh routed-copper DC screening remains within the existing limits.

The latest ground-pour pass raises the pour minimum width to 0.25 mm and adds a 0.25 mm native ground-pad connection rule. Outer layers use solid SMT ground connections and thermal relief for through-hole pads. Five local pour cutouts retreat opposing tips; J8.7 uses diagonal thermal spokes. Three redundant GND segments crossing J6.2's thermal slot were removed. The [native comparison](../reports/routing_cleanup.json) preserves every other object, including component/pad positions, all 242 vias, signal/power tracks, outline, stackup and markings. Copper fills and renders were regenerated. Segment count measures geometric representation; it is not a measure of electrical performance.

Independent Gerber checks now require at least 0.25 mm between separate ground regions, even when vias connect them elsewhere. A 0.24 mm erosion screen rejects narrow connections that split substantial ground areas (remaining cores over 0.025 mm²). Native minimum-width rules, local tip review and the [before/after ground details](../output/review/ground_pours.png) complement this screen. Intended thermal slots and ordinary concave corners remain; this is not a ground-return impedance or heating simulation.

These checks cover CAD geometry and the stated electrical models. The existing [full-power release HOLD and physical qualification requirements](VALIDATION.md) remain in effect.
