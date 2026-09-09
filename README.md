# SC12 — sensor inputs over CAN

A compact interface for **three NPN, PNP or logic sensors** on an FRC robot. Each port has a removable **5 V / 12 V power jumper**; input type is configured in software. CAN provides sensor readings, device-ID changes and recoverable firmware updates.

**Start with [Rev F in `current/`](current/README.md).** It is an unbuilt engineering prototype, with [physical qualification still pending](current/docs/VALIDATION.md). It uses its own protocol and drivers; it is not compatible with CTRE Phoenix or GrappleHook.

**Hold a final hardware order.** Rev F has unresolved capacitive-startup, fault-reset and short-pulse findings. It has never been physically tested and does not meet a requirement for a single order with no later hardware corrections. See the [pre-order review](current/docs/ORDER_READINESS.md) and [simulation results](current/docs/VALIDATION.md#manufacturer-model-transient-screen).

![SC12 Rev F](current/output/review/board_3d_final.png)

| Current design | Detail |
|---|---|
| Board input | 6–22 V DC |
| Sensor power | Regulated 5 V / 12 V; 300 mA shared per rail |
| Signals | Positive 0–30 V targets; NPN / PNP / push-pull / floating detection / keeper |
| Size and assembly | 52 × 64 mm, four copper layers; **all components on top** |
| User assembly | Six terminals, three headers and three removable caps |
| Parts estimate | **$27.17 per board at 10 boards**; $47.80 for one board, including minimum packs |
| Cost exclusions | PCB, assembly, freight, tax and testing; no factory quotation yet |

Rev F saves about **$8 in parts per board at ten boards** compared with E and reduces PCB area by **8.6%**. [What changed and how the costs were calculated](current/docs/COST_REDUCTION.md).

## Find what you need

| Task | Link |
|---|---|
| Connect and configure sensors | [Wiring](current/docs/WIRING.md) · [input modes](current/docs/INPUT_MODES.md) |
| Understand the power circuit | [Circuit explanation](current/DESIGN_PLAN.md) · [schematic PDF](current/output/assembly/schematic.pdf) |
| Assemble or request a quote | [Factory instructions](current/docs/FACTORY_ORDER.md) · [factory packet](current/order/RevF_SC12_Factory_Upload.zip) |
| Program or update over CAN | [CAN service](current/docs/CAN_SERVICE.md) · [robot drivers](current/examples/README.md) |
| Review CAD and tests | [Current design](current/README.md) · [power simulations](current/docs/VALIDATION.md#manufacturer-model-transient-screen) · [validation summary](current/reports/release_checks.json) |
| Download the full design | [Rev F source/review ZIP](current/release/FRC_Sensor_CAN_RevF_SC12_Prototype.zip) |

## Why the revisions differ

| Revision | Made for | Main difference |
|---|---|---|
| A | Original four-input concept | 96 × 96 mm baseline |
| B | Smaller, configurable three-input board | 60 × 68 mm; physical power/bias/threshold settings |
| B2 | Factory assembly of B at lower parts cost | Equivalent passives and sourcing; same B circuit |
| C Lite | Simpler, smaller digital interface | 52 × 56 mm; 5 V and protected battery power; fewer parts |
| D SC12 | Industrial sensors needing regulated 12 V | 52 × 64 mm; regulated 5 V / 12 V and rail-health reporting |
| D2 SC12 | Lower-cost assembly and CAN servicing | Hand-fitted terminals, removable voltage jumpers, CAN setup/update |
| E SC12 | Mixed sensor types without bias solder settings | Software NPN/PNP/push-pull/float/keeper; 52 × 70 mm |
| **F SC12 — current** | **Keep E's features at lower cost** | **Protected boost from internal 5 V, cheaper passives, 52 × 64 mm** |

[Revision details](REVISIONS.md) · [Historical downloads](archive/README.md). Use hardware, firmware and instructions from the same revision.

## Folder map

```text
current/                 The maintained Rev F design
  hardware/              Native KiCad, local libraries and circuit model
  firmware/              MCU application, bootloader and tests
  host/ + examples/      CAN setup tools and robot drivers
  bom/ + order/          Parts lists and factory upload packages
  docs/                  Wiring, assembly, servicing and qualification
  output/ + reports/     Fabrication exports, drawings and check evidence
  scripts/ + tools/      Reproduction scripts and pinned dependencies
  release/               Complete downloadable Rev F package
archive/                 Original older release/order ZIPs and checksums
```

Earlier expanded project copies and unused experiments were removed from the current tree. Historical packages are unchanged, and previous sources remain in Git history. [Contributing and generated-file policy](CONTRIBUTING.md).
