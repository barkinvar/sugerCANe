# sugarCANe / SC12 Rev H — current design

[Repository: barkinvar/sugerCANe](https://github.com/barkinvar/sugerCANe) · [Folder map](../README.md#folder-map)

Three digital sensor inputs over CAN, with regulated **5 V / 12 V sensor power** and software-selectable **NPN, PNP, push-pull, floating detection and keeper**. Removable 2 mm jumpers select each port's power voltage. Components populate both PCB surfaces.

A tiny pixel-cane island sits on the front, below the upper-left mounting hole and above C1. A vertical pixel wordmark reads bottom to top beside C1. The underside carries 79 fitted SMT parts, a compact sugarCANe wordmark, and labels for the termination bridge and ground test pad. Connector and voltage labels remain on top; the programming map is in the wiring guide. [Bottom render](output/review/board_bottom.png).

Rev H adds one enclosure-facing RGB status LED and a hand-soldered recessed female programming socket for a ten-board batch. The LED is on the right, above the mounting hole, with a 6 mm circular area reserved for a printed light duct; see the [enclosure dimensions](docs/STATUS_AND_PROGRAMMING.md#enclosure-location). It retains Rev G's power protection and physical voltage jumpers. The 12 V reservoir is upstream of a controlled output eFuse; both rails have default-off enables and CAN fault reset. Two ADC channels measure the protected rails. [Engineering review](docs/ORDER_READINESS.md) · [verification and bench procedure](docs/VALIDATION.md). This design uses its own CAN protocol; it is not CTRE Phoenix or GrappleHook compatible.

**Selected assembly plan:** JLC fits **129 SMT parts (50 top / 79 bottom)**. You buy **STM32F042K6T6 from DigiKey** and solder U5, then fit ten through-hole parts and three jumper caps. U5 is omitted from the factory BOM, CPL and stencil. The retained dated sourcing snapshot lists stock for ten boards for all 54 factory types; power transient screening passes; factory quotation remains pending. **[Start here: where to buy and how to order](docs/FACTORY_ORDER.md).**

![Rev H board](output/review/board_3d_final.png)

| Specification | Rev H |
|---|---|
| Board supply | 6–22 V DC |
| Sensor supplies | Regulated 5 V / 12 V; **300 mA shared per rail**, not per port |
| Signal targets | Positive 0–30 V; LOW ≤1.2 V, HIGH ≥2.4 V; common ground |
| Input setup | Software bias and active-state selection independently per channel |
| Protection | Reverse input, fuse/TVS, separate protected 5 V and 12 V outputs, controlled 12 V inrush |
| Fault reset | Remove the fault, then use CAN power reset; hardware limits remain independent |
| Controller | STM32F042K6T6, TCAN3413; 1 Mbit/s classic CAN |
| Software | App 0.9.0, bootloader 1.1.0, hardware 8, protocol 4 |
| Servicing | CAN discovery, ID/settings and recoverable firmware upload; initial installation through a 2.54 mm SWD service socket |
| PCB / assembly | **44 × 48 mm**, four copper layers, 129 factory SMT + user-fitted MCU + ten through-hole parts + three caps |

Parts purchasing is about **$27.08 per board at ten boards before SMT attrition**, or **$27.96** including a conservative allowance. These include the user-fitted DigiKey MCU, through-hole parts and caps; two optional spare MCUs are extra. PCB, assembly, freight and tax are extra. [Cost calculation](docs/COST_REDUCTION.md).

| What you want to do | Start here |
|---|---|
| Wire and configure a sensor | [Wiring](docs/WIRING.md), [input modes](docs/INPUT_MODES.md) |
| Understand the circuit | [Power and input design](DESIGN_PLAN.md), [schematic PDF](output/assembly/schematic.pdf) |
| Request a prototype quotation | [Factory instructions](docs/FACTORY_ORDER.md), [package status](order/README.md) |
| Read LED / choose a programmer | [Status and programming](docs/STATUS_AND_PROGRAMMING.md) |
| Assemble and program | [Assembly](docs/ASSEMBLY.md), [unit fixture](docs/FIXTURE.md), [CAN service](docs/CAN_SERVICE.md) |
| Write robot code | [Examples/drivers](examples/README.md), [CAN protocol](docs/CAN_PROTOCOL.md) |
| Edit the board | [KiCad project](hardware/FRC_Sensor_CAN.kicad_pro), [PCB](hardware/FRC_Sensor_CAN.kicad_pcb), [interactive BOM](output/assembly/interactive_bom.html) |
| Design an enclosure | [STEP](output/mechanical/FRC_Sensor_CAN.step), [mechanical drawing](output/mechanical/mechanical_drawing.pdf) |
| Review or reproduce checks | [Validation](docs/VALIDATION.md), [power simulations](reports/electrical/boost_spice.json), [check summary](reports/release_checks.json), [tool setup](TOOLS.md) |
| Download everything | [Source/release status](release/README.md), [handbook](output/documentation/SC12_RevH_Handbook.pdf) |

Change voltage jumpers only with power disconnected. A missing cap disconnects port power, not its signal wire. Input mode changes use CAN software. Rail voltage readback uses the MCU ADC and factory voltage-reference calibration. External signal inputs remain digital; rail measurement does not add user analog-input or encoder support.

The compact variant is **44 × 48 mm**, using **45.1% less area** than the original 52 × 74 mm board. It retains all 140 fitted parts and electrical functions, with 79 parts underneath. Mounting holes, connectors and the LED move to suit the smaller outline. See the [compact layout review](docs/COMPACT_BOARD.md), [routing checks](reports/routing_rules.json), [all four copper layers](output/assembly/gerber_copper_review.pdf) and [connector details](docs/CONNECTORS.md). [Size comparison](output/review/size_comparison.png).

Ordering update: **0.30 mm minimum via holes, 1 oz outer / 0.5 oz inner copper**, and corrected CPL coordinates matching the Gerber origin. All component positions and trace geometry are retained. Re-upload the matching Gerber ZIP and CPL together. [Checks and order settings](docs/FABRICATION_OPTIONS.md).

The input connector-to-fuse and fuse-to-MOSFET routes are now **0.7 mm wide** (14 segments widened from 0.5 mm). The protected input and converter paths retain their reviewed clearance necks. Width, clearance, connectivity and ground-pour checks cover **all four layers**; see the [power-path review](docs/ORDER_READINESS.md).

| Copper layer | Role | PNG | SVG |
|---|---|---|---|
| Top | Components, signals and power | [PNG](output/review/gerber_top_copper.png) | [SVG](output/review/gerber_top_copper.svg) |
| Inner 1 | Ground plane | [PNG](output/review/gerber_inner_1_copper.png) | [SVG](output/review/gerber_inner_1_copper.svg) |
| Inner 2 | Ground with selected signals and low-current supply branches | [PNG](output/review/gerber_inner_2_copper.png) | [SVG](output/review/gerber_inner_2_copper.svg) |
| Bottom | Signals, power and ground | [PNG](output/review/gerber_bottom_copper.png) | [SVG](output/review/gerber_bottom_copper.svg) |

These views show the actual exported copper and drills. Inner layers are viewed from the top; the bottom is mirrored for an underside view.
