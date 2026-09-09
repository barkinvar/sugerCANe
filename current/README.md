# SC12 Rev F — current design

Three digital sensor inputs over CAN, with regulated **5 V / 12 V sensor power** and software-selectable **NPN, PNP, push-pull, floating detection and keeper**. Removable 2 mm jumpers select each port's power voltage. All components mount on the top.

**Hold a final hardware order.** Circuit consistency checks pass, but capacitive startup, fault reset and short-pulse behavior remain unresolved. No board has been built or tested; Rev F does not meet a requirement for one order with no later hardware corrections. See the [pre-order review](docs/ORDER_READINESS.md) and [validation evidence](docs/VALIDATION.md). This independent design uses its own protocol and drivers; it is not CTRE Phoenix or GrappleHook compatible.

![Rev F board](output/review/board_3d_final.png)

| Specification | Rev F |
|---|---|
| Board supply | 6–22 V DC |
| Sensor supplies | Regulated 5 V / 12 V; **300 mA shared per rail**, not per port |
| Signal targets | Positive 0–30 V; LOW ≤1.2 V, HIGH ≥2.4 V; common ground |
| Input setup | Software bias and active-state selection independently per channel |
| Protection | Reverse input, fuse/TVS, separate latching current limits for 5 V sensors and the 12 V boost input |
| Fault reset | Remove the fault, then cycle board power; stored output-capacitor energy is not instantly removed |
| Controller | STM32F042K6T6, TCAN3413; 1 Mbit/s classic CAN |
| Software | App 0.7.0, bootloader 1.0.0, hardware 6, protocol 4 |
| Servicing | CAN discovery, ID/settings and recoverable firmware upload; initial installation through SWD contacts |
| PCB / assembly | **52 × 64 mm**, four copper layers, 110 top SMT parts + nine hand-soldered parts + three loose caps |

Rev F replaces E's battery-fed buck-boost stage with a protected boost from the existing internal 5 V supply. Cheaper equivalent capacitors and more compact placement lower parts purchasing from about **$35.14 to $27.17 per board at ten boards**, and PCB area falls **8.6%**. PCB, assembly, freight and tax are extra. [Cost calculation and limitations](docs/COST_REDUCTION.md).

| What you want to do | Start here |
|---|---|
| Wire and configure a sensor | [Wiring](docs/WIRING.md), [input modes](docs/INPUT_MODES.md) |
| Understand the circuit | [Power and input design](DESIGN_PLAN.md), [schematic PDF](output/assembly/schematic.pdf) |
| Request a prototype quotation | [Factory instructions](docs/FACTORY_ORDER.md), [complete factory packet](order/RevF_SC12_Factory_Upload.zip) |
| Assemble and program | [Assembly](docs/ASSEMBLY.md), [unit fixture](docs/FIXTURE.md), [CAN service](docs/CAN_SERVICE.md) |
| Write robot code | [Examples/drivers](examples/README.md), [CAN protocol](docs/CAN_PROTOCOL.md) |
| Edit the board | [KiCad project](hardware/FRC_Sensor_CAN.kicad_pro), [PCB](hardware/FRC_Sensor_CAN.kicad_pcb), [interactive BOM](output/assembly/interactive_bom.html) |
| Design an enclosure | [STEP](output/mechanical/FRC_Sensor_CAN.step), [mechanical drawing](output/mechanical/mechanical_drawing.pdf) |
| Review or reproduce checks | [Validation](docs/VALIDATION.md), [power simulations](reports/electrical/boost_spice.json), [check summary](reports/release_checks.json), [tool setup](TOOLS.md) |
| Download everything | [Source/review ZIP](release/FRC_Sensor_CAN_RevF_SC12_Prototype.zip), [handbook](output/documentation/SC12_RevF_Handbook.pdf) |

Change voltage jumpers only with power disconnected. A missing cap disconnects port power, not its signal wire. Input mode changes use CAN software. Rail health is a coarse status indication, not calibrated voltage/current measurement. Analog readings and encoder decoding are not implemented.
