# Rev H validation and release boundary

**No Rev H prototype has been assembled, powered or tested.** The automated evidence checks the design, software and manufacturing package. Physical acceptance remains a separate step.

## Automated evidence

Native KiCad ERC/DRC, explicit model/schematic/PCB parity, assembly constraints and independent reconstruction of all four Gerber copper layers check the delivered geometry. Firmware tests exercise the application state machine, CAN servicing, ADC scaling and register-level GPIO behavior; host and Java/C++ tests check protocol handling. Mocked hardware does not prove physical STM32 or CAN behavior.

Electrical calculations cover input thresholds, sensor leakage/residual-voltage margins, divider stress, capacitor derating, converter current budgets and output current-limit tolerances. The rail-reading budget reserves ±2.5% gain and ±90 mV offset at the sensor rail; firmware health bands include this uncertainty. The averaged boost loop screen covers 768 CCM corners. See the [release report](../reports/release_checks.json) for the exact retained results and hashes.

## Manufacturer-model transient screen

**Current run status: PASS transient screening.** All nine power cases and both complete 40 ms startup traces pass on the final BOM. Startup settles at 11.975–11.980 V, with 12.054 V peak protected output and 1.544 A peak inductor current. The two startup runs differ by at most 4.15 mV on internal 5 V, 14.23 mV on raw boost, 10.37 mV on protected 12 V and 0.524 mA in peak inductor current. The hot-short half-timestep repeat differs by at most 0.77 mV and 0.39 mA. [Full results](../reports/electrical/boost_spice.json) · [Current waveforms](../reports/electrical/boost_spice.png). Factory confirmation and physical qualification remain separate gates.

The [harness](../scripts/check_boost_spice.py) maps the fitted TPS61085 and TPS259620 pins/components into original TI models, with the Diodes B240A rectifier model. [Results](../reports/electrical/boost_spice.json) retain every scenario, criterion and generated netlist; [current Rev H waveforms](../reports/electrical/boost_spice.png) show the responses. A failed criterion returns nonzero and prevents the release validation command from passing.

| Scenario | Engineering question |
|---|---|
| Low-input combined startup, 66 µF raw bank, 100 µF external and 300 mA | Does controlled load connection avoid the former input-limiter startup failure? |
| 30→310→410→0 mA boost load | Does the converter regulate at normal load and the output limiter's upper current bound? |
| Running short and explicit reset | Does output protection limit current and recover when commanded? |
| Startup into a short and explicit reset | Does the circuit remain bounded without requiring a successful first startup? |
| 470 µF external capacitance with 300 mA | Does a larger capacitive load start in the standalone eFuse model? |
| 5 V startup, short and enable reset with concurrent 1.3 A load on internal 5 V | Does the unchanged TPS2553 latch-off branch work with its new GPIO enable? |
| Half-timestep repeat of the running 12 V short | Are the fault/reset results numerically stable away from imposed switching edges? |
| Sustained short, removal, then enable cycle | Does the thermal-latch model remain off until deliberate recovery? |
| Reduced current-limit surrogate, 120 µF external and 300 mA | Does the supported capacitance plus 20% start with minimum charging-current headroom? |

Capacitance stress cases use constant nameplate values; ceramic DC-bias reduction makes actual capacitance voltage-dependent. This is a conservative capacitive-load screen, not a guaranteed sensor-capacitance rating. Actual sensors can have constant-power or nonlinear startup loads.

The short tests connect a supply output to ground. They do not establish survival when the 12 V and 5 V outputs are joined: that can exceed U4's 7 V OUT absolute maximum and damage 5 V devices. Cross-rail wiring and externally powering output pins remain unsupported; do not interpret current limiting or software rail monitoring as protection against these faults.

The reduced-limit case uses a 2.92 kΩ test resistor in the typical eFuse model, producing approximately 314.4 mA, below the calculated 314.7 mA minimum for the fitted 2.61 kΩ resistor. This deliberately harder charging condition reaches 11.4 V in about 93 ms with no model fault. It supplements the analytical startup budget; it does not represent a full silicon or temperature corner model, and does not change the BOM.

The upstream supply is idealized with 120 mΩ series resistance, 25.92 µF internal capacitance and 450 mA concurrent logic/RGB/5 V load. The exact LMR51430 has no compatible public switching model listed on its TI product page. Its control loop/current limit, PCB/cable inductance, robot brownouts, temperature and production corners are not simulated. The default-off transistor stage is represented by an idealized enable switch; its physical startup behavior needs the separate bench check below. The eFuse thermal timing comes from its behavioral model, not a board thermal solution.

The normal boost case uses fixed derated C60/reservoir values. Silicon models are typical 27°C; inductor DCR is 32 mΩ and inductance is linear below the specified 8 A/20%-drop domain. D5 uses the vendor diode model; D6 uses an approximate static TVS clamp. This does not establish fast fault overshoot or reverse-power survival.

