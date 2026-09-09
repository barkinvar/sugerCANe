# Rev F prototype fabrication and assembly order

Use [RevF_SC12_Factory_Upload.zip](../order/RevF_SC12_Factory_Upload.zip) for a **prototype lot**, after reviewing the validation plan. No board has been physically qualified, no factory quotation is included and no order has been placed. The exact-MPN BOM is intended for a Chinese or other assembler that accepts customer-specified sourcing; it is not a pre-approved JLCPCB/LCSC turnkey basket.

For a JLCPCB upload, start with the [fabrication-only Gerber ZIP](../order/RevF_SC12_Gerbers.zip), then supply [BOM_JLCPCB.csv](../bom/BOM_JLCPCB.csv) and [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv). Keep [Factory_BOM.csv](../bom/Factory_BOM.csv) alongside for exact-MPN matching. The larger factory packet is a complete reference handoff.

## Fabrication

| Setting | Requirement |
|---|---|
| Board | 52 × 64 mm, four copper layers, FR-4, 1.6 mm nominal |
| Layer order | F.Cu signal/power, In1.Cu GND, In2.Cu GND + 12 V monitor and 3.3 V service branches, B.Cu signal/power |
| Copper | 35 µm nominal each layer; verify finished copper with supplier |
| Dielectric | Symmetric four-layer stack; target outer-to-inner dielectric ≤0.25 mm; supplier must confirm final stack |
| Finish | ENIG specified for exposed programming contacts and fine-pitch ICs |
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

**Factory scope: 110 SMT components on the top side only.** Use `bom/Factory_BOM.csv` (exact MPNs) and `output/assembly/CPL_JLCPCB.csv`. The simplified `bom/BOM_JLCPCB.csv` is a matching aid; blank LCSC numbers require exact-MPN matching against Factory_BOM, never an automatic substitution.

**User scope: six terminal blocks plus three voltage headers (nine through-hole parts), then three loose caps.** The factory must leave J1–J6 and JP101/JP201/JP301 empty. `positions_all_top.csv`, the complete BOM and drawings describe the finished board, not additional factory placements.

CPL coordinates are mm from the PCB lower-left, positive X right and Y up, with native KiCad counterclockwise rotation. Match the uploaded preview to the assembly drawing and check IC/diode pin 1; machine-library rotation conventions can differ.

Power headers are unpopulated; the JP2 termination bridge and all J8 contacts are **unbridged/unpasted as supplied**. The factory must not add solder across JP2 unless a separate reviewed port-configuration work instruction is supplied. The user will hand solder all through-hole parts after delivery. The family name “LSF-SMT” does not make these exact connectors ordinary two-pad SMT parts.

Use exact TPS61085DGKR for U8 and latch-off TPS2553DBVR-1 for both U4/U9. Do not substitute auto-retry TPS2553, a lower-saturation inductor, or nominally equal small MLCCs without electrical review. Preserve capacitor voltage/dielectric/DC-bias behavior, the precision resistors and the 13 kΩ / 33 nF compensation network.

Inspect VSSOP/MCU lead joints, diode polarity and all passive values. Perform unpowered shorts/selector checks, staged current-limited bring-up, firmware programming/readback and rail/input/CAN tests. Track every component substitution and lot.

## Sourcing, cost and delivery

[Cost reduction and batch estimates](COST_REDUCTION.md) separates parts procurement from assembly. LCSC inventory is not proof of JLCPCB factory allocation. No SMT part allocation, complete cart or final quotation has been confirmed. Request exact-MPN matching and incoming date confirmation before paying; the STM32 and any unavailable exact MPN may require outside procurement. Any unapproved item must remain unresolved rather than being silently substituted.

Request Economic PCBA first if the exact parts and four-layer board qualify; compare Standard PCBA with the same SMT-only scope. Avoid paying for bottom-side assembly or through-hole work. Standard assembly still charges feeder loading for all 48 SMT types. No programming or functional-test service is included by this package unless separately quoted; the user performs bring-up and programming.

One-month delivery is unconfirmed. Obtain allocated-part dates, CAM/assembly timing and a destination-specific tracked express quote before scheduling the robot build. Procurement holds and customs may exceed the target. Order hand-fitted parts in parallel once the BOM is finalized.

## Programming deliverables

The packet includes combined `firmware/build/factory.hex` and `tools/program_factory.tcl` for initial SWD programming/protection. Power cycle and verify protection, then use CAN for setup and later `application.sc12` updates. User programming is the default quoted scope; see [fixture procedure](FIXTURE.md). Do not substitute an application-only ELF/HEX.
