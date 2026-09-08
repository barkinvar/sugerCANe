**FRC industrial sensor to CAN interface — design and verification plan**

This is the original Rev A planning record. Candidate parts and early options below are historical; the final [Rev A architecture](docs/ARCHITECTURE.md) and [revision comparison](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md) describe the delivered designs.

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Prepared 2026-09-07. This is the original planning record. The subsequent routed prototype, BOM, firmware and computational checks are now complete as described in [README.md](README.md) and [VALIDATION.md](docs/VALIDATION.md). Physical hardware validation remains pending. Targets and candidate parts below document the planning stage; the final architecture and BOM control the delivered revision.

Build an original, repairable CAN sensor interface using DigiKey-orderable components. Prioritize reliable photoelectric-sensor detection, FRC integration, straightforward hand assembly, and replacement-part availability. Optimize total assembled cost, including connectors, protection, programming equipment, and rework—not just the microcontroller price.

CTRE CANdi is a functional reference: its published specifications include digital/PWM/quadrature inputs, 3.3–24 V input detection, 6–28 V supply operation, and CAN/CAN FD. Those specifications are reference points, not ratings inherited by this design. [CTRE product specifications](https://store.ctr-electronics.com/products/candi)

**1. Establish the requirements before selecting the circuit.**

Use the following working assumptions while collecting actual sensor part numbers, intended countries of purchase, quantity, budget, and mechanical constraints:

| Item | Proposed first revision |
| --- | --- |
| Inputs | Four independent channels; confirm connector/board cost before freezing count |
| Main use | Three-wire DC photoelectric sensors, including NPN sinking and PNP sourcing outputs |
| Other inputs | Dry contacts and 3.3 V / 5 V push-pull or open-drain logic |
| Industrial voltage | Support sensor outputs associated with 10–30 V DC sensors, subject to datasheet-defined low/high levels and leakage |
| Lower-voltage signals | Explicitly support 3.3 V; investigate 1.8 V only after a real requirement is identified |
| Board supply | Required: nominal 12 V FRC battery supply, connected through a protected robot power-distribution branch; investigate 6–30 V continuous board operation separately from sensor operating limits |
| Sensor power | Required: both protected battery-voltage output (VBAT_OUT) and regulated 5 V output (5V_SENSOR), available concurrently for a mixture of sensor types; specify per-port and total current limits |
| CAN | Native roboRIO bus; proposed 1 Mbit/s Classical CAN and 29-bit FRC addressing |
| Software | Custom WPILib interface and documented protocol; no assumed Phoenix/Talon remote-sensor compatibility |
| Construction | Two-layer PCB if return paths and layout permit; top-side SMD, through-hole connectors |
| Isolation | Common-ground baseline; add galvanic isolation only if the wiring/ground-offset requirement warrants it |

“5 V or lower” does not define a valid input specification by itself. For every supported mode, specify maximum recognized LOW, minimum recognized HIGH, hysteresis, input current, maximum continuous terminal voltage, and behavior when unpowered. Treat signal voltage, sensor supply voltage, and board supply voltage as separate requirements.

Record each intended sensor's supply range, supply current and startup current, NPN/PNP/push-pull topology, residual ON voltage, OFF leakage, output-current rating, response time, cable length, and wiring diagram. A sensor requiring at least 10 V may stop working during a robot brownout even if our board stays alive. A 12 V pass-through does not create regulated 24 V. The required first-revision outputs are battery voltage and regulated 5 V; a 24 V boost stage is a separate possible extension only if actual sensors require it. Industrial signal-voltage tolerance does not imply the board generates that voltage.

Power requirement confirmed by the user on 2026-09-07: the same FRC battery input must power the board and its attached sensors. Plan two sensor supply paths after input protection: a current-limited battery pass-through and a regulated, current-limited 5 V rail. VBAT_OUT follows the input battery voltage minus protection/switch losses; it is not regulated to 12 V. 5V_SENSOR must remain within its specified tolerance throughout the declared input-voltage and sensor-load range. Both rails must be usable at the same time. Keep the MCU/CAN logic supplied through a branch arranged so that a sensor-power short is contained and the interface can report the fault where feasible.

Expose the supply choice through clearly labeled connector contacts or a deliberate per-port selector, so different channels can use different supply voltages. A sensor connects to one selected power rail plus ground and signal; do not join the two rails. Freeze connector implementation and per-port/rail current ratings after checking representative sensors. Budget MCU/CAN consumption separately from the current advertised as available to sensors. Verify simultaneous rail loading, startup inrush, output-voltage drop, current-limit behavior, and thermal rise. Define low-input-voltage shutdown/restart behavior and the point below which regulated 5 V is no longer guaranteed.

Two-wire sensors, IO-Link, AC sensors, analog 0–10 V, and 4–20 mA require separate interfaces; do not advertise them as supported by the initial digital-input design.

**2. Separate electrical compatibility from software compatibility.**

A board transmitting valid CAN frames is not automatically a CTRE CANdi replacement in Phoenix, Tuner, or Talon firmware. The baseline is a documented custom sensor protocol read by robot code. Direct CTRE integration is a separate requirement to investigate before committing to it.

Use FIRST's CAN identifier structure and the Team Use manufacturer allocation for team prototypes, coordinate IDs with other custom devices, and investigate a manufacturer allocation if this becomes a distributed product. Provide Java and C++ examples, device-ID configuration, firmware/protocol version reporting, and stale-data detection. [WPILib CAN device specification](https://docs.wpilib.org/en/latest/docs/software/can-devices/can-addressing.html), [WPILib CAN API](https://github.wpilib.org/allwpilib/docs/release/java/edu/wpi/first/wpilibj/CAN.html)

Review current-season custom-circuit, power-conversion, wiring, radio, and CAN rules at requirements freeze and before robot use. In the 2026 manual, R707 limits wireless communication and R716 prohibits disruption of existing CAN communications. If an ESP32 is selected, disable its radios in robot firmware. Bench qualification must establish that resets, malformed messages, and faults do not disturb other devices. This plan is not a competition-compliance certification. [FIRST 2026 game manual](https://firstfrc.blob.core.windows.net/frc2026/Manual/HTML/2026GameManual.htm)

**3. Use KiCad as the editable design source.**

Use a pinned stable KiCad release for schematic capture, PCB layout, project libraries, 3D inspection, and manufacturing exports. Use its CLI to produce reproducible electrical-rule checks, design-rule checks, BOMs, and exports. Verify commands against the installed version. KiCad CLI and ngspice were not found on PATH in the initial workspace inspection; installing and recording the toolchain belongs to the implementation phase. [KiCad CLI documentation](https://docs.kicad.org/9.0/en/cli/cli.html)

Use ngspice for input thresholds, hysteresis, filters, and appropriate transient models. Use small Python calculations for worst-case tolerances, dissipation, supply budgets, and CAN bandwidth. Check simulation models against manufacturer data; document effects not represented by models. Simulation cannot establish EMC immunity or real hot-plug survival. [KiCad simulation capabilities](https://www.kicad.org/discover/spice/)

Keep editable sources, calculations, firmware, BOM, and reports in the project. Vendor symbols and footprints must be local or version-pinned so another team can reopen the design. Do not treat a rendered board image as a design deliverable.

**4. Search components systematically and preserve the evidence.**

Start with electrical and package constraints, then search DigiKey's parametric listings. Prefer active, normally stocked parts sold in single units/cut tape by DigiKey, not marketplace-only or obsolete inventory. Follow every shortlisted item to the manufacturer's datasheet, errata, application circuits, and package drawing.

For each candidate, record exact manufacturer part number, package suffix, DigiKey order code, product URL, stock-check date, observed stock, lead time, and quantity-1/10/100 pricing. Separate observed stock from guaranteed availability. Check intended regional DigiKey sites and at least one other authorized distributor as evidence of broader availability, while retaining DigiKey as the primary BOM supplier. Do not infer global availability from one US listing.

Compare the complete circuit cost: MCU, clock, flash, supply, CAN transceiver, programming connector, and assembly complexity. Rank electrical suitability and assembly feasibility first, then availability and total cost. Favor common 0805/1206 passives and leaded IC packages where practical. For substitutes, distinguish verified pin-compatible alternatives from parts requiring changed values, firmware, or PCB routing.

Initial research candidates—not an approved or complete BOM:

| Function | Candidate and DigiKey order code | Reason to investigate / unresolved checks |
| --- | --- | --- |
| Preferred MCU direction | STM32G0B1CBT6N; 497-STM32G0B1CBT6N-ND | Leaded LQFP candidate in a family with FDCAN; verify exact N-suffix pinout, clock requirements, timers, errata, and cost |
| MCU comparison | ESP32-C3-WROOM-02-N4; 1965-ESP32-C3-WROOM-02-N4CT-ND | Module reduces external circuitry; verify module soldering, exposed-pad requirements, available pins, and radio-disabled behavior |
| CAN transceiver | TCAN3413DR; 296-TCAN3413DRCT-ND | SOIC-8, 3.3 V candidate with wider bus-fault tolerance; verify pin modes, protection coordination, and regional supply |

Sources: [STM32 DigiKey listing](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32G0B1CBT6N/18086035), [ST family documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g0b1cb.html), [ESP32 module DigiKey listing](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-C3-WROOM-02-N4/14553036), [TCAN3413 DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/TCAN3413DR/22147484), [TI transceiver datasheet](https://www.ti.com/tw/lit/gpn/tcan3413).

The ESP32-C3 contains a CAN/TWAI controller, not a physical CAN transceiver; it still needs an external transceiver. Its controller supports Classical CAN, not CAN FD. An STM32 FDCAN peripheral also requires a physical transceiver. Select Classical CAN for the initial roboRIO interface even if the chosen hardware supports FD. [Espressif TWAI documentation](https://docs.espressif.com/projects/esp-idf/en/v5.1-rc1/esp32c3/api-reference/peripherals/twai.html)

**5. Prove the input front end before duplicating four channels.**

Investigate a protected comparator input with defined hysteresis and selectable bias/threshold modes. Compare it against an industrial digital-input receiver and, if isolation becomes necessary, an isolated approach. Choose from calculations and bench behavior rather than assuming a generic optocoupler or divider works across the entire range.

| Mode | Required behavior |
| --- | --- |
| 3.3/5 V push-pull | High-impedance sensing, low-voltage threshold, no pull-up to industrial voltage |
| Low-voltage open-drain/contact | Defined safe low-voltage pull-up, switch filtering, predictable open state |
| Industrial NPN | Defined load/pull-up compatible with sensor sinking capability and residual voltage |
| Industrial PNP | Defined load/pull-down compatible with sensor sourcing capability and OFF leakage |

Prefer clearly labeled physical mode selection for revision A unless a protected electronic implementation materially improves usability. Independently specify whether a wrong mode merely misreads or can damage a connected low-voltage sensor. Avoid any selectable high-voltage pull-up that can silently expose low-voltage equipment without an explicit connector/mode strategy.

Calculate worst-case thresholds including resistor tolerance, reference drift, comparator offset, leakage, temperature, and supply variation. Check input common-mode limits, clamp current, resistor working voltage and pulse energy, continuous 30 V dissipation, negative transients, and input-powered/board-unpowered conditions. Protection must not back-power the MCU rail.

Define filter bandwidth, minimum pulse width, propagation delay, and deglitch settings from the intended sensors. Ordinary beam detection is the first priority. PWM and quadrature support require a separately verified fast mode; heavy filtering that works for a switch may lose encoder edges. Reserve appropriate MCU timer pins before layout. Do not claim open-wire diagnosis for ordinary three-wire digital sensors unless additional circuitry demonstrably distinguishes it from an inactive sensor.

**6. Design power, CAN, and recovery behavior as complete subsystems.**

Power: coordinate branch protection, reverse-polarity protection, TVS clamping, regulator voltage margin, inrush, and output current limits. Calculate clamp voltage at the chosen transient current—not just TVS nominal voltage. Select a buck supply using manufacturer layout guidance and derated capacitors/inductors; avoid burning the industrial-to-logic voltage drop in an undersized linear regulator. Specify pass-through and regulated sensor-power current budgets, startup load, short-circuit behavior, and thermal limits. Keep programming power from feeding the robot or sensor rail unintentionally.

CAN: place connector protection at the entry, keep the transceiver close, preserve ground return paths, and provide convenient daisy-chain connections. Use optional 120-ohm termination, disabled by default for an intermediate robot node. Inspect the entire bus termination rather than adding a resistor at every device. [WPILib CAN wiring guidance](https://docs.wpilib.org/en/latest/docs/hardware/hardware-basics/can-wiring-basics.html)

Firmware: establish a clock/timing budget; put the transceiver in a harmless state during reset; include watchdog and brownout recovery, bounded transmission rates, bus-off recovery, persisted configuration with integrity checks, and recovery programming access. Report input state, sequence/timing information, and implemented fault indicators. Bound event bursts and calculate worst-case bandwidth including frame overhead and bit stuffing. Robot code must distinguish stale data from a valid inactive sensor.

**7. Lay out specifically for hand soldering and a heatbed.**

Prefer 0805 passives, larger protection components where dissipation warrants them, SOIC/TSSOP ICs, and a leaded MCU. Avoid BGA and unnecessary fine-pitch leadless parts. A heatbed can help assemble an exposed pad, but that does not make it easy to inspect or rework.

Place SMD parts on top, allow iron/tweezer access, and solder through-hole connectors after reflow. Follow component thermal profiles and moisture handling; select solder/stencil and assembly order explicitly. Check plastic connector temperature limits. Use a mostly continuous ground plane, short regulator switching loops, local decoupling, and separation between noisy power and sensitive input paths.

Choose terminal pitch, wire gauge range, retention, mounting holes, and enclosure clearance before fixing board dimensions. Label power polarity, CAN H/L, channel numbers, mode positions, and sensor power voltage. Add accessible test points for supply rails, conditioned input signals, CAN logic, reset, and programming. Keep bottom clearance suitable for the intended heatbed and mounting arrangement.

**8. Cross-check with independent methods and explicit release gates.**

| Gate | Evidence required |
| --- | --- |
| Requirements | Sensor compatibility matrix, supported modes, numerical thresholds, power/current budget, speed target, mechanical assumptions |
| Architecture | MCU/pin allocation, CAN protocol outline, input topology comparison, priced major-component shortlist |
| Schematic | Every IC pin checked against the exact datasheet; power/boot/debug review; protection and tolerance calculations; ERC with no unexplained findings |
| Layout | Symbol-pad-pin mapping and package dimensions verified; return paths and heat reviewed; no unrouted nets; DRC and schematic parity checked; exclusions justified |
| Fabrication | Gerbers/drills opened independently; outline, copper, mask, paste, holes, and polarity inspected; BOM/placement/designators reconciled; schematic PDF and assembly drawing exported |
| Prototype | Measurements recorded against requirements; failures corrected before claiming ratings or robot readiness |

ERC/DRC cannot prove correct thresholds, transient survival, firmware safety, or compatibility. Review those separately. Build one input-channel prototype or test coupon before committing the full board if the front end remains uncertain.

Hardware tests require physical boards and bench equipment: current-limited supplies, DMM, oscilloscope, signal generator or representative sensors, CAN interface/analyzer, and eventually a roboRIO system. First check unpowered resistance and rails, then program the MCU, then test CAN on an isolated bench bus before connecting it to a robot.

Test every channel in each supported mode at supply extremes, minimum HIGH/maximum LOW, sensor leakage/residual-voltage limits, open input, power sequencing, and intended maximum pulse rate. Exercise supply dips, restart, hot plugging, protected sensor-output shorts, declared input miswiring cases, CAN unplug/reconnect, missing termination, duplicate IDs, bus-off, and firmware recovery. Measure rail ripple, temperature, timing, and bus load. Include endurance operation with actual sensors and representative cable lengths. Use controlled test levels and distinguish bench fault testing from formal EMC qualification.

**9. Deliver a reproducible package and a complete DigiKey BOM.**

Final deliverables: native KiCad project and libraries; schematic PDF; reviewed fabrication Gerbers and drill files; board renders/STEP; placement and assembly drawings; firmware source/build instructions; CAN protocol; WPILib Java/C++ examples; bring-up and wiring instructions; and validation reports identifying completed versus pending hardware tests.

The BOM will contain every populated component, including passives, connectors, protection, mode jumpers, and programming hardware on the board. Include reference designators, quantity, value, tolerance, voltage/power rating, footprint, manufacturer, exact MPN, DigiKey order code/link, pricing date/currency, quantity pricing, observed availability, and approved alternates. List DNP options separately. Include mating connectors and other required off-board items as an accessory BOM. Separate electronics cost from PCB, stencil, shipping, taxes, tools, and spares.

Finish in this order: requirements and sensor matrix → architecture and sourcing → one-channel proof/calculations → complete schematic → PCB and assembly review → fabrication package → prototype validation and revision. The resulting prototype files are indexed in README.md. Computational checks support the design choices; physical measurements are still required to establish operating ratings.
