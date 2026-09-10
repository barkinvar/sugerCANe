# sugarCANe — sensor inputs over CAN

[GitHub repository: barkinvar/sugerCANe](https://github.com/barkinvar/sugerCANe)

A compact interface for **three NPN, PNP or logic sensors** on an FRC robot. Each port has a removable **5 V / 12 V power jumper**; input type is configured in software. CAN provides sensor readings, device-ID changes and recoverable firmware updates.

**sugarCANe** is the product name; SC12 Rev H remains the hardware identity. The underside carries a large original pixel-cane illustration on a raised island with a stepped underside and a bold pixel **sugarCANe** wordmark, with no other text. [Bottom artwork render](current/output/review/board_bottom.png).

**Start with [Rev H in `current/`](current/README.md).** It is an unbuilt engineering prototype, with [physical qualification still pending](current/docs/VALIDATION.md). It uses its own protocol and drivers; it is not compatible with CTRE Phoenix or GrappleHook.

Rev H adds one RGB status LED on the right, with space for a printed light duct, and a recessed female programming socket for small batches. It retains G's protected sensor supplies, CAN fault reset and rail measurements. See [the engineering review](current/docs/ORDER_READINESS.md) for the evidence and remaining physical tests.

**Assembly plan:** JLC fits all 130 SMT parts, including the MCU, RGB LED and C1. You solder only six terminal blocks, three voltage headers and the service socket. C1 now uses a reviewed high-reflow capacitor and smaller footprint; its previous peak-temperature conflict is resolved. The exact MCU is available from DigiKey but must be procured into JLC’s parts library before assembly. Final simulation approval and factory quotation remain pending. [Ordering steps](current/docs/FACTORY_ORDER.md) · [check summary](current/reports/release_checks.json).

![SC12 Rev H](current/output/review/board_3d_final.png)

| Current design | Detail |
|---|---|
| Board input | 6–22 V DC |
| Sensor power | Regulated 5 V / 12 V; 300 mA shared per rail |
| Supply protection | Current limiting for shorts to ground; **5 V-to-12 V cross-connections are unsupported** |
| Signals | Positive 0–30 V targets; NPN / PNP / push-pull / floating detection / keeper |
| Size and assembly | 52 × 74 mm, four copper layers; **all components on top** |
| User assembly | Six terminals, three voltage headers, one service socket and three removable caps |
| Parts estimate | **$25.68 per board at 10 boards** before SMT attrition; **$26.55** with conservative allowance |
| Cost exclusions | PCB, assembly, freight, tax and testing; no factory quotation yet |

The updated supplier estimate is $3.31 lower per board than the preceding $28.99 estimate, before SMT attrition. MCU price remains provisional until sourced. Assembly and the reusable programmer are separate. [Cost basis](current/docs/COST_REDUCTION.md).

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

Clone the repository and enter the maintained design:

```sh
git clone https://github.com/barkinvar/sugerCANe.git
cd sugerCANe/current
```

See [tools and reproduction](current/TOOLS.md) for setup and build instructions.

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

The 52 × 74 mm board has top-side assembly, rounded corners, improved edge clearances, a recessed debug socket and labelled voltage selectors. Its 1,530 straight track segments and 242 vias satisfy the [routing rules](current/docs/ROUTING_RULES.md). All-layer cleanup removes pad overshoots, redundant paths and stubs, with explicit chamfered branches. Ground pours use checked widths and gaps; see the [ground cleanup](current/output/review/ground_pours.png). Component positions and artwork are unchanged. See [before/after details](current/output/review/routing_contacts.png), [all four copper layers](current/output/assembly/gerber_copper_review.pdf) and [connector details](current/docs/CONNECTORS.md).

The input connector-to-fuse and fuse-to-MOSFET routes are now **0.7 mm wide** (14 segments widened from 0.5 mm). The protected input and converter paths retain their reviewed clearance necks. Width, clearance, connectivity and ground-pour checks cover **all four layers**; see the [power-path review](current/docs/ORDER_READINESS.md).

| Copper layer | Role | PNG | SVG |
|---|---|---|---|
| Top | Components, signals and power | [PNG](current/output/review/gerber_top_copper.png) | [SVG](current/output/review/gerber_top_copper.svg) |
| Inner 1 | Ground plane | [PNG](current/output/review/gerber_inner_1_copper.png) | [SVG](current/output/review/gerber_inner_1_copper.svg) |
| Inner 2 | Ground with selected signals and low-current supply branches | [PNG](current/output/review/gerber_inner_2_copper.png) | [SVG](current/output/review/gerber_inner_2_copper.svg) |
| Bottom | Signals, power and ground | [PNG](current/output/review/gerber_bottom_copper.png) | [SVG](current/output/review/gerber_bottom_copper.svg) |

These views show the actual exported copper and drills. Inner layers are viewed from the top; the bottom is mirrored for an underside view.
