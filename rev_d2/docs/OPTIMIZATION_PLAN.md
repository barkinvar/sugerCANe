# SC12 optimization: implementation and qualification plan

**Updated 2026-09-08:** D-2 now delivers application 0.5.0 and bootloader 1.0.0, CAN commissioning/updating, laptop CLI/GUI and robot bridge adapters. Software tests pass; the board and controller workflow remain physically unqualified. Earlier planning/binaries are preserved in git at `7078fd9`; the neighboring Rev D remains firmware 0.4.0.

## What was implemented

| Work | Current evidence | Remaining gate |
|---|---|---|
| Separate bootloader/application | Fits existing 32 KiB STM32; protected 8 KiB boot region, 21 KiB app, manifest, redundant configuration | Real option-byte programming, handoff/interrupts and stack high-water |
| Discover/blink/persistent settings | Full 96-bit UID selection, readback, duplicate-ID simulation, explicit save/reset | Several physical blank and duplicate-ID boards; power-cycle verification |
| CAN update/recovery | Actual C engine tested through uploader; 2,148 simulated erase/program cut points, retries, bounds/CRC checks | Physical power cuts, bus-off and actual CAN timing; no rollback |
| Laptop and controller workflow | Python CLI and Tk GUI; real TCP fragmentation/revocation test with mock CAN; 2026 and 2027 alpha-7 adapters compile | End-to-end roboRIO/Systemcore and desktop adapter testing |
| Programming/test process | Combined factory image, protected programming script, per-UID acceptance-record tool and measurement template | Build fixture; measure pilot units and programming/test labor |
| Cost | Exact existing MPNs retained; purchase-quantity optimizer and assembly-fee sensitivity table generated | Allocated exact-MPN quotes, quantity/destination, lead time and full delivered price |

Use [CAN service](CAN_SERVICE.md) for protocol and operating instructions, [fixture](FIXTURE.md) for unit records and [cost reduction](COST_REDUCTION.md) for current numbers. Compilation and simulations do not close the physical gates. No PCB redesign or new bill-of-material component was needed for servicing.

## Lessons taken from LaserCAN and GrappleHook

LaserCAN separates its application and CAN bootloader while retaining SWD for initial installation/recovery. Its STM32F103 bootloader reserves 20 KiB and uses different vector handling; SC12 implements its own compact Cortex-M0 C engine and SRAM remap. Sources: pinned [bootloader](https://github.com/GrappleRobotics/LaserCAN/blob/5f444a38242da367e60176aecb3b1c7f20c92063/lasercan-bootloader/src/main.rs), [memory map](https://github.com/GrappleRobotics/LaserCAN/blob/5f444a38242da367e60176aecb3b1c7f20c92063/lasercan-bootloader/memory.x), [SWD instructions](https://github.com/GrappleRobotics/LaserCAN/tree/5f444a38242da367e60176aecb3b1c7f20c92063#flashing-a-new-bootloader) and [ST RM0091](https://www.st.com/resource/en/reference_manual/dm00031936.pdf).

GrappleHook demonstrates serial-based identification/settings, acknowledged offset uploads and a TCP-to-CAN robot path. SC12 provides those architectural capabilities with its own protocol and UID discovery. Our bridge remains inside running robot code, requires opt-in plus disabled state, and binds localhost for SSH access. Reference: pinned [management/upload code](https://github.com/GrappleRobotics/GrappleHook/blob/1e77ad3c29be867b026018c243e5ba6dfd9a01b2/grapple-hook/src-tauri/src/devices/mod.rs) and [roboRIO provider](https://github.com/GrappleRobotics/GrappleHook/blob/1e77ad3c29be867b026018c243e5ba6dfd9a01b2/grapple-hook/src-tauri/src/devices/roborio/daemon.rs). No reference implementation code was copied; both repositories carry GPL-3.0 notices. GrappleHook does not recognize SC12.

SC12 continues to serve three external industrial digital inputs. LaserCAN's integrated ranging sensor has different power/interface needs, so its board size and price are not like-for-like targets. SC12 retains regulated 5 V/12 V at 300 mA shared per rail, 6–22 V input target, top-side-only assembly, removable power caps and no slide switches.

## Next qualification loop

1. Program two pilot boards through SWD; verify protected pages and configuration retention. Measure boot/startup, watchdog recovery, vector interrupts, stack headroom and update time. Confirm the firmware truly returns to healthy telemetry after maintenance.
2. Test duplicate IDs, blank devices and mixed boot/application states on a real CAN network. Disconnect controller/host, interrupt power at erase/program/commit, corrupt images and force bus-off. Repeat uploads and verify configuration and bootloader integrity. Verify the controller bridge's permission loss and robot output interlock.
3. Exercise representative Banner/Omron models at cable ends: both rails independently/together to 300 mA, 6/12/22 V input, startup, shorts, brownout and enclosure temperature. Validate sensor residual-voltage limits rather than assuming all NPN sensors work.
4. Qualify terminal, mounting, harness and actual cap/retention compound under vibration/impact. An absent cap or disconnected sensor can resemble a valid inactive input; do not claim disconnect detection. Consider a passive CAN bypass harness for board replacement without opening the robot backbone.
5. Record all observations per UID and lot, correct failures, repeat affected tests and publish the measured limits. Complete the [validation matrix](VALIDATION.md) before production use.

## Cost decisions

Keep the reviewed circuit for the pilot. The software fits the current MCU without external memory or a USB connector. The small implemented purchasing correction saves $0.48 across five boards by buying cheaper ten-packs for three precision resistor MPNs; it does not materially change the ten-board price. Parts remain $34.69/board at ten and $32.23 at 25, before assembly/PCB/shipping.

The useful next step is an exact-MPN quote comparison at 5/10/25 boards. Standard fees charge all 46 SMT types; Economic charges extended types differently. The [scenario CSV](../bom/assembly_scenarios.csv) keeps unknown fees separate, with no assumed free feeders. At 25 boards Standard's parts-plus-setup/feeder/fixture subtotal is about $37.05/board versus $46.75 at ten, still excluding fabrication, placement, inspection, freight and other charges. Buying more boards lowers unit allocation while increasing cash for the order.

Connector redesign remains a candidate, not a substitution: compare complete latched-crimp harness cost including housings, contacts, crimp tools/labor, spare harnesses and strain relief. Verify mating cycles, wire gauge, current, polarity, footprints and vibration. Current terminals cost about $7.85/board at ten; the cheaper exact-MPN LCSC listing reviewed had zero stock and is not a basis for promised savings or delivery.

A converter redesign must compare the complete power circuit and requalify regulation through battery sag, thermal behavior and protection. Keep four copper layers and the critical switching/return layout until an actual quote demonstrates worthwhile savings. Preserve effective bulk/local capacitance and precision compensation values. A larger MCU or CAN-FD controller requires a separately justified feature and new hardware revision.

China delivery inside a month remains conditional on allocated components, review/manufacturing time, destination-specific air shipping and customs. No order has been placed, no supplier contacted and no delivered price/date confirmed by this work.
