# Cost and robot-use plan after Rev E

Planning date: 2026-09-08. Baseline: ten boards, three industrial photoelectric inputs, installation near an FRC mechanism. Exact sensor models, order quantity and shipping destination remain open. This is a proposal for a future revision; Rev E's circuit, firmware, BOM and manufacturing packages have not changed.

**Recommendation:** retain regulated sensor power, software input modes and CAN servicing. First reduce sensor connector and procurement costs, then evaluate a protected 5 V-to-12 V boost stage. Target approximately **$24–27 in parts per board at ten units**, before assembly, PCB, harness labor, enclosure, programming, freight and taxes. This is a design target supported by the calculations below, not a supplier quote.

## 1. Design around the robot job

The assumed job is detecting a game piece, mechanism position or limit state over CAN. Place the board on a fixed, protected surface near the sensors, with short sensor runs, a twisted CAN pair and independent cable strain relief. Account for mechanism movement when routing cables. Service should mean identifying a faulty channel and replacing a harness quickly in the pit.

Priorities are reliable sensing during motor-induced battery dips, secure wiring, prompt fault reporting and straightforward replacement. Low standby power, additional communications ports and high sensor supply current are secondary for this use.

Retain the existing targets while optimizing: 6–22 V board input, regulated 5 V and 12 V with 300 mA shared per rail, three independently configured digital inputs, and top-side component assembly. Four copper layers can coexist with one-sided assembly.

