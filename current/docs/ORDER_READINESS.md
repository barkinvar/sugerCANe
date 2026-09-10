# Rev H pre-fabrication review

**Current order decision: HOLD.** Engineering checks are complete for the selected DigiKey-MCU/JLC assembly BOM. C25/C26 use 20 pF clock-load capacitors; U1/L1 now use a 3 A LMR51430XDDCR and 8.2 µH SRP7028A-8R2M in unchanged footprints. The C1 high-reflow replacement is retained. Native CAD, all-layer connectivity, BOM matching, input simulations and firmware checks pass. Full coupled-startup transient screening passes; factory process/stack confirmation remains open. No physical board has been tested.

The current BOM has **nine completed power cases, required timestep/solver repeats, ten input cases and sixteen firmware waveform replays passing**. The original checkout's coupled-startup simulations completed without interruption. Source hashes were checked before importing the completed evidence. [Current power report](../reports/electrical/boost_spice.json). The earlier `8d4deb4` results are historical, and are no longer used as a substitute for current standalone evidence.

The compact board's native routed-copper calculation gives **43.69 mV buck-output-to-boost-input drop against a 120 mV allowance**, at the stated 85°C/nominal-copper assumptions. The worst complete protected-supply-to-connector path drops **14.04 mV at 300 mA against the existing 60 mV allowance**. Each rail has a shared 300 mA sensor budget; the calculation places that entire load at each port in turn.

The DC model now recognizes overlapping track copper, contacts inside a straight segment and via connections on multiple layers, using the saved stackup depths. Buck-to-boost drop is measured between those two terminals; the older value was relative to the buck feedback tap. These figures therefore are not a direct before/after performance comparison. Six resistor-network regression fixtures check known resistance, segment subdivision, contacts, via depths, voltage-reference independence and genuine opens. The model still assumes ideal pad/via-annulus copper and does not solve current crowding or heating.

The compact layout occupies 44 × 48 mm; the routing report lists its current segment and via inventory. The [routing gate](ROUTING_RULES.md) rejects pad overshoots, overlapping routes, tiny free jogs, end-cap-only joins, sharp free bends, unchamfered branches and unreviewed widths. Low-current control and monitoring traces use the existing 0.18 mm fabrication minimum; the reviewed width policy separately preserves CAN, supply, ground and converter widths. Outer and In1 ground pours use a 0.30 mm minimum, In2 pours 0.25 mm, and separate ground islands retain the 0.25 mm gap rule. SMT ground pads retain solid zone connections. The [compact preservation audit](../reports/compact/layout_verification.json) verifies unchanged circuit/schematics and rigidly transformed critical clock/converter copper. Native DRC and independent reconstruction of all four exported layers find no shorts or opens; see [routing results](../reports/routing_rules.json) and [copper review](../output/assembly/gerber_copper_review.pdf). These checks do not replace physical qualification.

The input screen uses 2 A through J1 → F1 → Q1 → U1, with finite via resistance. It is a DC screening point above the normal analytical 1.726 A at 6 V, not a fault-current or thermal rating.

| Input copper path | Width | Drop at 2 A |
|---|---|---|
| J1 to F1 (`VIN_RAW`) | 0.7 mm | 2.15 mV |
| F1 to Q1 (`VIN_FUSED`) | 0.7 mm | 50.40 mV |
| Q1 to U1 VIN (`VIN_PROT`) | 0.8 mm trunk; retained low-current enable branch | 57.34 mV |
| Total input feed copper | All three paths | **109.90 mV** |

The input copper resistance is approximately 54.95 mΩ. At the normal analytical input current, its modeled drop is approximately 94.84 mV. The existing 276 mΩ entry-resistance planning budget leaves approximately 221.05 mΩ for the excluded fuse, MOSFET, contacts, cables and ground return; those items still require verification. The low-current U1 enable branch remains 0.25 mm.

All four layers retain nominal **35 µm (1 oz) copper**, now explicitly enforced by the DC screen. Inner 1 is the ground plane; inner 2 carries selected signal/service/control and low-current supply routes alongside ground; the routing report records the delivered inventory. Native routing rules and independent exported geometry checks include both inner layers. [Individual PNG/SVG views](../README.md) and the four-page copper PDF are regenerated from the delivered Gerbers.

## Final component-margin review

C25/C26 changed from 30 pF to **20 pF C0G / Yageo CC0805JRNPO9BN200** without moving pads or traces. The conservative crystal gain calculation improves from 4.61 to **6.54** at 10 pF assumed stray capacitance and the published worst component bounds. All six modeled loading corners exceed ST's gain-margin recommendation. Frequency pulling, oscillator drive, actual stray capacitance and startup must still be measured on the first board. [Calculation and assumptions](../reports/electrical/component_margins.json).

The buck review found a second margin issue: the former 2 A LMR51420's minimum 1.7 A valley limit can be exceeded by maximum 12 V charging current plus a normal 5 V load near minimum input, as well as by some simultaneous-fault corners. **U1 is now LMR51430XDDCR and L1 is SRP7028A-8R2M, 8.2 µH**, in the same footprints. The new minimum limits are 2.75 A valley and 3.67 A peak. All nine normal/charging/fault current-limit corners pass; the maximum calculated peak is 2.625 A. L1's published 4 A RMS and 7.5 A saturation ratings exceed the modeled load and the regulator's 6.68 A maximum peak limit. This improves current headroom; dropout, supply impedance, thermal behavior and uninterrupted MCU/CAN operation still require bench testing. [Calculation](../reports/electrical/component_margins.json) · [Exact change scope](../reports/manufacturing/buck_margin_change.json).

