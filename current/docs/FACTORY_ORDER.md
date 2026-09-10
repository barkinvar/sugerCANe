# Rev H prototype fabrication and assembly order

Rev H now has a [JLC sourcing candidate](JLC_SOURCING.md): all 55 SMT types have JLC codes; 54 have sufficient public stock for ten boards. The exact MCU needs sourcing. New simulations are paused until user approval of the six passive substitutions. Review/quotation files are available; the full-release order package remains on HOLD. Previous Rev G ZIPs are historical and must not be ordered as Rev H.

For quotation, use [BOM_JLCPCB.csv](../bom/BOM_JLCPCB.csv), [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv), the [fabrication exports](../output/fabrication/) and [Factory_BOM.csv](../bom/Factory_BOM.csv) for exact-MPN matching. Read the [engineering review](ORDER_READINESS.md) and [physical acceptance procedure](VALIDATION.md). No factory quotation or order is included.

## Fabrication

| Setting | Requirement |
|---|---|
| Board | 52 × 74 mm, four copper layers, FR-4, 1.6 mm nominal |
| Layer order | F.Cu signal/power, In1.Cu GND, In2.Cu GND with short/slow control and service routes, B.Cu signal/power |
| Copper | 35 µm nominal each layer; verify finished copper with supplier |
| Dielectric | Symmetric four-layer stack; target outer-to-inner dielectric ≤0.25 mm; supplier must confirm final stack |
| Finish | ENIG retained for fine-pitch IC assembly |
| Minimum trace | 0.18 mm |
| Clearance | 0.20 mm general; U8 package pad-to-pad 0.15 mm local minimum |
| Vias | Through vias, minimum 0.30 mm drill / 0.60 mm pad; no blind/buried vias |
| Drills | Separate PTH and NPTH Excellon; mounting holes remain nonplated |
| Solder mask | Both sides; preserve fine-pitch openings; review U8 mask webs with CAM |
| Stencil | Top only, nominal 0.10 mm laser-cut; use supplied paste apertures |
| Panels | Factory rails/fiducials may be added outside the delivered outline; preserve connector overhang |

Native nominal stack: 0.035 mm copper on all four layers, 0.20 / 1.04 / 0.20 mm dielectric and 0.01 mm solder mask per side, totaling 1.60 mm. These are planning thicknesses; final fabrication tolerances and material selection belong to the approved supplier stack.

This stack is an order requirement, not a confirmed laminate/impedance quotation. CAN is short board-level routing; no fabricated impedance coupon has been qualified. Get the supplier's CAM/stackup review before fabrication.

## Assembly

**Factory scope: 130 SMT components on the top side only.** Use `bom/Factory_BOM.csv` (exact MPNs) and `output/assembly/CPL_JLCPCB.csv`. `bom/BOM_JLCPCB.csv` contains an exact JLC code for every SMT type. Check the manufacturer/MPN against Factory_BOM; an assigned code does not mean stock is allocated. Do not accept automatic substitutions.

**User scope: six terminal blocks, three voltage headers and one J8 service header (ten through-hole parts), then three loose caps.** The factory must leave J1–J6, J8 and JP101/JP201/JP301 empty. `positions_all_top.csv`, the complete BOM and drawings describe the finished board, not additional factory placements.

CPL coordinates are mm from the PCB lower-left, positive X right and Y up, with native KiCad counterclockwise rotation. Match the uploaded preview to the assembly drawing and check IC/diode pin 1; machine-library rotation conventions can differ.

Power headers are unpopulated; JP2 remains **open with no solder bridge**, and all through-hole connector holes remain unpopulated/unpasted. The factory must not add solder across JP2 unless a separate reviewed port-configuration work instruction is supplied. The user will hand solder all through-hole parts after delivery. The family name “LSF-SMT” does not make these exact connectors ordinary two-pad SMT parts.

Use exact TPS61085DGKR for U8, latch-off TPS2553DBVR-1 for U4 and TPS259620DDAR for U9. U9 has an exposed ground pad with supplied segmented paste apertures and six adjacent thermal vias. Inspect its solder attachment. Do not substitute auto-retry TPS2553, a lower-saturation inductor, or nominally equal small MLCCs without electrical review. Preserve capacitor voltage/dielectric/DC-bias behavior, the precision resistors and the 13 kΩ / 33 nF compensation network.

D10 is OPSCO SK6805-EC15 (C2890035), with the exact supplied A/1 pin layout; U10 is SN74AHCT1G125DBVR. Inspect VSSOP/MCU lead joints, diode polarity and all passive values. Perform unpowered shorts/selector checks, staged current-limited bring-up, firmware programming/readback and rail/input/CAN tests. Track every component substitution and lot.

## Sourcing, cost and delivery

[Cost reduction and batch estimates](COST_REDUCTION.md) separate parts from assembly. The [public JLC snapshot](../bom/jlc_sourcing.json) covers all SMT MPNs, but it does not reserve inventory. U5 / STM32F042K6T6 / C69216 has no available public stock. Arrange exact-part JLC sourcing and confirm arrival before assembly; changing MCU silicon or package requires a separate design review.

Request Economic and Standard PCBA quotes with the same SMT-only scope. The snapshot has 42 ordinary extended types; posted fixed fees are close ($138.65 Economic versus $134.34 Standard with two fixtures), so Economic is not automatically cheaper. Standard may need factory rails because the board is only 52 mm wide. Confirm the final four-layer stack, nominal 35 um copper on every layer and component-compatible reflow profile. No programming or functional-test service is included unless separately quoted; the user performs bring-up and programming.

One-month delivery is unconfirmed. Obtain allocated-part dates, CAM/assembly timing and a destination-specific tracked express quote before scheduling the robot build. Procurement holds and customs may exceed the target. Order hand-fitted parts in parallel once the BOM is finalized.

## Programming deliverables

The packet includes combined `firmware/build/factory.hex` and `tools/program_factory.tcl` for initial SWD programming/protection. Power cycle and verify protection, then use CAN for setup and later `application.sc12` updates. User programming is the default quoted scope; see [fixture procedure](FIXTURE.md). Do not substitute an application-only ELF/HEX.