Three 30 mA sensors use only 90 mA, but that is a planning example, not the maximum load specification. Omron lists 30 mA maximum for several E3Z types and 35 mA for a through-beam emitter/receiver pair. Its 12–24 V ±10% supply specification means a nominal 12 V battery connection is insufficient when the battery drops below the sensor minimum. Motor load can depress the robot supply substantially. Preserve regulation unless the actual sensors and operating requirements justify giving it up. [Omron specifications](https://www.ia.omron.com/products/family/407/specification.html), [WPILib brownout explanation](https://docs.wpilib.org/en/latest/docs/software/roborio-info/roborio-brownouts.html).

## 2. Where the money goes

These values use the repository's dated ten-board purchasing model, including minimum purchase quantities. They are not a refreshed live cart. Component cash is allocated among schematic blocks without counting a part twice.

| Cost block | Parts per board | Interpretation |
|---|---:|---|
| Complete regulated 12 V block | $9.61 | U8, L2, current shunt, compensation, feedback and local capacitors |
| Six wire terminals | $7.85 | $4.77 for J4–J6 sensors; $3.08 for power and two CAN terminals |
| STM32F042K6T6 | $3.28 | Already supports the implemented modes and CAN update path |
| Everything else, including caps/accessories | $14.40 | 5 V power, protection, CAN, input conditioning, oscillator and other parts |
| **Total** | **$35.14** | Parts purchasing only |

The comparator costs about **$0.29 total** at this quantity; the complete electronic-bias addition versus D2 is approximately **$0.45 per board**. Removing either is a poor first cost target. [Detailed purchasing CSV](rev_e/bom/cost_detail.csv), [current cost summary](rev_e/bom/cost_estimate.csv), [Rev E cost basis](rev_e/docs/COST_REDUCTION.md).

Current Standard assembly modeling adds $123.63 per order for setup, stencil, 48 feeder types and fixtures. At ten boards, the resulting **$47.50 per board is still only a partial subtotal**, excluding PCB, placement, inspection, handling and shipping. This explains why a finished unit can exceed $50 even when parts are about $35. [Assembly scenarios](rev_e/bom/assembly_scenarios.csv).

The older cost-decision section in Rev E's packaged optimization document retains D2 figures ($34.69 and 46 SMT types). Use the current E cost CSV and the figures above for this proposal; historical release packages have not been regenerated for a planning-only document.

## 3. First hardware candidate: locking sensor connectors

Replace only J4–J6 with right-angle, through-hole **JST PA** connectors. Retain the power and CAN push terminals for flexible field wiring and easy access to the CAN backbone. JST PA provides a positive locking mechanism. The manufacturer's family matrix pairs the following header, housing and contact families. Exact wire insulation diameter, crimp tooling, pin numbering and enclosure access must still be checked. [JST PA catalogue](https://www.jst.co.uk/downloads/series/ePA-F%20%2821-03-26%29_1.pdf).

| Candidate | Ten-board purchase | Observed unit price | Batch cash |
|---|---:|---:|---:|
| S03B-PASK-2(LF)(SN), right-angle 3-pin header | 30 | $0.2363 | $7.089 |
| PAP-03V-S, mating housing | 30 | $0.0543 | $1.629 |
| SPHD-001T-P0.5, crimp contact | 100 for 90 positions | $0.0103 | $1.030 |
| **Total for three connector pairs per board** | | | **$0.9748/board** |

Sources observed during this review: [header](https://www.lcsc.com/product-detail/C265095.html), [housing](https://www.lcsc.com/product-detail/C161864.html), [contact](https://www.lcsc.com/product-detail/C246755.html). Listed stock is not allocated inventory.

The material reduction is **$4.773 − $0.9748 = $3.7982 per board**. This includes mating housings and contacts, but excludes wire, crimp tooling, crimp labor, spares, shipping and inspection. Compare a supplier-made harness against hand crimping before selecting this route. A $4 harness labor charge would erase the material saving.

The cited contact suits AWG 22–26 and 1–1.5 mm insulation diameter; verify the actual sensor cable. An incompatible cable may require a correctly specified contact or an adapter harness, which changes the economics. Require pull tests, polarity checks, vibration checks and a spare preassembled harness. Preserve consistent power/ground/signal order. Avoid making power and CAN plugs physically interchangeable in a later connector consolidation.

Continue hand soldering through-hole parts as already planned. That saving is already in the baseline and must not be claimed again. Do not replace locking connectors with loose friction-fit jumper leads.

## 4. Largest redesign candidate: a protected boost from internal 5 V

Evaluate this architecture:

```text
Protected robot supply → existing 5 V buck → logic supply
                                         → existing protected 5 V sensor output
                                         → 12 V boost → output protection → 12 V sensors
```

The boost must connect to **V5_INTERNAL**, before the existing 5 V sensor current limiter. Connecting it to SENSOR_5V would consume that output's limited budget.

The **TPS61085DGKR** is a concrete candidate: TI specifies a 2.3–6 V input range and includes a 12 V/300 mA application. LCSC lists $0.4885 at ten with stock observed. This supports screening it for a post-regulator boost, not connecting it to the 6–22 V robot input. [TI datasheet](https://www.ti.com/lit/ds/symlink/tps61085.pdf), [supplier observation](https://www.lcsc.com/product-detail/C113659.html).

Its IC price is much lower than the current U8's $5.42, but the **whole replacement power block** is the comparison. Include the inductor, rectifier, effective output capacitance, compensation, feedback, short protection, output-health detection and any extra upstream protection/capacitance. Reserve **$4–6 per board for that complete replacement and incremental upstream changes**, giving a planning saving of **$3.61–5.61** versus $9.61. This allowance has not been established by a complete replacement BOM.

An ordinary boost retains a DC path through its inductor and diode when switching stops. A sensor-output short therefore needs protection that actually interrupts or limits that path. Screen a **TPS259541DSGR** output eFuse: this is the 13.7 V clamp, auto-retry option, listed at $0.5854 for the relevant purchase quantity. Its nominal clamp is a fault limit, not a regulated sensor voltage. Check maximum clamp voltage, short behavior, reverse current and thermal limits in the complete circuit. **TPS259531 is a 5.7 V clamp variant and is unsuitable at this 12 V output.** The existing TPS2553 also cannot simply move to the 12 V output. [TI variant table](https://www.ti.com/lit/ds/symlink/tps2595.pdf), [12 V eFuse candidate price](https://www.lcsc.com/product-detail/C2155673.html).

Evaluate the unused fourth LM339LV comparator for 12 V undervoltage detection, plus the eFuse fault signal. That could preserve rail-health reporting without another comparator IC. An eFuse's fault output alone does not prove that a boost converter has reached 12 V. Keep threshold, reference-loading and startup behavior in the circuit review.

The first current check, using deliberately assumed 85% boost efficiency, is:

```text
12 V × 0.30 A / (5 V × 0.85) = 0.847 A from internal 5 V
+ 0.30 A for 5 V sensors
+ 0.10 A provisional logic/bias allowance
= approximately 1.25 A from the 5 V buck
```

This is below the buck's nominal 2 A rating, but does not establish operation across temperature, startup, dropout or overload. Cascaded conversion adds losses and couples 12 V load transients into the logic power source. A 12 V short or repeated protection retry must not reset the MCU, corrupt CAN traffic or invent input counts. Check simultaneous full rail loads at 6/12/22 V input, remote sensor voltage, cold start, short removal and hot enclosure conditions. A single failed gate rejects this architecture or requires additional protection included in the cost.

As a fallback, screen an integrated-disconnect boost such as TPS61378-Q1 and compare its complete circuit cost. Keep the existing buck-boost if the protected replacement does not save at least about $3 per board after assembly changes. [TI alternative](https://www.ti.com/product/TPS61378-Q1).

## 5. Procurement and assembly work

1. **Select against the assembler's actual inventory.** LCSC stock and JLCPCB Basic/Extended classification are different facts. Obtain separate Economic and Standard line-item estimates for 5, 10 and 25 boards. No supplier has been contacted or order placed by this review.
2. **Reduce part types where electrically justified.** Start with crystal/load-cap sourcing, 1 nF input capacitors, 1 µF logic capacitors and ordinary resistors. Preserve C0G where required, precision feedback, resistor voltage/power ratings and effective MLCC capacitance. Target $1–2 in parts outside the replaced 12 V block; this is an unquoted target. Do not count power-stage capacitor savings a second time.
3. **Retain low-cost protection and the clock.** Keep the input fuse, reverse-polarity circuit, CAN/signal transient protection, comparator hysteresis, bias blocking diodes and CAN crystal. Source equivalent parts rather than deleting their functions. Review redundant bleed loading only after the unpowered backfeed budget; the resistor cash is negligible.
4. **Quote a smaller four-layer board after placement.** About 52 × 60 mm is a layout goal, not a completed layout. It would reduce area 14.3% from E, but PCB/panel pricing need not fall by that percentage. Preserve mounting, connector latch access, switch-current paths and a continuous ground reference. Keep all components on top.
5. **Count programming, test and harness labor.** Reuse the SWD fixture and CAN acceptance tools, but measure time on pilot units. A factory-installed MCU or connector is only cheaper if the whole procurement/assembly process is cheaper.

JLCPCB currently publishes $3.07 per Extended feeder type for Economic and $1.53 per Basic/Extended type for Standard. If the revised board qualifies for Economic with 20 charged types, its modeled setup/stencil/feeders subtotal is $71.11 per order, compared with E's $123.63 Standard setup/stencil/feeders/fixtures. The difference is **$5.25 per board at ten**, before all other fee differences. This is a sensitivity example, not a proven saving. Removing ten charged types saves $30.70/order in Economic or $15.30/order in Standard. Do not add those savings to a service comparison that already assumes the reduced type count. [Current assembly fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price).

Two tempting sourcing changes do not currently support claimed savings: the exact STM32's LCSC page is out of stock, and the non-automotive TPS552872RYQR listing is $6.1931 at ten with only five units observed, higher than the current automotive part in the repository budget. Keep the existing MCU architecture for this revision; no external CAN controller or extra memory is needed for the current functions. [MCU listing](https://www.lcsc.com/product-detail/C69216.html), [converter listing](https://www.lcsc.com/product-detail/C22427496.html).

## 6. Features to keep, improve or defer

| Decision | Recommendation for this robot use |
|---|---|
| Keep | Three channels, electronic NPN/PNP/push-pull selection, comparator protection, regulated rails, CAN ID/configuration/update/recovery, SWD recovery contacts and both CAN terminals |
| Improve mechanically | Enclosure with cable tie points/strain relief, clearance from robot metal, clear connector labels and a captured power-cap retainer. The current power caps are friction retained; changing the input bias to software did not solve their retention |
| Improve in firmware | Expose useful reset/rail-fault/CAN-error history and configurable sensor startup blanking; retain the existing identification LED and live input view. Add only missing diagnostics after checking present telemetry. Verify flash/RAM headroom |
| Add if fault tests justify it | Per-port power protection so a damaged sensor cable does not disable the others. Budget and coordinate it with shared rail limits; a resettable fuse alone does not guarantee fast isolation. Current drivers also invalidate all inputs on a rail fault, so partial-operation behavior needs an explicit firmware change |
| Optional modest addition | Three channel indicator LEDs if pit testing shows the GUI and sensor LEDs are insufficient. Show logical state rather than float-probe transitions; use actual spare GPIOs, not extra field-signal loading |
| Defer | Analog measurement, quadrature/high-speed encoders, extra channels, CAN-FD, USB-C, wireless and motor outputs until a real attached device needs them. They expand validation and do not improve the primary photoelectric-sensor job |
| Conditional simplification | If every intended sensor is 12 V, a fixed-12 V-port variant can remove the three power caps/headers and 5 V sensor-output stage, about $1.35 gross parts in the current model. Keep internal 5 V for logic and the proposed boost. This variant loses external 5 V support and is excluded from the recommended savings |

Do not remove the 12 V regulator and label the battery output “12 V.” That could gross-remove about $9.61 before replacement protection, but loses regulation during battery sag. Do not remove the second CAN terminal merely to save about $1.03; account for the replacement bus harness and pit service consequences.

## 7. Budget and execution order

| Ten-board scenario | Estimated parts per board | Confidence |
|---|---:|---|
| Current Rev E | $35.14 | Existing dated purchasing model |
| Locking sensor connectors only | $31.34 | Connector-material arithmetic; excludes extra harness labor |
| Connector change + protected power redesign | $25.74–27.74 | Power-block allowance, pending complete design/BOM |
| Above + separate passive sourcing target | **$23.74–26.74** | Planning range; round to **$24–27** |

These rows do not include extra optional features or assembly savings. With 20 Economic charged types, the $24–27 target becomes roughly **$31–34 in parts plus setup/stencil/feeders**, still excluding PCB, solder placement, inspection, other handling, harness labor, enclosure, programming/test, freight and tax. The present research does **not** establish a delivered $30 unit.

1. **Freeze requirements and prices:** record exact sensors, longest cable, shortest pulse, simultaneous rail loads, quantity and delivery destination; confirm the candidate MPNs and mating harness cost. Keep 300 mA/rail unless a deliberate specification change is accepted.
2. **Complete a paper design and BOM:** power current/thermal/short calculations, comparator health thresholds, pin allocation, startup/fault semantics and full factory fee comparison. Advance if combined net parts savings remain at least $6/board at ten without sacrificing the core specification.
3. **Create a separate hardware revision:** native schematic/PCB, model parity, routed top-side assembly, BOM/CPL, mechanical fit, firmware identity, documentation and matching manufacturing exports. Preserve Rev E as the baseline.
4. **Build 2–5 pilot units:** qualify representative sensors, mixed input modes, sag/load steps, short/recovery behavior, CAN updates, cable pull and vibration. Test each input after power recovery without false counts. A layout check cannot replace these measurements.
5. **Order 10–25 only after pilot acceptance:** compare total cash as well as unit price and include spares. A larger first order is not justified solely by lower unit allocation on an unbuilt design. Confirm allocated parts and destination-specific shipping before relying on a one-month deadline.

The root README links this planning document. Existing board releases remain the reference for what is actually implemented.
