# Rev F validation and release boundary

**No Rev F prototype has been assembled, powered or tested.** The files support engineering review and prototype fabrication. The production/competition qualification gates below remain open, even when every automated check passes.

**Final hardware order: HOLD.** See the [pre-order review](ORDER_READINESS.md) for the decision, additional component experiments and issues firmware cannot fix. Prototype fabrication and an order intended to need no hardware corrections have different acceptance requirements.

## Automated evidence

The release contains native KiCad electrical/design-rule reports, explicit pin-model/schematic/PCB parity, placement/selector/programming-contact checks, manufacturing-file parsing and copper checks, host firmware tests, and Java/C++/Python protocol tests. These check design consistency and modeled behavior. Mocked peripheral tests do not prove STM32 timing or CAN electrical operation.

Electrical checks sweep input-threshold tolerances, divider accuracy, resistor stress, fuse/load budgets and manufacturer-curve capacitor derating. The averaged converter model screens boost CCM loop corners; the additional manufacturer-model transient screen below checks startup and faults. Neither substitutes for hardware measurement. Reports state their assumptions rather than treating typical values as guaranteed bounds.

## Manufacturer-model transient screen

**Outcome: review required.** The nominal-load cases pass, but this is not an all-pass power qualification. Failed cases remain in the published data, and `validate_release.sh` now stops at the simulation gate. An archive-integrity pass only verifies that the delivered files match their manifest.

| Check | Observed result |
|---|---|
| Full-load startup, fixed derated capacitors | PASS: first 11.4 V at 3.632 ms; 11.919–12.009 V during 5–6 ms, about 12.00 V average into 40 Ω |
| Numerical repeat | Halving maximum timestep changes startup crossing by 0.127 µs and final extrema by less than 0.6 mV |
| Typical Samsung C(V), unchanged 100 nF C66 | PASS diagnostic: first 11.4 V at 3.850 ms, 11.937–12.009 V during 6–7 ms, no boost UVLO retry. Typical behavior does not establish production corners |
| 30→300→0 mA, 10 µs transitions | PASS: 11.252–12.422 V over the tested steps; no false U9 latch |
| Standalone protection switch | PASS: approximately 1.199 A limiting, 7.494 ms fault delay, stays latched after removing the short; later power cycle recovers |
| Startup into a short | PASS for modeled latch behavior; remains disconnected after removing the short |
| Constant nameplate 22 µF input / 66 µF output, lower input | FAIL: four boost UVLO drops; peak 11.393 V and no regulated startup within 10 ms. This deliberately neglects ceramic DC-bias reduction |
| 66 µF fixed output bank plus 100 µF external, lower input, 40 Ω load | FAIL: repeated boost UVLO/soft-start retries; output never reaches 11.4 V in the 12 ms run (peak 9.752 V) |
| Rapid reset after a running short | FAIL in the model: a roughly 2 ms off interval does not recover. The same behavior occurs with the switch alone; its deglitch state remains high while IN is zero. Actual reset timing needs bench confirmation |
| Hot-short peak-current model validity | REVIEW: linear-L model predicts 8.613 A, above 8 A for about 4.7 µs. The Bourns 8 A specification represents 20% inductance drop, not a destruction limit; this model cannot establish the actual peak or component survival |

The [reproducible ngspice harness](../scripts/check_boost_spice.py) combines TI's TPS61085 and TPS2553-1 transient models with the Diodes B240A rectifier model. Device pin order is mapped explicitly from the maintained circuit, including the switch model's extra ground/pad port. Original model files, notices and hashes are retained. [Results and assumptions](../reports/electrical/boost_spice.json); [waveform overview](../reports/electrical/boost_spice.png); [run instructions](../TOOLS.md#power-transient-simulation).

The eight scenarios also include startup using constant nameplate capacitances (22 µF input / 66 µF output). Constant 66 µF overstates this ceramic bank's capacitance at 12 V; it is a conservative screen, not an exact prediction of the bare board. The additional 100 µF case is an engineering stress case, not a guaranteed maximum sensor capacitance. Resistive startup loads reach 300 mA at 12 V; actual sensor startup and constant-power behavior can differ.

[Four diagnostic experiments](../reports/electrical/boost_spice_experiments.json) and their [plots](../reports/electrical/boost_spice_experiments.png) separate these effects. Substituting hypothetical 220 nF or 330 nF C66 values still fails the 66+100 µF stress case within 14 ms (peaks 10.497 V and 11.004 V respectively); neither is an accepted fix. The unchanged circuit passes the additional typical C(V) run. Its differential-capacitance interpolation differs from the retained Samsung data by less than 1% over 0–13 V, and a standalone ramp check agrees with the expected charging current within 0.085%. This validates the model implementation, not actual capacitor production spread. The fourth experiment reproduces the rapid-reset issue using U9 alone. Diagnostic records retain exact netlists and raw-trace hashes; reproduce each with its recorded `--case` command.

The upstream LMR51420 model is encrypted, so this simulation uses an ideal ramped 5 V source with 50 mΩ series resistance, a 25.92 µF reservoir and a 400 mA parallel load representing the other rail and logic. It does **not** simulate the buck control loop, its current limit, battery wiring or robot brownouts. The boost's 10.8238 µF normal output bank and 8.64 µF input capacitor use fixed derated values; actual capacitance changes with voltage. Capacitor ESR is assumed, inductor DCR uses the Bourns 32 mΩ typical value, and silicon models run at 25°C. Thermal effects, component production corners, extracted PCB/cable parasitics, input comparators and firmware are outside this SPICE model. The plotted fault signal is U9's output alone; the physical U7D comparator also pulls that net low below its threshold.

PSpice syntax needed minor compatibility changes, including Boolean XOR. Gear integration was required because trapezoidal integration produced an artificial latch reset. This port has not been correlated against the original simulator or measured hardware. No semiconductor model parameters were tuned to obtain a pass. A short can produce an initial current spike and discharge stored capacitor energy before the switch limits/latches; the result does not certify peak fault energy or fuse coordination. Acceptance bands in the harness are screening criteria, not revised product specifications.

Before the next hardware iteration, define and qualify the allowed sensor capacitance/inrush at full load, revisit the soft-start margin, and measure a running short with the actual input/output capacitors and inductor. Increasing U9's current limit is not an automatic fix: the shared 2 A buck budget must still hold. A larger C66 using the existing 1 µF BOM value is a candidate for further evaluation, not a validated change. Measure reset recovery across short and long power interruptions. The PCB/BOM still specify 100 nF C66; simulation experiments do not change fitted hardware.

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
