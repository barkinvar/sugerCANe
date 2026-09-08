# FRC Sensor CAN

A sensor-to-CAN interface for FRC robots: read industrial photoelectric sensors and 3.3 V / 5 V digital signals, and power sensors from either protected battery voltage or a regulated 5 V rail. The design uses an STM32F042 CAN controller and a separate TCAN3413 transceiver, with its own documented Team Use CAN protocol.

**Rev C Lite is the new simplified design: 52 × 56 mm, 89 fitted parts, three inputs and no plug-in jumpers.** A, B and B-2 remain available. All four are unbuilt prototypes with native KiCad, BOMs, firmware, examples, manufacturing exports and computational checks.

![Rev C Lite](rev_c/output/review/board_3d_final.png)

[Rev C Lite guide](rev_c/README.md) · [BOM](rev_c/bom/BOM_grouped.csv) · [What was removed](rev_c/docs/SIMPLIFICATION.md) · [Prototype ZIP](rev_c/release/FRC_Sensor_CAN_RevC_Lite_Prototype.zip)

Rev C reduces fitted parts by **38.2%** and PCB area by **28.6%** versus B/B-2. It retains horizontal Weidmüller terminals and 5 V/battery sensor power, while removing the boost converter, software power control, rail monitoring and selectable thresholds. Supply becomes **6–22 V**. The dated parts estimate is **$43.90**, before PCB/assembly/shipping/tax. See the [wiring guide](rev_c/docs/WIRING.md), [handbook](rev_c/output/documentation/FRC_Sensor_CAN_RevC_Lite_Handbook.pdf) and [factory quotation packet](rev_c/order/RevC_Lite_Factory_Upload.zip).

Earlier revisions:


| | Rev A | Rev B | Rev B-2 |
|---|---|---|---|
| Preview | ![Rev A](output/review/board_3d_final.png) | ![Rev B](rev_b/output/review/board_3d_final.png) | ![Rev B-2](rev_b2/output/review/board_3d_final.png) |
| Overview | [Rev A guide](REV_A.md) | [Rev B guide](rev_b/README.md) | [Rev B-2 guide](rev_b2/README.md) |
| PCB size | 96 × 96 mm | 60 × 68 mm | 60 × 68 mm |
| Sensor channels | 4 | 3 | 3 |
| Input target | 6–18 V | 5–22 V | 5–22 V |
| External terminals | Würth 5.00 mm | Weidmüller LSF-SMT 3.50 /90 | Same horizontal Weidmüller parts |
| Assembly focus | Hand assembly / heatbed | Compact hand assembly / heatbed | Turnkey SMT + THT assembly |
| Dated parts estimate | $49.61 | $59.30 | $46.35 |
| BOM | [Purchasing guide](bom/README.md) | [DigiKey BOM](rev_b/bom/BOM_grouped.csv) | [Turnkey BOM](rev_b2/bom/BOM_turnkey.csv) |
| Editable design | [KiCad project](hardware/FRC_Sensor_CAN.kicad_pro) | [KiCad project](rev_b/hardware/FRC_Sensor_CAN.kicad_pro) | [KiCad project](rev_b2/hardware/FRC_Sensor_CAN.kicad_pro) |
| Build package | [Rev A ZIP](release/FRC_Sensor_CAN_RevA_Prototype.zip) | [Rev B ZIP](rev_b/release/FRC_Sensor_CAN_RevB_Prototype.zip) | [Rev B-2 ZIP](rev_b2/release/FRC_Sensor_CAN_RevB2_Prototype.zip) |

Prices are dated component estimates, including loose shunts where used; they exclude PCB fabrication, assembly labor, MOQ/attrition, shipping and taxes. See the [B-2 cost model](rev_b2/docs/COST.md) for estimated assembled-board orders. The [factory packet](rev_b2/order/RevB2_Factory_Upload.zip) is ready for quotation and placement review; it is not a completed factory order or physical qualification.

## Choose the matching documentation

Use each revision's PCB, BOM, firmware and wiring guide together. The root `hardware/`, `firmware/`, `bom/`, `docs/` and `output/` directories belong to **Rev A**; Rev B, B-2 and C are self-contained under their own directories.

- [Revision history and comparison](REVISIONS.md), including the archived angled-connector Rev B iteration.
- [Rev A handbook](output/documentation/FRC_Sensor_CAN_RevA_Handbook.pdf), [Rev B handbook](rev_b/output/documentation/FRC_Sensor_CAN_RevB_Handbook.pdf), [Rev B-2 handbook](rev_b2/output/documentation/FRC_Sensor_CAN_RevB2_Handbook.pdf).
- [Rev A wiring](docs/WIRING.md), [Rev B wiring and pogo map](rev_b/docs/WIRING.md), [Rev B-2 factory instructions](rev_b2/docs/FACTORY_ORDER.md).
- [Tools and rebuild workflow](TOOLS.md), [repository and generated-file policy](CONTRIBUTING.md).

## Horizontal push-in connectors

Rev B, B-2 and C use **1824420000**, LSF-SMT 3.50/02/90 3.5SN BK TU, for the three 2-pole power/CAN terminals, and **1824430000**, LSF-SMT 3.50/03/90 3.5SN BK TU, for the three sensor terminals. `/90` is horizontal wire entry, parallel to the PCB. These are THT/THR terminals despite “SMT” in the series name.

The current renders use **manufacturer STEP geometry** aligned to the PCB pins, with project display colors. Earlier box-shaped connector models were only simplified envelopes. See the [connector verification and model provenance](rev_b/docs/CONNECTORS.md). Allow a conservative **60 × 76.1 mm assembly envelope**, plus wires and button access, for Rev B/B-2; Rev C reserves 52 × 64.1 mm.

## Operating targets and validation

Each revision has separate shared 5 V and VBAT sensor rails, with a **300 mA design budget per rail across all ports**. VBAT follows the input; it does not create regulated 12 V or 24 V. Battery sag can stop a sensor that requires at least 10 V even while the interface continues running.

Inputs target positive 0–30 V signals with common ground. A/B/B-2 have selectable logic (LOW ≤0.8 V / HIGH ≥2.4 V) and industrial (LOW ≤4 V / HIGH ≥7 V) thresholds. Rev C has fixed LOW ≤1.2 V / HIGH ≥2.4 V targets under its documented component/leakage budgets. The board does not promise 1.8 V recognition, analog acquisition, IO-Link or CTRE Phoenix/Tuner compatibility. This is an original design, not a CTRE product.

ERC/DRC, exported-copper connectivity, calculations and software tests are recorded under each revision's reports. Physical surge, thermal, sensor, CAN and programming tests remain pending. Start with the matching qualification guide before using a board on a robot. Component availability and prices must be checked again when purchasing.

No blanket license has been selected for original project material. Third-party notices remain in each revision's `licenses/` and [sources documentation](docs/SOURCES_AND_LICENSES.md).
