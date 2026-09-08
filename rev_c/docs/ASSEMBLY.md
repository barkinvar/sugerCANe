# Rev C Lite assembly

Use the exact [BOM](../bom/BOM_grouped.csv), [assembly drawing](../output/assembly/top_assembly.pdf), [interactive BOM](../output/assembly/interactive_bom.html) and placement files. Reference labels are in these drawings; dense placement does not leave room to print every reference legibly on the actual top silkscreen.

1. Order the 52 ×56 mm, two-layer, 1.6 mm board with 1 oz finished copper target. Use the exported Gerbers and separate plated/nonplated drill files. Have the fabricator review its actual stackup, annular rings, mask registration and minimum features. Gold finish is useful at the programming contacts; keep solder and paste off them.
2. Check bare-board continuity and orientation. Apply paste to SMT pads only. A 0.10 mm stencil is a starting point; the assembler must review release and the exposed-pad aperture. Solder selectors, TC2050 contacts and the test point deliberately have no paste.
3. Place 0805/1206 passives, diodes and ICs. Verify C1 polarity, TVS/diode cathodes, pin 1 on each IC and the exact latch-off TPS2553DBVR-1 suffix. U3 TPS1H200A has an exposed thermal pad that must be soldered to its ground land; use paste and a controlled heatbed/reflow profile. There are no components on the bottom.
4. Inspect joints and measure for supply shorts. Hand solder the six horizontal Weidmüller terminals after SMT reflow unless the assembler qualifies their THR process. Fill both plated holes per terminal pole. Support the board without loading fresh SMT joints. The terminal pins extend below the board.
5. Leave all selectors open for initial bring-up. Supply J1 from a current-limited bench supply, starting at 12 V and a modest current limit. Confirm input polarity, protected input, approximately 5.07 V internal and 3.3 V logic rails. Sensor headers remain unpowered while power selectors are open.
6. Program through the custom TC2050 mapping, verify flash and configure a unique CAN ID over UART. Then power off, choose each port's supply/bias and termination settings, inspect bridges and check that 5 V and battery are not shorted.
7. Perform the [qualification checks](VALIDATION.md) before connecting a robot harness. Begin with a known load and known logic source, then the actual sensor/cable.

Use M3 hardware at (3.5,4) and (48.5,34.5) mm. Holes are 3.2 mm NPTH. The copper keepout has at least 3.30 mm radius; use hardware whose contact area stays within a 6.4 mm diameter, with insulating washers/spacers as appropriate. Account for component bodies, connector overhang and protruding pins. Do not clamp the PCB between conductive surfaces. The [mechanical drawing](../output/mechanical/mechanical_drawing.pdf) gives nominal geometry, not a fitted enclosure.

The compact board still benefits from magnification and a fine iron. It is easier to assemble than B because it removes 55 fitted parts and all loose shunts, but it is not a through-hole beginner kit.
