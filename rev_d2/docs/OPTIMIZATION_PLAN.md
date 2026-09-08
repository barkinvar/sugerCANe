# SC12 optimization plan: lessons from LaserCAN

**Planning document, 2026-09-08. No proposed feature below is implemented by this change.** The delivered D-2 firmware remains 0.4.0 / protocol v3: SWD flashing, UART persistent setup and volatile CAN input configuration. CAN discovery, persistent CAN-ID changes, a CAN bootloader and a roboRIO maintenance bridge are missing today.

The objective is a board that teams can configure and update through the robot's CAN wiring, with lower delivered cost and demonstrated FRC reliability. Start with D-2's existing hardware; prove the software and manufacturing opportunities before choosing a circuit redesign. Retain three industrial digital inputs, regulated 5 V / 12 V at 300 mA shared per rail, top-side-only assembly, no sliders and user-fitted through-hole parts. The current prototype is unbuilt.

## Lessons and limits of the reference

LaserCAN separates its application and CAN bootloader, retaining SWD contacts for initial programming/recovery. Its STM32F103 bootloader reserves 20 KiB; that allocation and its interrupt-vector handling are not a direct fit for our STM32F042. See the pinned [bootloader](https://github.com/GrappleRobotics/LaserCAN/blob/5f444a38242da367e60176aecb3b1c7f20c92063/lasercan-bootloader/src/main.rs), [memory layout](https://github.com/GrappleRobotics/LaserCAN/blob/5f444a38242da367e60176aecb3b1c7f20c92063/lasercan-bootloader/memory.x) and [programming instructions](https://github.com/GrappleRobotics/LaserCAN/tree/5f444a38242da367e60176aecb3b1c7f20c92063#flashing-a-new-bootloader).

GrappleHook addresses identification and ID changes by device serial. Its newer upload path uses offsets and request acknowledgements. The roboRIO provider bridges TCP to CAN; its deployment mode stops robot code and later restarts it. Our tool must make maintenance transitions explicit and verify recovery after disconnects. Sources: [management/upload code](https://github.com/GrappleRobotics/GrappleHook/blob/1e77ad3c29be867b026018c243e5ba6dfd9a01b2/grapple-hook/src-tauri/src/devices/mod.rs), [roboRIO provider](https://github.com/GrappleRobotics/GrappleHook/blob/1e77ad3c29be867b026018c243e5ba6dfd9a01b2/grapple-hook/src-tauri/src/devices/roborio/daemon.rs).

These are architectural references. GrappleHook's current device support does not recognize SC12, and SC12 must retain its own identifiers and protocol. Both reference repositories carry GPL-3.0 notices; this plan imports no code. Any later code reuse must retain its applicable notices and license requirements. Their integrated distance sensor also serves a different electrical function from our three externally powered industrial inputs; its size or cost is not an equivalent SC12 target.

## Priorities and completion gates

| Order | Work and expected benefit | Completion gate |
|---|---|---|
| 1 | Define service protocol and prove STM32 memory budget; avoid an unnecessary MCU/PCB change | Bootloader/application link successfully in separate regions, with documented RAM/stack allowance and interrupt handoff |
| 2 | CAN discovery, identify LED, persistent ID/inversion/debounce; eliminate normal UART setup | Several blank and duplicate-ID boards can be individually selected, configured and verified after power cycling |
| 3 | Recoverable CAN firmware update; eliminate normal SWD reflashing | Interrupted/corrupt transfers never boot an incomplete image; the same board remains discoverable for retry |
| 4 | Laptop tool and robot bridge; make the features usable through existing wiring | End-to-end discovery, ID change and update through a real roboRIO, including cable loss and maintenance exit |
| 5 | Physical qualification and repeatable programming/test fixture; reduce field failures and rework | Rail, CAN, power-cut, sensor, thermal and mechanical tests recorded for the prototype lot |
| Parallel | Exact-MPN factory quotes and connector/harness study; reduce delivered cost | Itemized totals for identical quantities and scope, with stock, test labor and delivery assumptions visible |
| After evidence | Select any connector, converter or MCU redesign | Savings justify redesign/qualification effort and the affected requirements still pass |

Protocol design, memory proof and quote preparation can begin together. Freeze the protocol before integrating uploader and device. Physical qualification precedes production. Quantity, destination and exact sensor models are required for final quotes and bench limits.

## 1. CAN commissioning and maintenance

Use the STM32's full 96-bit unique ID as the permanent service identity, separate from the changeable 0-63 CAN ID. Initialize a service receive path on unconfigured boards while suppressing normal telemetry. Define bounded discovery and collision resolution so multiple blank or duplicate-ID boards do not transmit conflicting replies indefinitely; a shortened UID hash or random delay alone is not a uniqueness guarantee.

Provide discover/info, blink, set ID, set inversion/debounce, explicit save, enter bootloader and update-status operations. Target destructive state changes to one full UID and a transaction/session. Confirm ID availability, acknowledge the operation and rediscover the same UID at its new ID. Duplicate/lost requests must not repeatedly erase flash. Reuse the two redundant configuration pages with CRC and commit-last writes; save only on explicit changes, then verify persistence after reset. Preserve existing broadcast-disable behavior and keep read operations free of writes/resume actions.

Measure normal CAN traffic before optimizing it. The current schedule sends 131 frames/s: 100 status, 20 counter, 10 diagnostic and one identity frame. At an illustrative 160 bits per fully stuffed extended eight-byte frame, that is about 2.1% of a 1 Mbit/s bus per board before faults or retransmissions. Later evaluate configurable 10/20/50 ms status periods and slower diagnostics, preserving the 1 ms sampler. Bound driver freshness timeouts to the selected period and measured jitter; retain today's default until verified.

## 2. Compact bootloader and interrupted-update recovery

The [current build](../reports/firmware-build.log) uses 6,148 bytes of flash. The MCU has 32 KiB total, with the last two 1 KiB pages already assigned to configuration. This leaves a plausible budget for a small C bootloader, but compilation and measured stack use must establish fit.

One candidate allocation is **8 KiB bootloader + 21 KiB application + 1 KiB image manifest + 2 KiB configuration**. This is a planning allocation, not the current linker layout. Reserve SRAM for relocated interrupt vectors and a validated boot request. Implement the Cortex-M0 SRAM vector-remap/handoff described by [ST RM0091](https://www.st.com/resource/en/reference_manual/DM00031936-.pdf), including stack, interrupts, clocks and watchdog state. Verify flash write-protection granularity before fixing the layout. Normal CAN updates must have no erase/write path into the bootloader, option bytes or configuration pages.

Use one application image for the first implementation. Validate product/hardware identifier, format, size, vector bounds and whole-image CRC. Invalidate and read back the boot-valid marker before erasing application pages; write a new valid marker only after full flash readback and verification. Give chunks explicit session/offset information, bounded retries and acknowledgements. Handle duplicates without advancing twice; reject gaps, stale sessions and out-of-range writes. Pace transfers around flash erase/program stalls and other CAN traffic.

After interrupted flashing, stay in the protected bootloader and accept a fresh upload. Automatic rollback to a previous image is outside this first design. Add a bounded boot-time recovery opportunity and repeated-watchdog-failure recovery so entry does not depend entirely on a working application. Preserve configuration across updates and report bootloader/application versions separately. CRC detects corruption; it does not authenticate an uploader. Restrict the tool/bridge to explicit trusted maintenance sessions, and do not claim signed-update security.

First installation still uses the existing SWD contacts. Deliver distinct factory-combined and CAN-application update files with manifests, and prevent the tool from confusing them. Preserve the original 0.4.0 package; migrate existing boards through SWD once, since that firmware cannot install a CAN bootloader remotely. No extra USB connector or external flash is planned. Reconsider the MCU only if the measured memory budget or a separately chosen CAN-FD requirement demands it.

## 3. Tooling and robot integration

Implement a reusable host protocol library and command-line tool first, with a SocketCAN/USB-CAN transport for development and a roboRIO TCP/CAN bridge for normal team use. Both transports need the same transaction and recovery tests; a SocketCAN-only tool does not fulfill the robot-connected workflow. Keep transfer buffers, receive work and bus utilization bounded.

The user flow is: connect to controller, discover, select serial, blink to confirm, edit/save settings or select firmware, verify result. Show old/new CAN ID, hardware/application/bootloader versions and actionable failures. A transfer progress bar reaching 100% is insufficient: reconnect to the same UID and verify the running version. Add a small GUI after this path works.

Require an explicit maintenance session with robot enable inhibited; enforce that at the bridge/controller, since the sensor does not independently know Driver Station enable state. Measurements are unavailable during flashing, and sensor power remains hardware-enabled. Restore and verify normal robot-code operation after bridge exit, timeout and disconnection. First target the pinned 2026 environment, then add a separately compiled/tested 2027 adapter with explicit bus selection. [WPILib's 2027 changes](https://docs.wpilib.org/en/latest/docs/yearly-overview/yearly-changelog.html) already replace integer CAN ports with `CANPort`; do not freeze the implementation to the earlier forum example. SC12 remains classical CAN and must use a compatible bus.

## 4. Cost reductions in order of expected return

The dated [D-2 purchasing model](COST_REDUCTION.md) gives $34.69/board at ten: $26.10 SMT plus $8.59 manually fitted parts/caps. PCB, assembly, programming/test, freight and tax are additional. The Standard-service setup/feeder/fixture allowance is about $12.06/board at ten before placement and other charges. These are baseline estimates, not new quotations or a confirmed sub-$50 delivered price.

| Candidate | Action and decision rule |
|---|---|
| Factory service and batch size | Compare Economic and Standard SMT-only quotes at 5/10/25 boards using identical exact MPNs. Include PCB, setup, feeders, attrition, inspection, programming/test and freight. Resolve stock allocation; LCSC stock alone is insufficient. |
| Connector/harness cost | The six terminals account for about $7.85/board at ten. Compare the existing parts against a keyed, latched crimp family using the complete cost of headers, housings, contacts, crimp labor/tools and spare harnesses. Verify wire gauge, current, strain relief, mating cycles, polarity and vibration before adoption. |
| Feeder/part consolidation | Match electrically identical passives and verify factory Basic/Extended classifications. At the cited Standard rate, removing five MPN types saves only $7.65/order, about $0.77/board at ten. Do not change precision or compensation values merely to share a feeder. [Fee basis](https://jlcpcb.com/help/article/pcb-assembly-price). |
| Assembly and test labor | Keep all SMT on top and hand-fit the nine through-hole parts. Use a reusable SWD/CAN fixture and one scripted report per UID. CAN setup reduces repeated service access; initial programming and functional testing still cost time. |
| Power-stage redesign | The present 12 V converter is about $5.42/board at ten. Compare any alternative using total converter circuit cost, availability, losses, PCB area and qualification effort. Preserve regulated output through 6-22 V input, current protection and startup behavior. |
| MCU redesign | The present MCU is about $3.28/board at ten. First measure the bootloader/application budget. A cheaper chip that adds a controller, regulator, external memory or difficult assembly may increase total cost. |

No specific replacement connector, converter or MCU is approved by this plan. Retain four copper layers and the reviewed power layout for the first prototypes. Smaller PCB area or fewer copper layers must show a quoted saving while preserving return paths, thermal behavior and access. Retain effective bulk capacitance and local bypassing. The internal 5 V rail supplies logic and converter bias as well as the 5 V sensor branch. Supplying sensors directly from the battery would change the regulated-12 V product requirement; assess that only as a separate variant.

## 5. Reliability and release evidence

Extend the existing [qualification plan](VALIDATION.md) with these service-specific gates:

- Inject power loss at manifest invalidation, every erase/program boundary and final commit; test lost/duplicate/reordered chunks, wrong hardware images, oversize files, bus-off and host disappearance. Confirm recovery and preserved configuration. Exercise blank, duplicate-ID and mixed application/bootloader nodes.
- Measure boot/startup time, flash/RAM/stack headroom, update duration and bus utilization. Verify CAN/SysTick/UART/PVD interrupts and watchdog resets after the bootloader handoff on the real STM32, not only in host mocks. Acceptance requires reliable return to healthy telemetry and no false counts.
- Test representative sensors at their cable ends, both rails separately/together up to 300 mA, 6/12/22 V input, brownouts, startup and shorts. Record converter/inductor/input-device temperatures in the intended enclosure. MCU temperature alone cannot qualify the power stage.
- Test the actual jumper caps, retention compound, terminals, mounting and harness under vibration/impact. An open power cap or disconnected sensor may appear as a valid inactive input; show that limitation. Assess an external CAN bypass harness for board replacement, preserving termination and short branches.
- Build a pilot with enough units for normal measurements, repeatability and a dedicated fault-test unit. Record component lots, MCU UID, images/hashes, protection settings, rail/input/CAN results and programming/test time. Quotes must distinguish assembled-only boards from programmed/tested boards; production size and a one-month arrival date require allocated parts and a destination-specific schedule.

Qualify the new features for product use only after the service tests and applicable physical gates pass. Update firmware/protocol capability reporting and drivers together; do not mark older binaries as CAN-updatable. Refresh the READMEs, wiring/assembly instructions, factory programming scope and release manifest with the implemented behavior and remaining limitations. Hardware changes require a separately traceable revision and matching native CAD/BOM/manufacturing evidence.