The public TI LMR51430 product page does not provide a compatible switching model. Its upstream control loop is **not simulated** here. The completed downstream power decks match final-BOM generation byte for byte because U1/L1 lie upstream of their idealized source. That preserves the downstream evidence, without treating it as a simulation of the new buck.

## Changes that address the earlier failures

| Rev F finding | Retained power implementation | Verification |
|---|---|---|
| Low-input charging current exceeds former buck minimum current-limit headroom | 3 A LMR51430 with 8.2 µH / 7.5 A-saturation L1 | All nine current-limit corners pass; upstream loop/dropout/thermal qualification remains physical |
| Input-side limiter interrupts loaded boost startup | U8 connects to internal 5 V; TPS259620 output eFuse connects the sensor load after the raw boost reservoir | Rev H combined startup with 66 µF raw reservoir, 100 µF external load and 300 mA passes, including the required solver/timestep repeat |
| Reservoir discharge passes through the boost short-current path | U9 limits the protected output; C62–C64 remain upstream; D5 clamps negative output excursions | Running short, cold short, sustained fault and restart scenarios |
| Firmware cannot reset power protection | PA15 controls U4; PB7 controls Q3/Q2 and U9 enable | Register-level pin tests, application sequencing and addressed CAN reset tests |
| Reset/unpowered MCU needs a safe output state | R71/R75 pull enable signals LOW; R70 derives the 12 V inhibit from raw BOOST_12V | Native pin/net checks and default-off circuit review |
| Coarse rail-presence indication misses undervoltage | Separate 11:1 dividers and RC filters feed PB0/PB1 ADC; firmware uses calibrated internal reference | ADC register tests, rail-state tests and divider/current budgets |
| Local boost bypass below recommended value | C61 increased to 1 µF; 22 µF bulk C60 retained | Exact-MPN BOM/model/parity checks |
| Buck input bypass left remote from U1 | C2/C3 moved beside VIN; explicit local bottom-side ground return, with bootstrap routing clear of it | Native path checks require C3→VIN below 2.2 mm and C2→VIN below 5.5 mm; fresh DRC and Gerber connectivity |

The 5 V/12 V selection remains a removable 2 mm cap on each three-pin header. The 140 fitted parts comprise 50 top and 79 bottom factory SMT placements, plus the top-side user-fitted MCU and ten through-hole parts. The PCB is 44 × 48 mm, four copper layers.

## Evidence to read

[Release check index](../reports/release_checks.json), [electrical budgets](../reports/electrical/electrical_checks.json), [native-route DC calculation and pin review](../reports/electrical/order_readiness.json), [768-corner averaged boost-loop screen](../reports/electrical/converter_loop.json), [ten input-transient cases](../reports/electrical/input_spice.json), [eight standalone power cases](../reports/electrical/boost_spice_partial.json), [firmware waveform replay](../reports/electrical/power_replay.json), and [completed power transient screening](../reports/electrical/boost_spice.json) with [earlier complete Rev G evidence](../../archive/README.md).

The DC calculation uses nominal 35 µm copper at 85°C and 20 µm via plating, with ideal pad contacts. It checks the 120 mV boost-input PCB allowance at a conservative 1.3 A boost branch, 510 mA 5 V branch, 130 mA logic load and 20 mA RGB/buffer load. Ground return, connectors, cables, actual copper tolerances and temperature rise need measurement.

Pin expectations are checked independently against manufacturer functions for the MCU, CAN transceiver, comparators and power switches. Native ERC/DRC, model/schematic/PCB parity and reconstructed Gerber connectivity check the actual delivered design rather than only the conceptual schematic.

## Limits and first-article acceptance

The vendor transient model uses an idealized upstream 5 V source; it does not simulate the LMR51430 loop, robot wiring, all silicon corners or an assembled board. The eFuse's floating OVCSEL setting is a roughly 13.8 V fault clamp, not a precision 13 V trip. Software rail monitoring supplements the independent hardware current limits. It does not make a fault-proof or reverse-powered output.

The passing short cases are **shorts to ground**. Directly joining the 5 V and 12 V rails is unsupported and can damage the 5 V switch or sensors: U4's OUT absolute maximum is 7 V. Its reverse-voltage blocking and software overvoltage detection do not guarantee survival of a 12 V cross-connection. See the [wiring limits](WIRING.md).

Qualify startup, both rails loaded together, the exact sensor models and cables, brownouts, cold/running shorts, temperature and CAN programming/recovery using the [validation procedure](VALIDATION.md). Record PCB revision H, exact BOM and firmware identity. Simulation and manufacturing checks reduce the risk of a first order; they cannot guarantee first-board success.

Primary pin/application references: [STM32F042](https://www.st.com/resource/en/datasheet/stm32f042t6.pdf), [TPS2596](https://www.ti.com/lit/ds/symlink/tps2596.pdf), [TPS61085](https://www.ti.com/lit/ds/symlink/tps61085.pdf), [TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf), [TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf), [LM339LV](https://www.ti.com/lit/ds/symlink/lm339lv.pdf).
