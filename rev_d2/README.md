# SC12 — Revision D-2: China SMT assembly and removable voltage jumpers

Rev D-2 preserves Rev D’s circuit and firmware identity (hardware 4, protocol 3). It changes 27 passive placements to specified equivalents, adds three removable power-selection headers, and separates factory SMT assembly from your through-hole work. [Cost basis and remaining costs](docs/COST_REDUCTION.md).

Three industrial digital inputs, selectable **regulated 12 V or 5 V sensor power**, and classic CAN for FRC team projects. The **52 × 64 mm** PCB keeps horizontal Weidmüller push terminals and the compact TC2050 programming contacts. **Every component mounts on the top side.** It uses four copper layers, with both inner layers reserved for ground.

**Engineering prototype release.** CAD, source, manufacturing files and checks are provided for review and prototype fabrication. No physical Rev D-2 board has been assembled or qualified. Production release and competition use require the tests in [VALIDATION.md](docs/VALIDATION.md); CAD checks do not establish either.

![Actual Rev D-2 CAD render](output/review/board_3d_final.png)

| Item | Rev D-2 design target |
|---|---|
| Board input | 6–22 V DC at J1, protected distribution branch required |
| Sensor supplies | 12.01 V nominal buck-boost and 5 V nominal; 300 mA shared per rail |
| Inputs | Three PNP, NPN or push-pull inputs; positive signal range 0–30 V |
| Logic thresholds | LOW ≤1.2 V, HIGH ≥2.4 V targets; supports 3.3/5 V logic, not guaranteed 1.8 V |
| Connectors | Weidmüller LSF-SMT 3.50/90; 1824420000 and 1824430000 |
| MCU / CAN | STM32F042K6T6 LQFP32 + TCAN3413 SO8; 1 Mbit/s |
| Power stage | TPS552872-Q1, synchronous buck-boost; 3.3 µH shielded inductor |
| Assembly | 107 fitted parts: 98 top-side factory SMT; six terminals and three headers hand soldered; three loose caps |
| Parts estimate | $40.50 / $34.69 / $32.23 per board in lots of 5 / 10 / 25, including purchase minimums; PCB/assembly/freight/tax extra |
| Firmware | 0.4.0, hardware 4, original protocol v3; Java, C++ and Python interfaces |

12 V remains regulated when the battery is above or below 12 V within the qualified input/load envelope. It is intended for compatible three-wire Omron/Banner sensors; verify the exact model, current, output type and residual/leakage voltage. A brand name alone is not a compatibility guarantee. Sensor power is hardware-enabled; removable 2 mm jumper caps choose each port's supply. No raw battery output is exposed on Rev D-2.

Firmware reports qualified 12 V power-good and 5 V switch fault status. Counts pause on either rail fault and resume only after 100 ms of continuous good indications. Drivers provide a health-checked input helper. These indications are not calibrated voltage measurements and cannot detect every cable or sensor failure.

The integrated switches, current limiting, shared 5 V driver bias and PCB Kelvin taps avoid extra purchased power devices. Most passives remain 0805 or larger. Four local 0402 capacitors and the 21-pad HotRod QFN require a stencil and controlled reflow/heatbed; inspect the power IC joints. Hand soldering the remaining parts is practical. See [design choices](docs/SIMPLIFICATION.md).

## Order and finish a board

1. Request top-side SMT assembly using the [Gerber ZIP](order/RevD2_SC12_Gerbers.zip), [JLCPCB BOM](bom/BOM_JLCPCB.csv) and [CPL](output/assembly/CPL_JLCPCB.csv). Match all 98 placements against [Factory_BOM.csv](bom/Factory_BOM.csv); a blank factory part ID still needs exact-MPN sourcing. Follow the [factory instructions](docs/FACTORY_ORDER.md).
2. Buy and hand solder the [six terminals and three headers](bom/Hand_solder_BOM.csv), and buy [three closed-top caps](bom/ACCESSORIES.csv). The factory leaves these nine through-hole positions empty. A complete placement drawing also shows these user-fitted parts, so use the SMT-only CPL for the factory order.
3. Leave the caps off during initial bring-up. Follow [assembly and programming](docs/ASSEMBLY.md), then configure voltage, bias and termination with power disconnected. Use the [firmware](firmware/README.md) and [drivers](examples/README.md) supplied here; D-2 retains D's hardware-4/protocol-v3 identity.