PSpice adaptations are syntax-only: namespacing, duplicate PARAMS removal and Boolean XOR translation. The combined startup uses KLU/Gear with `xtrtol=2`, a 50 ns maximum step and a 1 fF numerical node shunt. A complete repeat uses `xtrtol=7` and a 25 ns maximum step. Both retain relative tolerance 0.003 and the same circuit/models, and must pass all electrical criteria. Over the full 40 ms, the comparison requires voltage differences below 50 mV and peak-inductor-current difference below 20 mA. These are solver controls, not component changes.

The original `xtrtol=1` combined run stopped numerically at 28.971 ms during the transition into regulation. It and other [incomplete solver diagnostics](../reports/electrical/solver_diagnostics.json) are excluded from passing evidence; an incomplete trace cannot establish circuit operation or hardware failure. Standalone enable conductance ramps over 1 µs; a discontinuous ideal enable switch also produced a numerical timestep failure. The finite transition keeps the same 2 Ω final shunt. Zero-supply operating-point warnings are accepted only after successful transient-OP fallback and full completion. No semiconductor parameter is tuned to obtain a pass. Results have not been correlated with PSpice or a physical board. Rev F's superseded failure reports remain in its immutable archive.

## Firmware monitor waveform replay

The [replay screen](../reports/electrical/power_replay.json) feeds four completed SPICE traces into the actual `power.c`, compiled with ASan/UBSan, at all four combinations of ±2.5% ADC gain and ±90 mV rail offset. It also subtracts the worst current-layout branch drop at 300 mA. All sixteen cases pass: slow capacitive startup does not cause a false trip; running 12 V short causes a software latch after 20 ms; the 5 V hardware-fault signal causes a latch at the 33 ms sample. Neither rail automatically restarts in the replay, and the other rail stays enabled.

The 12 V trace is aligned to the firmware's 60 ms enable; the running-short case holds a pre-short regulated sample until startup grace ends. Samples are 1 ms apart and the last trace sample is held after its end. This is one-way replay, not coupled hardware/firmware simulation: shutdown commands do not alter the recorded waveform. The 470 µF case remains an extra diagnostic beyond the supported 100 µF external capacitance.

## Sensor-input transient screen

[Ten input-model runs](../reports/electrical/input_spice.json), including two half-timestep repeats, exercise the three native divider/filter/feedback circuits together. The [waveforms](../reports/electrical/input_spice.png) cover 3.3/5/24 V push-pull, 1.2/2.4 V logic limits and 30 V input, NPN/PNP with 100 µA OFF leakage, floating and driven probes, hysteresis, and comparator supply cycling. Cable capacitances are 0.1, 1 and 10 nF; probe checks sample before the firmware's 2 ms settling interval expires.

TI links its LM393LV channel model from the LM339LV product page. Three instances represent the used channels; native resistor/capacitor values and shared reference are retained. The model uses typical comparator behavior. The bias FETs, diode and sensors use explicit resistance, voltage-drop and leakage abstractions, not transistor-level models. The independent 4,096 static threshold corners remain necessary; these transients do not establish worst-temperature behavior, arbitrary sensor compatibility, MCU sampling of short pulses, or whole-board backfeed safety. The report records model/source hashes, decks, completed trace lengths and numerical-repeat differences.

## Prototype gates before production release

| Gate | Measurement / acceptance intent |
|---|---|
| Assembly | Confirm exact horizontal terminals, pin-to-hole fit, polarity, U8 VSSOP joints, D4 polarity, U9 TPS259620DDAR and exposed-pad soldering, selector isolation and no solder shorts |
| Staged power | No sensors first; current-limited 12 V source, verify 5 V/3.3 V before full operation, then regulated 12 V and low-load input current |
| Regulation | Sweep 6–22 V with 0–300 mA on each rail separately and together; verify 12 V remains within the selected sensors' supply limits at their cable ends |
| Cascaded startup | Scope V5_INTERNAL, BOOST_12V, BOOST_SS, SENSOR_12V and 3V3 during slow/fast input ramps, repeated starts and brownouts. Confirm boost startup/inrush does not falsely latch U9 or collapse U1; review operation below 6 V |
| Transients | 6↔14↔22 V line steps; 0↔300 mA load steps; representative sensor startup/inrush and cable lengths; check ringing/undershoot on both cascaded converters |
| Stability | Measure loop response or justified equivalent transient qualification on the cascaded 5 V buck / 12 V boost, including CCM and light-load/DCM modes; target >45° phase and >10 dB gain margin where measured |
| Faults | Short each sensor supply and each port; verify current-limit behavior, hardware current limiting, firmware latching and explicit CAN reset, firmware flags, no spurious counts and safe temperatures. Measure peak current and output-capacitor discharge energy before U9 disconnects; verify cold-start into a short and hot-plug loads |
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

## Rev H-specific prototype checks

