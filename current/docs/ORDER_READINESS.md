# Rev H pre-fabrication review

**Current order decision: HOLD.** The [JLC sourcing candidate](JLC_SOURCING.md) changes six passive MPN types at nine placements, preserving electrical values and layout. Native CAD/manufacturing and BOM consistency are checked. New power/input simulations are deferred until user approval, and U5 still needs exact-part sourcing. No physical board has been tested.

The electrical results below describe the preceding BOM at commit `8d4deb4`. Eight standalone power cases, ten input cases and sixteen firmware waveform replays passed there; both full coupled-startup traces remained incomplete. Retained reports are baseline evidence and have not been revalidated against the substituted BOM.

The native routed-copper calculation was rerun after widening 14 input-route segments from 0.5 to 0.7 mm. At the stated 85°C/nominal-copper assumptions, the buck-output-to-boost-input drop remains 51.14 mV against a 120 mV allowance. The worst protected-supply-to-jumper branch drops 42.49 mV at 300 mA; including jumper-to-connector copper brings it to **44.01 mV against the existing 60 mV allowance**. Each rail has a shared 300 mA sensor budget; this tests that entire load at each port in turn.

The DC model now recognizes overlapping track copper, contacts inside a straight segment and via connections on multiple layers, using the saved stackup depths. Buck-to-boost drop is measured between those two terminals; the older value was relative to the buck feedback tap. These figures therefore are not a direct before/after performance comparison. Six resistor-network regression fixtures check known resistance, segment subdivision, contacts, via depths, voltage-reference independence and genuine opens. The model still assumes ideal pad/via-annulus copper and does not solve current crowding or heating.

Routing cleanup uses 1,530 segments and 242 vias. The [routing gate](ROUTING_RULES.md) rejects pad overshoots, overlapping routes, tiny free jogs, end-cap-only joins, sharp free bends, unchamfered branches and unreviewed widths. All 77 routed nets satisfy the updated width policy. The ground-pour pass adds 0.25 mm width/gap rules, solid SMT ground connections, five local cutouts and a corrected J8.7 thermal-spoke angle. Three redundant J6.2 ground segments were removed; that pass preserved signal/power routes and all 242 vias. The latest pass changes only the 14 input widths and regenerated pours. Local converter/crystal path limits still pass. Fresh native DRC and independent reconstruction of all four exported copper layers find no shorts or opens; see the [routing results](../reports/routing_rules.json) and [four-layer copper review](../output/assembly/gerber_copper_review.pdf). These checks do not replace physical qualification.

The input screen uses 2 A through J1 → F1 → Q1 → U1, with finite via resistance. It is a DC screening point above the normal analytical 1.726 A at 6 V, not a fault-current or thermal rating.

| Input copper path | Width | Drop at 2 A, before → current |
|---|---|---|
| J1 to F1 (`VIN_RAW`) | 0.5 → 0.7 mm | 27.42 → 19.03 mV |
| F1 to Q1 (`VIN_FUSED`) | 0.5 → 0.7 mm | 41.14 → 30.90 mV |
| Q1 to U1 VIN (`VIN_PROT`) | 0.5 mm trunk / 0.8 mm local bypass | 91.44 mV, unchanged |
| Total input feed copper | All three paths | **160.00 → 141.37 mV** |

The input copper resistance falls about 12%, to 70.68 mΩ. At the normal analytical input current, its drop is approximately 122 mV. The existing 276 mΩ entry-resistance planning budget therefore leaves approximately 205 mΩ for the excluded fuse, MOSFET, contacts, cables and ground return; those items still require verification. The protected-input trunk cannot simply be widened in place without violating clearances near J1 and D3. The low-current U1 enable branch remains 0.25 mm.

All four layers retain nominal **35 µm (1 oz) copper**, now explicitly enforced by the DC screen. Inner 1 is the ground plane; inner 2 has 92 selected signal/service/control and low-current supply segments alongside ground. Native routing rules and independent exported geometry checks include both inner layers. [Individual PNG/SVG views](../README.md) and the four-page copper PDF are regenerated from the delivered Gerbers.

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
