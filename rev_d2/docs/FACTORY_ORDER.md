# Rev D-2 prototype fabrication and assembly order

Use [RevD2_SC12_Factory_Upload.zip](../order/RevD2_SC12_Factory_Upload.zip) for a **prototype lot**, after reviewing the validation plan. No board has been physically qualified, no factory quotation is included and no order has been placed. The exact-MPN BOM is intended for a Chinese or other assembler that accepts customer-specified sourcing; it is not a pre-approved JLCPCB/LCSC turnkey basket.

For a JLCPCB upload, start with the [fabrication-only Gerber ZIP](../order/RevD2_SC12_Gerbers.zip), then supply [BOM_JLCPCB.csv](../bom/BOM_JLCPCB.csv) and [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv). Keep [Factory_BOM.csv](../bom/Factory_BOM.csv) alongside for exact-MPN matching. The larger factory packet is a complete reference handoff.

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

**Factory scope: 98 SMT components on the top side only.** Use `bom/Factory_BOM.csv` (exact MPNs) and `output/assembly/CPL_JLCPCB.csv`. The simplified `bom/BOM_JLCPCB.csv` is a matching aid; blank LCSC numbers require exact-MPN matching against Factory_BOM, never an automatic substitution.

**User scope: six terminal blocks plus three voltage headers (nine through-hole parts), then three loose caps.** The factory must leave J1–J6 and JP101/JP201/JP301 empty. `positions_all_top.csv`, the complete BOM and drawings describe the finished board, not additional factory placements.

CPL coordinates are mm from the PCB lower-left, positive X right and Y up, with native KiCad counterclockwise rotation. Match the uploaded preview to the assembly drawing and check IC/diode pin 1; machine-library rotation conventions can differ. R64 is physically a normal two-terminal 1206 resistor; its four numbered PCB pads include two copper-only Kelvin taps. NT1 is a copper ground tie and is not a purchased component. Do not interpret pad count as component termination count.

Power headers are unpopulated; all bias/termination solder bridges and all J8 contacts are **unbridged/unpasted as supplied**. The factory must not add solder across selectors unless a separate reviewed port-configuration work instruction is supplied. The user will hand solder all through-hole parts after delivery. The family name “LSF-SMT” does not make these exact connectors ordinary two-pad SMT parts.

Do not replace U8 with a generic 21-pin QFN, substitute a lower-saturation inductor, change the precision divider grade, or replace the 1210 capacitor bank with a nominally equal capacitance without approval of the actual electrical/footprint data. DigiKey substitute labels alone are insufficient. Maintain 0.1 ohm shunt value, tolerance and terminal orientation.

Include inspection of fine-pitch joints and the five long QFN power pads with suitable inspection/X-ray for the prototype lot. Perform unpowered shorts/selector tests, current-limited staged bring-up, firmware programming/readback and functional rail/input/CAN tests before accepting units. Track lot and component substitutions.

## Sourcing, cost and delivery

[Cost reduction and batch estimates](COST_REDUCTION.md) separates parts procurement from assembly. LCSC inventory is not proof of JLCPCB factory allocation. No SMT part allocation, complete cart or final quotation has been confirmed. Request exact-MPN matching and incoming date confirmation before paying; the STM32 and TPS552872-Q1 may require outside procurement. Any unapproved item must remain unresolved rather than being silently substituted.

Request Economic PCBA first if the exact parts and four-layer board qualify; compare Standard PCBA with the same SMT-only scope. Avoid paying for bottom-side assembly or through-hole work. Standard assembly still charges feeder loading for all 46 SMT types. No programming or functional-test service is included by this package unless separately quoted; the user performs bring-up and programming.

A delivery within one month is plausible with allocated parts and tracked air express. Budget 2–4 weeks as a planning allowance, not a carrier promise; procurement, review holds and customs can exceed it. Country/postcode and order quantity are needed for an actual delivered quote. Have the manual parts arrive in parallel. Do not select a long supplier lead time to obtain a lower component price when the one-month target matters.
