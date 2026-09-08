# SC12 Revision E - software-selectable sensor inputs

Rev E adds independent **NPN, PNP, push-pull, floating-detection and keeper modes** through software. It removes the three input-bias solder selectors. The separate removable caps still choose 5 V or 12 V sensor power. [How to configure and wire inputs](docs/INPUT_MODES.md).

This project serves a similar purpose to CANdi, with its own firmware, CAN protocol and robot drivers. It is **not CTRE Phoenix or GrappleHook compatible**. Earlier revisions remain preserved; use this revision's complete hardware/firmware package together.

![Rev E board](output/review/board_3d_final.png)

| Item | Rev E |
|---|---|
| Purpose | Three industrial digital sensor inputs over classic CAN |
| Board input | 6–22 V DC at J1 |
| Sensor power | Regulated 5 V or 12 V; 300 mA shared per rail |
| Signals | Positive 0–30 V; LOW ≤1.2 V / HIGH ≥2.4 V design targets |
| Bias | Per-channel software pull-up, pull-down, off, float detection or keeper |
| MCU / CAN | STM32F042K6T6 + TCAN3413; 1 Mbit/s |
| Firmware | App 0.6.0, bootloader 1.0.0; hardware 5, protocol 4 |
| Setup/update | UID-based CAN discovery, ID/configuration, desktop GUI and recoverable CAN firmware upload; initial SWD installation |
| PCB | 52 × 70 mm, four copper layers; In1 ground; In2 ground plus three bias-control routes |
| Assembly | All components on top; 111 factory SMT parts and nine user-soldered through-hole parts; three loose power caps |

**Unbuilt engineering prototype.** The package includes CAD, firmware and engineering checks. Physical sensor compatibility, temperature, startup, EMC, surge, vibration and robot-bus behavior still require [qualification](docs/VALIDATION.md). Floating detection cannot distinguish a broken wire from a normally inactive open-collector output.

Compared with [D2](https://github.com/barkinvar/candi-clone/blob/main/rev_d2/README.md), E adds six small MOSFETs and seven resistors, reuses the comparator and input-protection circuit, and extends the board by 6 mm to retain top-side assembly. The power stage, connector family and critical converter/crystal routing remain preserved. [Circuit comparison](reports/variant_verification.json).

| Quantity | Parts purchase estimate per board |
|---|---:|
| 1 | $56.42 |
| 5 | $40.96 |
| 10 | $35.14 |
| 25 | $32.72 |

Includes supplier minimums, hand-fitted connectors/headers and loose caps; excludes PCB, assembly, attrition, freight and taxes. This feature adds about $0.45 per board at ten units. No delivered-price or one-month shipping commitment is established. [Cost basis](docs/COST_REDUCTION.md).

To commission a board, follow [assembly](docs/ASSEMBLY.md), install the combined factory image through the custom SWD contacts, then discover it through [CAN service](docs/CAN_SERVICE.md). The desktop window offers mode and active-state choices for each input. CLI example from this directory:

```sh
python host/can_service.py --bridge localhost:5810 configure \
  --uid UID --device 17 --invert 0 --debounce 2 \
  --modes npn,pnp,push-pull
```

Replace `UID` with the discovered serial. Sensor power is hardware-enabled; leave power caps off during initial bring-up and change them only with power disconnected. Input bias defaults off during reset/bootloader, then uses saved settings. Keep robot outputs inhibited during maintenance.

| Deliverable | Link |
|---|---|
| Native hardware | [PCB](hardware/FRC_Sensor_CAN.kicad_pcb), [schematic](hardware/FRC_Sensor_CAN.kicad_sch), [schematic PDF](output/assembly/schematic.pdf) |
| Factory upload | [Gerbers](order/RevE_SC12_Gerbers.zip), [SMT BOM](bom/Factory_BOM.csv), [JLCPCB BOM](bom/BOM_JLCPCB.csv), [CPL](output/assembly/CPL_JLCPCB.csv), [complete packet](order/RevE_SC12_Factory_Upload.zip) |
| Hand-fitted parts | [BOM](bom/Hand_solder_BOM.csv), [caps](bom/ACCESSORIES.csv) |
| Wiring and software | [Wiring](docs/WIRING.md), [input modes](docs/INPUT_MODES.md), [firmware](firmware/README.md), [drivers](examples/README.md), [protocol](docs/CAN_PROTOCOL.md) |
| Mechanical | [STEP](output/mechanical/FRC_Sensor_CAN.step), [drawing](output/mechanical/mechanical_drawing.pdf), [connector details](docs/CONNECTORS.md) |
| Review | [Interactive BOM](output/assembly/interactive_bom.html), [checks](reports/release_checks.json), [handbook](output/documentation/SC12_RevE_Handbook.pdf) |
| Source/review archive | [ZIP](release/FRC_Sensor_CAN_RevE_SC12_Prototype.zip), [manifest](release/manifest.json) |

[Repository revision comparison](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md) · [Tools](TOOLS.md) · [Sources and licenses](docs/SOURCES_AND_LICENSES.md)
