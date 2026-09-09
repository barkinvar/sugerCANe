# Rev H pre-fabrication review

Rev H retains Rev G's power-path repairs and adds RGB diagnostics plus a recessed female service socket. The current native PCB, pin mapping, manufacturing exports, firmware and input simulations pass their checks. No physical board has been tested.

The latest rerun completed all eight standalone power cases and both input half-timestep repeats. The two full coupled-startup traces remain incomplete, so the order decision is **HOLD for full power evidence**. Sixteen one-way waveform replays also pass through the actual firmware power monitor, including ADC-error corners.

The native routed-copper calculation is now fresh for the cleaned routing. At the stated 85°C/nominal-copper assumptions, the buck-to-boost drop is 33.62 mV against a 120 mV allowance. The worst sensor branch drops 43.18 mV at 300 mA against a 60 mV allowance. The clearance, rounded-outline, female socket and jumper-label changes remain in the checked CAD.

Routing cleanup reduces 8,725 segments to 4,113 by removing tiny steps, unnecessary bends and backtracking hooks. Long runs use consistent 45° bends. Component/pad locations, all 245 vias, net assignments, widths, keepouts and the continuous inner ground layer are preserved. Existing short ground/pad entries and the local converter/crystal routing remain where needed. Fresh native DRC and reconstruction of all four exported copper layers find no shorts or opens; see the [routing inventory](../reports/board_constraints.json) and [four-layer copper review](../output/assembly/gerber_copper_review.pdf). These checks do not replace physical qualification.

## Changes that address the earlier failures

| Rev F finding | Retained power implementation | Verification |
|---|---|---|
| Input-side limiter interrupts loaded boost startup | U8 connects to internal 5 V; TPS259620 output eFuse connects the sensor load after the raw boost reservoir | Completed Rev G baseline; Rev H combined startup with 66 µF raw reservoir, 100 µF external load and 300 mA remains incomplete |
| Reservoir discharge passes through the boost short-current path | U9 limits the protected output; C62–C64 remain upstream; D5 clamps negative output excursions | Running short, cold short, sustained fault and restart scenarios |
| Firmware cannot reset power protection | PA15 controls U4; PB7 controls Q3/Q2 and U9 enable | Register-level pin tests, application sequencing and addressed CAN reset tests |
| Reset/unpowered MCU needs a safe output state | R71/R75 pull enable signals LOW; R70 derives the 12 V inhibit from raw BOOST_12V | Native pin/net checks and default-off circuit review |
| Coarse rail-presence indication misses undervoltage | Separate 11:1 dividers and RC filters feed PB0/PB1 ADC; firmware uses calibrated internal reference | ADC register tests, rail-state tests and divider/current budgets |
| Local boost bypass below recommended value | C61 increased to 1 µF; 22 µF bulk C60 retained | Exact-MPN BOM/model/parity checks |
| Buck input bypass left remote from U1 | C2/C3 moved beside VIN; explicit local top-side ground return, with bootstrap routing clear of it | Native path checks require C3→VIN below 2.2 mm and C2→VIN below 5.5 mm; fresh DRC and Gerber connectivity |

The 5 V/12 V selection remains a removable 2 mm cap on each three-pin header. All 140 fitted parts remain on top: 130 SMT factory placements plus ten user-fitted through-hole parts. The PCB is 52 × 74 mm, four copper layers.

## Evidence to read

[Release check index](../reports/release_checks.json), [electrical budgets](../reports/electrical/electrical_checks.json), [native-route DC calculation and pin review](../reports/electrical/order_readiness.json), [768-corner averaged boost-loop screen](../reports/electrical/converter_loop.json), [ten input-transient cases](../reports/electrical/input_spice.json), [eight standalone power cases](../reports/electrical/boost_spice_partial.json), [firmware waveform replay](../reports/electrical/power_replay.json), and [full power-run status](../reports/electrical/boost_spice.json) with [earlier complete Rev G evidence](../../archive/README.md).

The DC calculation uses nominal 35 µm copper at 85°C and 20 µm via plating, with ideal pad contacts. It checks the 120 mV boost-input PCB allowance at a conservative 1.3 A boost branch, 510 mA 5 V branch, 130 mA logic load and 20 mA RGB/buffer load. Ground return, connectors, cables, actual copper tolerances and temperature rise need measurement.

Pin expectations are checked independently against manufacturer functions for the MCU, CAN transceiver, comparators and power switches. Native ERC/DRC, model/schematic/PCB parity and reconstructed Gerber connectivity check the actual delivered design rather than only the conceptual schematic.

## Limits and first-article acceptance

The vendor transient model uses an idealized upstream 5 V source; it does not simulate the LMR51420 loop, robot wiring, all silicon corners or an assembled board. The eFuse's floating OVCSEL setting is a roughly 13.8 V fault clamp, not a precision 13 V trip. Software rail monitoring supplements the independent hardware current limits. It does not make a fault-proof or reverse-powered output.

The passing short cases are **shorts to ground**. Directly joining the 5 V and 12 V rails is unsupported and can damage the 5 V switch or sensors: U4's OUT absolute maximum is 7 V. Its reverse-voltage blocking and software overvoltage detection do not guarantee survival of a 12 V cross-connection. See the [wiring limits](WIRING.md).

Qualify startup, both rails loaded together, the exact sensor models and cables, brownouts, cold/running shorts, temperature and CAN programming/recovery using the [validation procedure](VALIDATION.md). Record PCB revision H, exact BOM and firmware identity. Simulation and manufacturing checks reduce the risk of a first order; they cannot guarantee first-board success.

Primary pin/application references: [STM32F042](https://www.st.com/resource/en/datasheet/stm32f042t6.pdf), [TPS2596](https://www.ti.com/lit/ds/symlink/tps2596.pdf), [TPS61085](https://www.ti.com/lit/ds/symlink/tps61085.pdf), [TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf), [TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf), [LM339LV](https://www.ti.com/lit/ds/symlink/lm339lv.pdf).

The RGB load is included in the increased 0.15 A internal logic/indicator reserve. Check D10 colors, timer waveform and reset/handoff behavior on the first physical board. The recessed J8 socket needs five male-ended mapped SWD leads; see [status and programming](STATUS_AND_PROGRAMMING.md).
