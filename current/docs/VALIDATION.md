# Rev F validation and release boundary

**No Rev F prototype has been assembled, powered or tested.** The files support engineering review and prototype fabrication. The production/competition qualification gates below remain open, even when every automated check passes.

## Automated evidence

The release contains native KiCad electrical/design-rule reports, explicit pin-model/schematic/PCB parity, placement/selector/programming-contact checks, manufacturing-file parsing and copper checks, host firmware tests, and Java/C++/Python protocol tests. These check design consistency and modeled behavior. Mocked peripheral tests do not prove STM32 timing or CAN electrical operation.

Electrical checks sweep input-threshold tolerances, divider accuracy, resistor stress, fuse/load budgets and manufacturer-curve capacitor derating. The separate converter model screens boost CCM loop corners only. Neither substitutes for hardware measurement. Reports state their assumptions rather than treating typical values as guaranteed bounds.

## Prototype gates before production release

| Gate | Measurement / acceptance intent |
|---|---|
| Assembly | Confirm exact horizontal terminals, pin-to-hole fit, polarity, U8 VSSOP joints, D4 polarity, U9 latch-off suffix, selector isolation and no solder shorts |
| Staged power | No sensors first; current-limited 12 V source, verify 5 V/3.3 V before full operation, then regulated 12 V and low-load input current |
| Regulation | Sweep 6–22 V with 0–300 mA on each rail separately and together; verify 12 V remains within the selected sensors' supply limits at their cable ends |
| Cascaded startup | Scope V5_INTERNAL, V5_BOOST, BOOST_SS, SENSOR_12V and 3V3 during slow/fast input ramps, repeated starts and brownouts. Confirm boost startup/inrush does not falsely latch U9 or collapse U1; review operation below 6 V |
| Transients | 6↔14↔22 V line steps; 0↔300 mA load steps; representative sensor startup/inrush and cable lengths; check ringing/undershoot on both cascaded converters |
| Stability | Measure loop response or justified equivalent transient qualification on the cascaded 5 V buck / 12 V boost, including CCM and light-load/DCM modes; target >45° phase and >10 dB gain margin where measured |
| Faults | Short each sensor supply and each port; verify current-limit behavior, both latching branches and power-cycle reset, firmware flags, no spurious counts and safe temperatures. Measure peak current and output-capacitor discharge energy before U9 disconnects; verify cold-start into a short and hot-plug loads |
| Electrical protection | Reverse input, realistic protected-branch fault energy, fuse clearing/I²t, inductive transients and TVS stress using suitable test equipment. Not automotive load-dump qualified |
| Temperature | Both rails fully loaded at 6/12/22 V, intended ambient and later enclosure; measure U8/U1/L1/L2/Q1/fuse/terminal and MCU temperatures, hot-start/restart and surface safety |
| Inputs | 0–30 V PNP/NPN/push-pull thresholds, off-state leakage/residual voltage, ground offset, sensor disconnection, wiring transients and all intended sensor models |
| CAN/firmware | Real roboRIO bus at 1 Mbit/s with correct end termination; no normal telemetry before provisioning, unique IDs, bus-off, clock faults, watchdog, broadcast disable, explicit resume, stale data and power-fault handling |
| EMC/mechanical | Motor-noise environment, ESD at terminals, cable retention, vibration, mounting insulation and programming-adapter fit; repeat after enclosure design |
| Production process | Approved stackup/CAM, stencil/profile, supplier alternates, test fixture, serial/lot records, programming/provisioning and final functional limits |

## FRC integration

Use a single appropriate protected power-distribution branch and wiring sized for its protection. The 0451 3 A fuse has a published 300 A interrupt rating at 32 V DC; confirm prospective branch fault current and clearing energy for the actual harness. The onboard fuse is secondary protection, not permission to bypass the robot distribution rules. Sensor grounds are common with the board; isolate conductive sensor cases where required by frame-ground rules. Do not use dedicated radio/roboRIO power outputs as a convenient supply.

The custom Team Use CAN address uses manufacturer 8 and miscellaneous device type 10. The implementation processes broadcast disable ID 0; it has no actuator outputs. It is not a CTRE Phoenix device. Robot inspection and the current season's rules still apply. Commercial CAN product acceptance, assigned identifiers and required ecosystem support are separate outstanding steps; Java/C++ examples alone do not establish approval.

Primary references: [2026 FIRST manual](https://firstfrc.blob.core.windows.net/frc2026/Manual/HTML/2026GameManual.htm), especially custom-circuit voltage, distribution/wire and frame-ground rules; [WPILib CAN addressing and acceptance requirements](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html). Recheck applicable rules for the actual event/season.

## Rev F-specific prototype checks

The 12 V monitor is a coarse collapse detector (~9.3 V nominal, modeled 8.0–10.6 V rising threshold), not a precision undervoltage guarantee. Measure actual sensor-terminal voltage and startup separately. The boost input limiter is approximately 1.2 A; the useful 12 V output remains 300 mA. Check 5 V source current and temperature with both rails loaded, and verify that a fault on either branch does not cause unsafe shared-supply oscillation. The 512-corner CCM result uses assumed amplifier/modulator bounds and does not qualify silicon behavior.


Verify the exact 2 mm header and cap fit, both 5 V / 12 V positions and unpowered open state on every channel. Verify no connection between the two rails in either position. Check solder fill on all 39 user-fitted through-hole joints. Fit/retention, vibration and impact testing must include the actual caps, chosen removable retention compound, enclosure and robot harness; these headers have no positive latch. Compare the substituted passive values/ratings against the supplied BOM. Factory BOM and CPL must contain exactly 110 SMT references, with all nine through-hole components omitted. Firmware identity is hardware 6 / protocol 4; prior-revision firmware is rejected.

## CAN servicing qualification

The service engine and host uploader pass simulated flash cuts/retries; ARM register checks and both bridge adapters compile. Before robot use, measure actual boot/vector/interrupt behavior, option-byte protection, stack use, upload time, CAN load, bus-off recovery and duplicate-ID discovery. Interrupt power during invalidation, every erase/program phase and final commit on physical units. Verify persistent configuration, bootloader recovery, controller disconnect/enable rejection and healthy telemetry after exit. [Protocol and evidence](CAN_SERVICE.md); [per-unit fixture records](FIXTURE.md). No software simulation closes these physical gates.

## Electronic bias qualification

Verify Q101/201/301 PMOS and Q102/202/302 NMOS polarity and correct exact MPNs. Scope all six gate signals during reset, SWD programming, bootloader, watchdog recovery and supply ramps: pull-up gates HIGH and pull-down gates LOW mean both biases off. Verify mixed NPN/PNP/push-pull operation and nonvolatile readback independently on all three channels.

Sweep external signal 0–30 V in every mode. Measure inactive sensor leakage margins, active residual voltage and pull-up sink current (~3.5 mA maximum). Test 3.3 V and 5 V push-pull, unpowered sensors and unpowered board backfeed. Qualify the BAT46W leakage/rail-bleed budget over the actual operating temperature; current calculation uses its 60°C reverse-leakage specification, not a zero-backfeed claim.

Test floating detection with open contacts, NPN and PNP inactive outputs, long cables and added capacitance. Verify UNKNOWN during inconsistent probe pairs, no probe-generated edge counts, and one debounced edge on actual active-state transitions. Check keeper retention while released and LOW initialization after reset. Verify fixed input modes for faster signals; float detection can alias changing sources.
