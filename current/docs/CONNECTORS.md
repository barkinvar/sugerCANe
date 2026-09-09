# Horizontal Weidmüller terminals

| References | Exact MPN | Series description | DigiKey |
|---|---|---|---|
| J1–J3 | **1824420000** | LSF-SMT 3.50/02/90 3.5SN BK TU | 281-2020-ND |
| J4–J6 | **1824430000** | LSF-SMT 3.50/03/90 3.5SN BK TU | 281-2021-ND |

Manufacturer pages: [2-pole](https://eshop.weidmueller.com/p/1824420000), [3-pole](https://eshop.weidmueller.com/p/1824430000). `/90` gives horizontal wire entry parallel to the PCB. `/135` is the angled version and is not used. Phoenix PTSM is not fitted.

These are through-hole/THR parts despite “SMT” in the family name. Pitch is 3.5 mm, with two solder legs per pole and 7 mm row spacing. PCB drills are 1.1 mm. Housing widths are 7.7 mm / 11.2 mm. Manufacturer CAD is 14.3 mm deep; the footprint conservatively reserves 14.75 mm. Height is 8.5 mm above the mounting surface; nominal pin tips reach 3.5 mm below that surface (about 1.9 mm beyond a 1.6 mm PCB).

Current renders use the official STEP solids with a rigid translation (-2.13,-12.625,-3.5) mm into the footprint origin. They are not approximate connector boxes. Display colors are assigned by the project. Original files, transformed files, URLs, hashes, pin/drill checks and nominal bounds are in [vendor_connectors.json](../hardware/library/3d/vendor_connectors.json). Script `import_connector_models.py` checks all six placed pad patterns and the two vendor models. Do not regenerate models merely to change routing: STEP exporters can alter file headers without changing geometry.

Top terminals face outward at the power/CAN edge; three sensor terminals face outward at the opposite edge. The board and nominal terminal bodies occupy a conservative 52 × 82.1 mm envelope; add room for cable bend, strain relief and button access. Renders do not validate conductor retention, tool clearance in an enclosure, molding tolerances or actual solder fit.

## Rev H voltage headers

JP101/JP201/JP301 use [Harwin M22-2010305](https://www.harwin.com/products/M22-2010305): 2 mm pitch, 0.50 mm square pins, 6 × 2 mm body, nominal 5 mm height above the PCB and 3.4 mm tails. The project's 2 mm header footprint uses 0.85 mm drills in 1.35 mm pads, retaining a 0.25 mm nominal copper annulus, and a 0.25 mm nominal body courtyard margin. Pads 1–3 run left-to-right at Y=60.4 mm; pin-1 positions are X=5, 21 and 37 mm.

The [Harwin drawing](https://content.harwin.com/asset/8870086f-d3e9-4bcd-99da-e6fb77550f38/DRG-00483-Technical-Drawing-Datasheet-M22-201-pdf.pdf) recommends 0.80 ±0.05 mm holes. The retained footprint adds 0.05 mm nominal diameter for hand assembly: with [JLCPCB's normal −0.08/+0.13 mm hole tolerance](https://jlcpcb.com/capabilities/pcb-capabilities), the minimum becomes 0.77 mm, above Harwin's 0.75 mm minimum. This trades a slightly larger solder gap for insertion clearance; verify finished holes and solder fill on the first article.

The [Sullins SPN02SVEN-RC drawing](https://www.sullinscorp.com/drawings/273_SVEN_11502.pdf) specifies a closed top, 2 mm pitch, 0.50 mm square mating pins and nominal 4 × 2 × 4.92 mm body. Contact height is 2.45 mm from the entry, within the header’s 3.5 mm mating pin length. Nominal mating geometry agrees; physical fit and retention remain untested. Caps are delivered loose and not included in the assembled-board STEP model. Use the finished cap envelope for enclosure access/clearance and allow room to remove them.

The generic local header STEP represents the nominal pin/body geometry, not manufacturer-qualified tolerances. Vendor connector hashes continue to cover the unchanged six terminal models. See [wiring](WIRING.md) for one-cap-per-header configuration and vibration retention qualification.

J8 is a hand-fitted XFCN PM254V-12-10P-H85 recessed female socket, 2×5 at 2.54 mm pitch, with 1.10 mm plated holes and 1.70 mm pads. The matching nominal model and the full custom pin map are in [status and programming](STATUS_AND_PROGRAMMING.md) and [wiring](WIRING.md).

## Edge clearance and visible markings

The bottom resistor R101 now lies horizontally between the first two sensor terminals: its closest pad is 2.20 mm from the board edge, previously 0.575 mm. R103 and R203 moved into the gap beside the third terminal, with 2.05 mm pad-to-edge clearance, previously 0.80 mm. F1, D102, R22 and R109 also moved inward. R104 has 1.98 mm clearance; the two small parts above J8 have 1.70 mm. The compact buck feedback pair R1/R2 retains its original 1.30 mm pad clearance and quiet local routing. These distances are to copper pads, not component bodies.

The board remains 52 × 74 mm, with all components on top. Keep an insulating enclosure around the board and underside solder tails. The recessed debug contacts reduce accidental bridging from above; the socket is unkeyed and is not sealed against metal debris. Remove the programming cable for robot use.

The power headers sit at Y=60.4 mm. Their 5V/12V labels share a baseline above the pins at Y=58.8 mm. The specified [Sullins SPN02SVEN-RC cap](https://s3.amazonaws.com/catalogspreads-pdf/PAGE127%202mm%20JUMPER.pdf) has a nominal 4 × 2 mm footprint; both fitted positions leave the labels above it exposed. Front legends identify VIN, CAN L(G)/H(Y), termination, DEBUG, each 5V/12V selection, and V1/V2/V3, GND and IN1/IN2/IN3 at the sensor terminals. Both CAN pairs share a horizontal label baseline: G means green, Y means yellow; see [wiring](WIRING.md). The back repeats the full connection and custom debug map. Select voltages with power off; fit one cap per header.

The two bare pads beside TERM are JP2, the optional CAN termination solder bridge. Closing it enables the onboard 120 Ω resistor across CAN H/L; leave it open unless this board needs to terminate a bus end. The single round gold pad near VIN is TP1, connected to GND for a meter or test probe. Both features intentionally remain unpopulated.

The large cylindrical part near the left edge is C1, a [Panasonic EEE-FK1H470P](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/lineup/aluminum-electrolytic-capacitors-surface-mount-type/series/88994/model/89532), 47 µF / 50 V, nominally 8 mm diameter and 6.2 mm body length. Its center is (5,21) mm, placing the nominal can edge 1 mm inside the PCB edge. The local CAD model is approximately 6.5 mm tall, below the 8.5 mm terminals. Engineering assessment: board orientation alone does not require moving C1, but its exposed side needs protection from impacts and cable forces. Keep clearance between the enclosure and capacitor; support the board and strain-relieve cables independently. Retain this placement for an enclosed prototype, pending physical vibration/impact checks. [Panasonic's handling guidance](https://industrial.panasonic.com/cdbs/www-data/pdf/RDE0000/RDE0000COL99.pdf) requires evaluation in the actual vibration environment; this standard part must not be treated as a 30 G vibration-proof variant.

## Layout refinement

The outline now has **1.5 mm corner radii**, within the same 52 × 74 mm dimensions. Mounting-hole centers, connector positions, service socket and the LED duct space stay fixed. All six input-bias transistors share the same Y=57.15 mm row; R4 aligns with the neighboring support parts. Native DRC and the independent Gerber check use the rounded contour, including copper-to-edge clearance around the corners.

[LaserCAN's board](https://github.com/GrappleRobotics/LaserCAN/tree/5f444a38242da367e60176aecb3b1c7f20c92063/LaserCAN-Board) informed the rounded outline and consistent grouping. Its approximately 25 × 25 mm board places components on both sides and uses a different connector and sensor arrangement. SC12 retains top-side assembly, hand-solderable terminals, three external input circuits and two protected sensor supplies. The refinement changes no purchased parts or functions; it does not claim a lower factory quote. No LaserCAN circuit or library files were copied into the design.
