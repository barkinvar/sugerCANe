**Hand assembly — revision A prototype**

Use the [interactive BOM](../output/assembly/interactive_bom.html), [top assembly drawing](../output/assembly/top_assembly.pdf) and exact [per-reference BOM](../bom/BOM_per_reference.csv). The board has 161 fitted components, ten bare test pads and four nonplated mounting holes. All fitted components are on the top side. Configuration shunts are installed only after inspection.

In the interactive BOM, filter by reference or manufacturer part number, then select a row to highlight its board position. Enable pin-1 highlighting when checking orientation. The 60 grouped assembly rows retain component-specific notes; the purchasing BOM combines these into 51 order lines. Widen the table with its divider or hide the Notes column when using a small screen. Sourced and placed checkboxes stay in that browser's local storage; they are personal assembly notes, not an inspection record shared with another computer.

Most passives are 0805 or larger, with visible leads on the MCU and most ICs. **U3 is the exception:** its HVSSOP exposed pad must be soldered to ground. A heatbed/reflow process with suitable paste and temperature measurement is needed for that joint. A soldering iron alone cannot reliably establish the underside joint. U3 has 0.65 mm lead pitch; U5 has 0.8 mm pitch.

Y1 uses Abracon's recommended 1.8 × 1.2 mm lands on 4.0 × 2.4 mm centers, extending beyond the nominal crystal body for solder access. Its electrical terminals are pads 1 and 3; pads 2 and 4 are grounded case contacts. Abracon permits the package chamfer at pin 1 or 4, so confirm the supplied part orientation against its drawing and markings rather than relying on a chamfer alone.

Recommended equipment: microscope or strong magnification, fine tweezers, temperature-controlled iron, flux, solder wick, a controllable heatbed/hotplate with thermocouple, optional hot-air assistance, multimeter, current-limited bench supply and oscilloscope. Use ESD handling and fume extraction appropriate for the chosen solder process. Buy paste from a traceable supplier and follow its storage and profile instructions.

**Fabrication and stencil**

Order a 96 × 96 mm two-layer board, 1.6 mm FR-4, 1 oz copper, with solder mask and lead-free HASL or ENIG. ENIG gives flatter small pads. The fabrication README lists drill and layer details. Request tenting of vias where the supplied mask does not open them. Do not add copper to the mounting-hole clearances or the C1 body keepout. Only C1's necessary footprint lands enter that body area; its ground land has a solid connection to the surrounding pour.

A 0.10 mm top stencil is the starting process choice; verify paste release with the assembler. U3's exposed-pad paste is split into four 0.65 × 0.8 mm windows, about 70% of the 1.57 × 1.89 mm exposed area. Four 0.30 mm thermal vias sit outside those paste windows. Do not replace the split apertures with one solid paste opening. Excess paste can float U3 or bridge its leads. The supplied bottom paste file is intentionally empty of component apertures.

**Assembly sequence**

1. Check board outline, solder mask, drill registration and pad finish. Confirm no visible shorts or broken tracks. Compare IC and connector footprints to the actual purchased parts before applying paste.
2. Apply paste to the top stencil and inspect every fine-pitch aperture. Place low-profile passives and ICs, then the crystal, inductor and aluminum capacitor. Keep through-hole headers and screw terminals out of the reflow cycle unless their exact manufacturer process explicitly allows it.
3. Check polarity and pin 1 before heating. U5 pin 1 is the package dot/chamfer reference, not the text direction. Q1's pin 4 is gate; pins 1–3 source face the protected rail and pins 5–8 drain face the fused input. TVS and bias-diode cathodes go to footprint pad 1. D3 cathode goes to VIN_PROT. C1 positive goes to VIN_PROT; the can's stripe marks negative. LED cathode is pad 1. Y1 pads 2 and 4 are grounded case pads.
4. Reflow using a measured board/component temperature profile compatible with the paste and the most restrictive component. **A heatbed setpoint is not the package temperature.** Do not invent a universal time/temperature recipe. Panasonic C1 requires its specified SMD reflow process; avoid prolonged heating. Leave at least 2 mm above the capacitor vent in an enclosure. U3 is MSL 2, 260 °C classified, with one-year floor life under specified storage conditions. Follow actual bag labels and baking instructions if exposure history is uncertain.
5. Cool without moving the board. Inspect U1/U2/U3/U4 fine-pitch leads, all U5 pins, and diode orientation. Inspect for solder balls beneath the MCU and regulator. U3's underside joint cannot be fully verified optically; use process control plus electrical/thermal checks, or X-ray if available.
6. Iron-solder headers and screw terminals, keeping them square and fully seated. Use enough heat to wet ground-connected leads without cooking the connector body. Clean according to the flux manufacturer's instructions and dry completely.
7. Leave JP1, JP2 and all sensor selectors open. Perform the unpowered checks in [BRING_UP.md](BRING_UP.md) before applying power. Add only the selected sensor shunts after rail validation.

The BOM's spare-parts import adds small passive/diode/LED spares. It does not buy extra ICs, connectors, crystal, inductor or fuse. Confirm R1 is **101 kΩ 0.1%**, R2 **13.7 kΩ 0.1%**, R4 **1 kΩ**, R14 **10 kΩ**, C14 **33 nF**, R5 **3.9 kΩ**, R10 **59 kΩ**, and the four pulldowns R109/R209/R309/R409 are **4.7 kΩ 2010, 0.75 W**. Do not substitute a small 0805 pulldown in that location.

Mount through H1–H4 using M3 insulating standoffs and hardware. Hole centers are (4,4), (92,4), (4,92), (92,92) mm from the board's top-left coordinate origin. Each has at least 3.5 mm radial copper clearance; the polygon vertices are at 3.52 mm radius. Keep metal, chips and wire strands away from the underside; provide cable strain relief and a ventilated insulating cover suitable for the robot. The STEP models are assembly envelopes, not enclosure-tolerance certification; terminal screws and wires need additional tool/bend clearance.

Record board serial number, PCB supplier/lot, component substitutions, paste/profile, inspection results and programming image hash. Any substitution affecting voltage, leakage, capacitance, pinout or package requires rechecking the relevant engineering calculation and physical test.