Measure the 5 V/12 V ADC readings against a calibrated meter throughout the supply and load sweep. Check 11:1 divider scaling, VDDA compensation, settling and fault thresholds. Confirm both rails stay disabled during SWD programming, bootloader operation and MCU reset. Remove 3.3 V while raw boost remains energized and verify the Q2/Q3 stage holds the 12 V supply switch off. There is no active output discharge: distinguish residual capacitor charge from a conducting switch, using a known test load and probing EN. Check the six U9 ground thermal vias and exposed-pad solder joint.

At minimum input, test fully loaded startup and simultaneous 5 V / 12 V faults; record shared-rail sag, dropout and reset behavior. The new LMR51430/SRP7028A-8R2M pair passes nine current-limit corners, including the charging corner that exceeded the old buck's minimum valley limit. This calculation does not guarantee uninterrupted operation: source impedance, closed-loop behavior, input dropout and thermal limits remain unmeasured. Confirm the output eFuse nominal 357 mA limit, tolerance bounds, load-capacitance startup and thermal latch behavior. Verify a short on either branch does not cause unsafe shared-supply oscillation. The 768-corner CCM screen uses assumed amplifier/modulator bounds and does not qualify silicon behavior.

Verify the exact 2 mm header and cap fit, both 5 V / 12 V positions and unpowered open state on every channel. Verify no connection between the two rails in either position. Check solder fill on all 49 user-fitted through-hole joints. Fit/retention, vibration and impact testing must include the actual caps, chosen removable retention compound, enclosure and robot harness; these headers have no positive latch. Compare the substituted passive values/ratings against the supplied BOM. Factory BOM and CPL must contain exactly 129 SMT references, with U5 and all ten through-hole components omitted. Inspect the additional 32 user-soldered MCU leads; factory paste must omit U5. Firmware identity is hardware 8 / protocol 4; prior-revision firmware is rejected.

## CAN servicing qualification

The service engine and host uploader pass simulated flash cuts/retries; ARM register checks and both bridge adapters compile. Before robot use, measure actual boot/vector/interrupt behavior, option-byte protection, stack use, upload time, CAN load, bus-off recovery and duplicate-ID discovery. Interrupt power during invalidation, every erase/program phase and final commit on physical units. Verify persistent configuration, bootloader recovery, controller disconnect/enable rejection and healthy telemetry after exit. [Protocol and evidence](CAN_SERVICE.md); [per-unit fixture records](FIXTURE.md). No software simulation closes these physical gates.

## Electronic bias qualification

Verify Q101/201/301 PMOS and Q102/202/302 NMOS polarity and correct exact MPNs. Scope all six gate signals during reset, SWD programming, bootloader, watchdog recovery and supply ramps: pull-up gates HIGH and pull-down gates LOW mean both biases off. Verify mixed NPN/PNP/push-pull operation and nonvolatile readback independently on all three channels.

Sweep external signal 0–30 V in every mode. Measure inactive sensor leakage margins, active residual voltage and pull-up sink current (~3.5 mA maximum). Test 3.3 V and 5 V push-pull, unpowered sensors and unpowered board backfeed. Qualify the BAT46W leakage/rail-bleed budget over the actual operating temperature; current calculation uses its 60°C reverse-leakage specification, not a zero-backfeed claim.

Test floating detection with open contacts, NPN and PNP inactive outputs, long cables and added capacitance. Verify UNKNOWN during inconsistent probe pairs, no probe-generated edge counts, and one debounced edge on actual active-state transitions. Check keeper retention while released and LOW initialization after reset. Verify fixed input modes for faster signals; float detection can alias changing sources.

Rev H design envelope: at most 100 µF total external capacitance on the shared 12 V rail, and 22 µF on the shared 5 V rail, at 300 mA per rail. The startup calculation includes +20% capacitance and the current-limit minimum; the 470 µF simulation is a typical diagnostic beyond that envelope. Qualify nonlinear sensor inrush separately.

## Rev H RGB and service header

The circuit regression compares H against G and records the status indicator, its buffer/passives, the service-header replacement and the explicitly reviewed JLC substitutions. C25/C26 use 20 pF to improve calculated crystal startup margin. Power component values and sensor inputs are unchanged. Compiled ARM tests check TIM2 update DMA mapping, both 8/48 MHz pulse settings, GRB encoding, reset gaps, bounded transfer-error recovery and CAN acknowledgment freshness. The application harness checks status during normal, unplugged-CAN, initialization, clock and power-fault cases. These tests emulate CPU/register boundaries, not the actual timer/DMA silicon or emitted optical waveform.

Follow [the fixture checks](FIXTURE.md) and [status/programming guide](STATUS_AND_PROGRAMMING.md) on the first assembled unit. Verify LED package orientation and 5 V buffer margin, reset/brownout transitions, no sampling interruption, the five-wire programming harness, and the enclosure optical opening. The nominal STEP model is not physical-fit evidence.
