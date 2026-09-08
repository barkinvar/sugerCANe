# Rev D prototype fabrication and assembly order

Use [RevD_SC12_Factory_Upload.zip](../order/RevD_SC12_Factory_Upload.zip) for a **prototype lot**, after reviewing the validation plan. No board has been physically qualified, no factory quotation is included and no order has been placed. The exact-MPN BOM is intended for a Chinese or other assembler that accepts customer-specified sourcing; it is not a pre-approved JLCPCB/LCSC turnkey basket.

## Fabrication

| Setting | Requirement |
|---|---|
| Board | 52 × 64 mm, four copper layers, FR-4, 1.6 mm nominal |
| Layer order | F.Cu signal/power, In1.Cu GND, In2.Cu GND, B.Cu signal/power |
| Copper | 35 µm nominal each layer; verify finished copper with supplier |
| Dielectric | Symmetric four-layer stack; target outer-to-inner dielectric ≤0.25 mm; supplier must confirm final stack |
| Finish | ENIG specified for exposed programming contacts and fine-pitch QFN |
| Minimum trace | 0.18 mm |
| Clearance | 0.20 mm general; U8 package pad-to-pad 0.15 mm local minimum |
| Vias | Through vias, minimum 0.30 mm drill / 0.60 mm pad; no blind/buried vias |
| Drills | Separate PTH and NPTH Excellon; no plated mounting or alignment holes |
| Solder mask | Both sides; preserve fine-pitch openings; review U8 mask webs with CAM |
| Stencil | Top only, nominal 0.10 mm laser-cut; use supplied paste apertures |
| Panels | Factory rails/fiducials may be added outside the delivered outline; preserve connector overhang |

Native nominal stack: 0.035 mm copper on all four layers, 0.20 / 1.04 / 0.20 mm dielectric and 0.01 mm solder mask per side, totaling 1.60 mm. These are planning thicknesses; final fabrication tolerances and material selection belong to the approved supplier stack.

This stack is an order requirement, not a confirmed laminate/impedance quotation. CAN is short board-level routing; no fabricated impedance coupon has been qualified. Get the supplier's CAM/stackup review before fabrication.

## Assembly

104 fitted components: **98 SMT on top, six through-hole/THR terminals**. Use `positions_smd_top.csv` for SMT and `positions_all_top.csv`/assembly drawing for reference. R64 is physically a normal two-terminal 1206 resistor; its four numbered PCB pads include two copper-only Kelvin taps. NT1 is a copper ground tie and is not a purchased component. Do not interpret pad count as component termination count.

All power/bias/termination solder bridges and all J8 contacts are **unbridged/unpasted as supplied**. The factory must not add solder across selectors unless a separate reviewed port-configuration work instruction is supplied. Through-hole connectors can be hand or selective soldered after SMT reflow. The family name “LSF-SMT” does not make these exact connectors ordinary two-pad SMT parts.

Do not replace U8 with a generic 21-pin QFN, substitute a lower-saturation inductor, change the precision divider grade, or replace the 1210 capacitor bank with a nominally equal capacitance without approval of the actual electrical/footprint data. DigiKey substitute labels alone are insufficient. Maintain 0.1 ohm shunt value, tolerance and terminal orientation.

Inspect fine-pitch solder bridges and the five long QFN power pads with suitable inspection/X-ray for the prototype lot. Perform unpowered shorts/selector tests, current-limited staged bring-up, firmware programming/readback and functional rail/input/CAN tests before accepting units. Track lot and component substitutions.

## Cost and quantity

The [BOM](../bom/BOM_grouped.csv) totals **$54.89 per board on a conservative quantity-one component basis**, using dated supplier observations. PCB, stencil, sourcing service, attrition, placement, through-hole work, inspection, programming, test, freight, duties and taxes are extra. Quantity breaks can reduce parts cost; factory-specific assembly fees require a real quotation. This release does not claim a fabricated-board or delivered-PCBA price.
