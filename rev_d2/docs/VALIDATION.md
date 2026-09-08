# Rev D-2 validation and release boundary

**No Rev D-2 prototype has been assembled, powered or tested.** The files support engineering review and prototype fabrication. The production/competition qualification gates below remain open, even when every automated check passes.

## Automated evidence

The release contains native KiCad electrical/design-rule reports, explicit pin-model/schematic/PCB parity, placement/selector/programming-contact checks, manufacturing-file parsing and copper checks, host firmware tests, and Java/C++/Python protocol tests. These check design consistency and modeled behavior. Mocked peripheral tests do not prove STM32 timing or CAN electrical operation.

Electrical checks sweep input-threshold tolerances, divider accuracy, resistor stress, fuse/load budgets and manufacturer-curve capacitor derating. The separate converter model screens boost CCM loop corners only. Neither substitutes for hardware measurement. Reports state their assumptions rather than treating typical values as guaranteed bounds.

## Prototype gates before production release

| Gate | Measurement / acceptance intent |
|---|---|
| Assembly | Confirm exact horizontal terminals, pin-to-hole fit, polarity, U8 long-pad joints, R64 Kelvin layout, selector isolation and no solder shorts |
| Staged power | No sensors first; current-limited 12 V source, verify 5 V/3.3 V before full operation, then regulated 12 V and low-load input current |
| Regulation | Sweep 6–22 V with 0–300 mA on each rail separately and together; verify 12 V remains within the selected sensors' supply limits at their cable ends |
| External bias | Scope V5_INTERNAL, BB_EN, V12_RAW and 3V3 during slow/fast input ramps, repeated starts and brownouts. Confirm converter bias never causes unsafe switching or back-powering; review operation below 6 V |
| Transients | 6↔14↔22 V line steps; 0↔300 mA load steps; representative sensor startup/inrush and cable lengths; check ringing/undershoot through the buck/boost crossing |
| Stability | Measure loop response or justified equivalent transient qualification in buck, boost, transition and light-load/PFM modes; target >45° phase and >10 dB gain margin where measured |
| Faults | Short each sensor supply and each port; verify current-limit behavior, 12 V automatic recovery versus 5 V latch, firmware flags, no spurious counts and safe temperatures. Do not assume every 12 V short enters hiccup |
| Electrical protection | Reverse input, realistic protected-branch fault energy, fuse clearing/I²t, inductive transients and TVS stress using suitable test equipment. Not automotive load-dump qualified |
| Temperature | Both rails fully loaded at 6/12/22 V, intended ambient and later enclosure; measure U8/U1/L1/L2/Q1/fuse/terminal and MCU temperatures, hot-start/restart and surface safety |
| Inputs | 0–30 V PNP/NPN/push-pull thresholds, off-state leakage/residual voltage, ground offset, sensor disconnection, wiring transients and all intended sensor models |
| CAN/firmware | Real roboRIO bus at 1 Mbit/s with correct end termination; startup silence before provisioning, unique IDs, bus-off, clock faults, watchdog, broadcast disable, explicit resume, stale data and power-fault handling |
| EMC/mechanical | Motor-noise environment, ESD at terminals, cable retention, vibration, mounting insulation and programming-adapter fit; repeat after enclosure design |
| Production process | Approved stackup/CAM, stencil/profile, supplier alternates, test fixture, serial/lot records, programming/provisioning and final functional limits |

## FRC integration

Use a single appropriate protected power-distribution branch and wiring sized for its protection. The 0451 3 A fuse has a published 300 A interrupt rating at 32 V DC; confirm prospective branch fault current and clearing energy for the actual harness. The onboard fuse is secondary protection, not permission to bypass the robot distribution rules. Sensor grounds are common with the board; isolate conductive sensor cases where required by frame-ground rules. Do not use dedicated radio/roboRIO power outputs as a convenient supply.

The custom Team Use CAN address uses manufacturer 8 and miscellaneous device type 10. The implementation processes broadcast disable ID 0; it has no actuator outputs. It is not a CTRE Phoenix device. Robot inspection and the current season's rules still apply. Commercial CAN product acceptance, assigned identifiers and required ecosystem support are separate outstanding steps; Java/C++ examples alone do not establish approval.

Primary references: [2026 FIRST manual](https://firstfrc.blob.core.windows.net/frc2026/Manual/HTML/2026GameManual.htm), especially custom-circuit voltage, distribution/wire and frame-ground rules; [WPILib CAN addressing and acceptance requirements](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html). Recheck applicable rules for the actual event/season.

## D-2-specific prototype checks

Verify the exact 2 mm header and cap fit, both 5 V / 12 V positions and unpowered open state on every channel. Verify no connection between the two rails in either position. Check solder fill on all 39 user-fitted through-hole joints. Fit/retention, vibration and impact testing must include the actual caps, chosen removable retention compound, enclosure and robot harness; these headers have no positive latch. Compare the substituted passive values/ratings against the supplied BOM. Factory BOM and CPL must contain exactly 98 SMT references, with all nine through-hole components omitted. Firmware identity intentionally remains hardware 4 / protocol 3.
