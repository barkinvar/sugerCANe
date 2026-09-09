# Routing rules

The saved Rev H PCB uses straight horizontal, vertical and 45° track centerlines. [Routing results](../reports/routing_rules.json) are a required export gate, alongside native DRC and independent Gerber verification.

| Rule | Enforcement |
|---|---|
| No curved tracks or arbitrary directions | Reject PCB arcs and non-octilinear centerlines; 0.00002 mm tolerance covers native coordinate rounding only. |
| No redundant copper segments | Reject exact duplicates, overlapping collinear centerlines outside contacts, and unnecessary equal-width collinear joints. |
| No tiny free-space jogs | Free segments must be at least 0.10 mm. Short pad/via escapes are permitted only within the contact copper plus half the trace width. |
| Consistent bends | Free bends have an included angle of at least 135°: a 45° change of direction. True branch junctions and transitions at pad/via contacts are permitted. |
| No disconnected ends | Native `track_dangling` and `via_dangling` checks are errors. Exports require zero DRC violations and zero unconnected items. |
| Preserve electrical requirements | Native net classes, local converter/decoupling path limits, layer restrictions, edge clearances and routed-copper DC-drop limits remain mandatory. |

Same-net branches are normal: several loads must join their supply, and grounds must join the ground network. Different nets crossing on separate copper layers are also normal. Shorts between different nets on the same layer fail clearance/connectivity checks. Rounded copper end caps are normal fabrication geometry; they do not mean the track centerline is curved.

From `current/`, with the tool environment loaded:

```sh
source tools/env.sh
python scripts/test_routing.py
python scripts/check_routing.py
kicad-python scripts/check_board_constraints.py
bash scripts/export_manufacturing.sh
```

Both `validate_release.sh` and `export_manufacturing.sh` enforce the routing gate. The validation summary rejects a routing report with an outdated PCB or checker hash. Ten regression fixtures cover invalid curves, angles, duplicates, overlaps, tiny jogs and sharp bends, plus valid contacts, branches and width transitions. The checks report failures without modifying the board.

The same test command runs six DC-network fixtures. Pad/via contacts and overlaps must remain electrically connected after redundant centerline pieces are removed; real gaps and isolated layers must remain open. The local bypass check counts distance through pad copper without relaxing its path-length limits.

In KiCad, use the straight 45° routing posture. `Ctrl+W` switches straight 45°/90° postures; avoid the curved posture. See the [KiCad PCB Editor manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html).

The cleanup reduced 4,113 segments to 1,993, retaining all 245 vias and the 0.18 mm minimum track width. The [native comparison](../reports/routing_cleanup.json) confirms unchanged footprints, pads, vias, outline, stackup, nets, markings and zone definitions. Copper fills were regenerated. Segment count measures geometric simplification; it is not a measure of electrical performance.

These checks cover CAD geometry and the stated electrical models. The existing [full-power release HOLD and physical qualification requirements](VALIDATION.md) remain in effect.
