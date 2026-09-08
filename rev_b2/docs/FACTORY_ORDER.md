# Rev B-2 factory order instructions

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

This package is ready to submit for a **prototype fabrication and turnkey assembly quotation**. Factory stock matching, panel/fixture review and placement-orientation approval remain necessary before manufacture. It is not a completed JLCPCB checkout or a qualified production release.

## Files to submit

1. `order/RevB2_Gerbers.zip`: single-board Gerbers and plated/nonplated Excellon drills, in millimeters. Do not scale or mirror.
2. `bom/BOM_turnkey.csv`: complete exact-manufacturer/MPN sourcing BOM, including all 144 fitted parts and ten loose shunts per board.
3. `output/assembly/CPL_JLCPCB.csv`: all 144 fitted placements, top side. `bom/BOM_JLCPCB.csv` supplies the corresponding 50 fitted BOM groups. Blank LCSC fields require exact-MPN global sourcing or consignment; they do not mean DNP. The shunts are separately listed in `bom/ACCESSORIES.csv` and must be bagged.
4. `output/assembly/top_assembly.pdf`, `bottom_markings.pdf`, `schematic.pdf`, `pad_coordinates.csv` and the interactive BOM for pin-one and polarity review.
5. `output/mechanical/FRC_Sensor_CAN.step`, the 1:1 mechanical PDF, and these instructions. The STEP models are conservative placement aids, not certified connector tooling models.

## PCB and panel requirements

| Setting | Requirement |
|---|---|
| Finished board | 60 × 68 mm, 2 layers, 1.6 mm FR-4 |
| Copper | Nominal finished 35 µm / 1 oz per side; use the supplied electrical clearances |
| Finish | ENIG, both masks, green mask, white silkscreen |
| Minimum features | 0.18 mm tracks; 0.20 mm clearance; ordinary vias 0.60/0.30 mm; preserve every supplied drill |
| Assembly | 128 SMT and 16 through-hole components, all on top; no bottom components |
| Stencil | 0.10 mm starting specification, supplied top paste; assembler to review aperture release and U3 exposed-pad paste |
| Pogo connector J8 | Ten bare ENIG contacts: NO paste, solder, connector or conformal coating; three alignment holes remain NPTH |
| Mounts | Four 3.2 mm NPTH; do not fill or plate |
| Solder | Lead-free process, engineer-reviewed profile compatible with every supplied component |

For JLCPCB **Standard PCBA**, the single PCB is below the published 70 × 70 mm minimum processing envelope. Request factory panelization with removable tooling rails and fiducials. A 5 mm rail allowance around each side gives a nominal **70 × 78 mm processing outline** before panel spacing/tabs. The assembler must finalize tooling-hole/fiducial/tab positions. Do not drill new tooling holes in the functional 60 × 68 mm board: there is routed copper near the edges.

The six horizontal connector bodies project beyond the top and bottom board edges. Assemble SMT while supported by rails, then depanel and install these connectors in a supporting fixture, or propose an equivalent process with sufficient overhang clearance. The finished assembly reserves **60 × 76.1 mm**, excluding cables; terminal height is **8.5 mm**, leads **3.5 mm** before trimming. Breakaway tabs and fixtures must not foul the housings, actuator travel, solder joints or nearby copper. Panel design is part of the factory's engineering service, not a supplied production panel.

The selected Samsung 100 nF capacitor's reference sheet recommends a maximum 250 °C reflow peak for six seconds. Use a controlled profile within component limits (JLCPCB Standard lists 240 ±5 °C). Do not automatically apply Economic PCBA's listed 255 ±5 °C profile to this BOM. Solder THT parts afterward. U3's exposed thermal pad must be soldered and inspected; do not omit it or its thermal vias. The assembler must review paste loss into these vias; no via-in-pad filling process is presumed in the cost estimate.

## Placement coordinates and orientation