| Board quantity | Parts purchase cost per board |
|---|---:|
| 1 | $55.27 |
| 5 | $40.50 |
| 10 | $34.69 |
| 25 | $32.23 |

These estimates include all fitted parts, loose caps and supplier minimums, using observations from September 7–8, 2026. PCB, assembly, attrition, freight and tax are extra; **a delivered price below $50 has not been established**. The $44.16 first-tier consumed-parts figure is a different basis from purchasing enough parts for one board. [Calculation and assumptions](docs/COST_REDUCTION.md).

Confirm component allocation and a destination-specific express-delivery estimate against the one-month target. The [factory guide](docs/FACTORY_ORDER.md) treats 2–4 weeks as a planning allowance, subject to sourcing, production and customs; no order or delivery date is confirmed.

## Removable sensor-voltage selection

JP101, JP201 and JP301 select power for J4, J5 and J6 respectively. Fit **one 2 mm cap per header** with input power disconnected:

| Cap position | Sensor power |
|---|---|
| Pins 1–2 | Regulated 5 V |
| Pins 2–3 | Regulated 12 V |
| Cap removed | Port power disconnected |

Pins run 1–2–3 left to right when viewed from the component side; pin 1 has a square PCB pad. Bias selectors JP103/JP203/JP303 and CAN termination JP2 remain solder settings. The caps are friction-retained, with retention/vibration qualification still required for the actual robot installation. [Full wiring and retention instructions](docs/WIRING.md).

## Files and verification

| Deliverable | Link |
|---|---|
| Native KiCad PCB / schematic | [PCB](hardware/FRC_Sensor_CAN.kicad_pcb), [schematic](hardware/FRC_Sensor_CAN.kicad_sch) |
| Manufacturing / assembly | [Gerbers and drills](output/fabrication), [interactive BOM](output/assembly/interactive_bom.html), [schematic PDF](output/assembly/schematic.pdf) |
| Ordering | [Gerber ZIP](order/RevD2_SC12_Gerbers.zip), [SMT BOM](bom/Factory_BOM.csv), [JLCPCB BOM](bom/BOM_JLCPCB.csv), [CPL](output/assembly/CPL_JLCPCB.csv) |
| User-fitted parts | [Hand-solder BOM](bom/Hand_solder_BOM.csv), [loose caps](bom/ACCESSORIES.csv), [DigiKey import](bom/DigiKey_hand_solder_import.csv) |
| Prototype factory packet | [ZIP](order/RevD2_SC12_Factory_Upload.zip) |
| Complete source/review release | [ZIP](release/FRC_Sensor_CAN_RevD2_SC12_Prototype.zip), [hashes](release/manifest.json) |
| Mechanical handoff | [STEP](output/mechanical/FRC_Sensor_CAN.step), [dimensioned drawing](output/mechanical/mechanical_drawing.pdf) |
| Setup and operation | [wiring](docs/WIRING.md), [assembly](docs/ASSEMBLY.md), [protocol](docs/CAN_PROTOCOL.md), [drivers](examples/README.md) |
| Engineering checks | [Consolidated report](reports/release_checks.json), [D-to-D-2 comparison](reports/variant_verification.json), [SMT file checks](reports/manufacturing/factory_files.json), [qualification plan](docs/VALIDATION.md) |
| Printable handbook | [PDF](output/documentation/SC12_RevD2_Handbook.pdf) |

![Horizontal manufacturer connector models](output/review/board_connectors.png)

[Connector geometry and official model provenance](docs/CONNECTORS.md). Case design is a subsequent task after review of this revision; the mechanical files are a nominal handoff, not an enclosure fit test. Earlier A/B/B-2/C/D designs remain available in the repository.
