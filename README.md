# sugarCANe — sensor inputs over CAN

A compact interface for **three NPN, PNP or logic sensors** on an FRC robot. Each port has a removable **5 V / 12 V power jumper**; input type is configured in software. CAN provides sensor readings, device-ID changes and recoverable firmware updates.

**sugarCANe** is the product name; SC12 Rev H remains the hardware identity. The underside carries a large original pixel-cane illustration and **sugarCANe** wordmark, with no other text. [Bottom artwork render](current/output/review/board_bottom.png).

**Start with [Rev H in `current/`](current/README.md).** It is an unbuilt engineering prototype, with [physical qualification still pending](current/docs/VALIDATION.md). It uses its own protocol and drivers; it is not compatible with CTRE Phoenix or GrappleHook.

Rev H adds one RGB status LED on the right, with space for a printed light duct, and a recessed female programming socket for small batches. It retains G's protected sensor supplies, CAN fault reset and rail measurements. See [the engineering review](current/docs/ORDER_READINESS.md) for the evidence and remaining physical tests.

Fresh checks pass for the native PCB, firmware, all ten input-transient cases, eight standalone power cases and sixteen firmware waveform replays. Full combined power startup remains incomplete; the release stays on HOLD. See the [check summary](current/reports/release_checks.json).

![SC12 Rev H](current/output/review/board_3d_final.png)

| Current design | Detail |
|---|---|
| Board input | 6–22 V DC |
| Sensor power | Regulated 5 V / 12 V; 300 mA shared per rail |
| Supply protection | Current limiting for shorts to ground; **5 V-to-12 V cross-connections are unsupported** |
| Signals | Positive 0–30 V targets; NPN / PNP / push-pull / floating detection / keeper |
| Size and assembly | 52 × 74 mm, four copper layers; **all components on top** |
| User assembly | Six terminals, three voltage headers, one service socket and three removable caps |
| Parts estimate | **$28.99 per board at 10 boards**; $55.14 for one board, including minimum packs |
| Cost exclusions | PCB, assembly, freight, tax and testing; no factory quotation yet |

RGB diagnostics and socket programming add approximately **$0.18 per board in parts at ten boards** versus G. Assembly and the reusable programmer are separate. [Cost basis](current/docs/COST_REDUCTION.md).

## Find what you need

| Task | Link |
|---|---|
| Connect and configure sensors | [Wiring](current/docs/WIRING.md) · [input modes](current/docs/INPUT_MODES.md) |
| Understand the power circuit | [Circuit explanation](current/DESIGN_PLAN.md) · [schematic PDF](current/output/assembly/schematic.pdf) |
| Assemble or request a quote | [Factory instructions](current/docs/FACTORY_ORDER.md) · [package status](current/order/README.md) |
| Read LED / choose a programmer | [Status and programming](current/docs/STATUS_AND_PROGRAMMING.md) |
| Program or update over CAN | [CAN service](current/docs/CAN_SERVICE.md) · [robot drivers](current/examples/README.md) |
| Review CAD and tests | [Current design](current/README.md) · [power simulations](current/docs/VALIDATION.md#manufacturer-model-transient-screen) · [validation summary](current/reports/release_checks.json) |
| Download the full design | [Rev H source/release status](current/release/README.md) |

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
| F SC12 | Keep E's features at lower cost | Input-protected boost, cheaper passives; startup/short findings remain in the archive |
| G SC12 | Resolve the power-path findings and enable CAN recovery | Output eFuse, controlled inrush, rail ADCs, default-off enables; 52 × 74 mm |
| **H SC12 — current** | **Visible diagnostics and inexpensive programming for ten boards** | **One RGB LED, buffered data, ordinary 2.54 mm service header; same 52 × 74 mm, top-side assembly** |

[Revision details](REVISIONS.md) · [Historical downloads](archive/README.md). Use hardware, firmware and instructions from the same revision.

## Folder map

```text
current/                 The maintained Rev H design
  hardware/              Native KiCad, local libraries and circuit model
  firmware/              MCU application, bootloader and tests
  host/ + examples/      CAN setup tools and robot drivers
  bom/ + order/          Parts lists and factory package status
  docs/                  Wiring, assembly, servicing and qualification
  output/ + reports/     Fabrication exports, drawings and check evidence
  scripts/ + tools/      Reproduction scripts and pinned dependencies
  release/               Release package status
archive/                 Original older release/order ZIPs and checksums
```

Earlier expanded project copies and unused experiments were removed from the current tree. Historical packages are unchanged, and previous sources remain in Git history. [Contributing and generated-file policy](CONTRIBUTING.md).

The current layout has rounded corners, aligned input-bias transistors, a recessed female debug socket, improved edge clearances and visible voltage-selector/input labels. Routing cleanup removes unnecessary zigzags and standardizes long runs to 45° bends, with unchanged component positions, vias and trace widths. It remains 52 × 74 mm with top-side assembly. See [all four copper layers](current/output/assembly/gerber_copper_review.pdf) and [connector details](current/docs/CONNECTORS.md).