The factory CPL origin is the **lower-left finished-board corner viewed from above**: X increases right, Y increases up, and all coordinates are positive millimeters. Rotations are KiCad top-side counterclockwise degrees. SMT parts use the native body-center origin. Through-hole header and terminal centers have explicit offsets from their KiCad pin-one origins; those offsets are recorded in `coordinate_offsets.csv`.

`pad_coordinates.csv` provides every numbered pad in the same coordinate frame and is the final reference for matching factory library orientation. Confirm U1–U8, Q1, Y1, every diode/LED and C1 polarity. Do not assume an LCSC library's zero-degree rotation matches KiCad. The original `positions_all_top.csv` uses KiCad's upper-left origin with negative Y and is provided only as a native reference; **do not mix it with the factory CPL**.

## Parts that require particular attention

- J1–J3: **Weidmüller 1824420000**, LSF-SMT 3.50/02/90 3.5SN BK TU. J4–J6: **1824430000**, LSF-SMT 3.50/03/90 3.5SN BK TU. These are horizontal wire entry, parallel to the PCB. Two legs per pole, 7 mm between rows, 1.1 mm drills. Do not substitute `/135`, `/180`, Phoenix or an unreviewed clone.
- U5: **STM32F042K6T6**, LQFP32. LCSC C69216 was out of stock at the observation date. Procure from DigiKey or another authorized source. Do not substitute STM32F030 or another MCU; pin compatibility alone is insufficient.
- U7: **LM339LVDR**, not an ordinary LM339. Its low-voltage input behavior is required.
- U4: **TPS2553DBVR-1**, including the `-1` latch-off suffix. U3: **TPS1H200AQDGNRQ1** with its exposed pad.
- Keep the specified inductors, fuse, TVS diodes, clamp diodes, timing/filter capacitors and crystal exact. Only the five part-family substitutions listed in `PART_CHANGES.md` are incorporated. Quote any further proposed change for engineering review before fitting it.

Every BOM reference is fitted unless explicitly labeled an accessory. J8, test pads and mounting holes are unpopulated PCB features. Deliver all ten configuration shunts loose in an antistatic bag. Ship power selectors, bias selectors, threshold selectors and CAN termination **open**. This leaves sensor-power connections open until the user configures the board.

## Inspection, optional programming and delivery

Include bare-board electrical testing, SMT AOI, THT visual inspection, polarity inspection, and inspection of U3's hidden solder joint. Check that paired terminal legs connect to the same pole and adjacent poles remain isolated. Do not count bare-board testing/AOI as a functional CAN or sensor test.

The base assembly quote may ship an unprogrammed MCU. For a programmed board, separately quote flash/verify and basic power checks using `firmware/build/sensor_can.hex` or `.bin` (address **0x08000000** for BIN). File hashes are in the archive manifest. Read `firmware/README.md` and `WIRING.md`: J8 is a TC2050-IDC-NL **mechanical** pattern with a **custom electrical pinout**. Its pin 6 is target-voltage reference, not programmer power. Power the board through J1 with a current-limited supply; never inject probe 3.3 V into J8.

With all shunts removed, check the intermediate rail (~3.97 V), internal 5 V and logic 3.3 V. Flash, read back, verify and leave sensor rails disabled. Leave flash configuration erased unless an explicit per-unit ID provisioning list is supplied. A production fixture, full CAN/sensor/load tests and qualification are additional work; `QUALIFICATION.md` describes the required engineering measurements.

Pack assemblies individually in ESD bags, protect actuator overhang and pogo pads, include loose shunts and unused boards/components as agreed in the quotation. Return the exact fitted-MPN list and programming/inspection results with each batch.

Sources: [JLCPCB assembly capabilities and reflow temperatures](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [JLCPCB pricing](https://jlcpcb.com/help/article/pcb-assembly-price), [Samsung capacitor reference sheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/893/CL21B104KCFNNNE_Spec.pdf).
