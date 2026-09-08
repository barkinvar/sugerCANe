# Revision history

[Repository overview](README.md)

| Revision | Location | Main changes | Status |
|---|---|---|---|
| A | [Rev A](REV_A.md), root design directories | Four inputs, 96 × 96 mm, 6–18 V target, Würth terminals, 2.54 mm service header | Archived design baseline; unbuilt |
| B, earlier connector iteration | [Historical package](rev_b/history/before_horizontal_connectors/README.md) | Compact three-input design with angled /135 terminals | Superseded; retained for traceability |
| B, current | [rev_b](rev_b/README.md) | 60 × 68 mm, 5–22 V target, horizontal Weidmüller /90 terminals, compact pogo pattern | Full-feature hand-assembly prototype |
| C Lite | [rev_c](rev_c/README.md) | 52 × 56 mm, 89 fitted parts, 6–22 V, solder selectors, standalone protected power, fixed thresholds, protocol v2 | Simplified successor; unbuilt prototype |
| B-2 | [rev_b2](rev_b2/README.md) | Same B circuit/geometry; 49 equivalent passive placements changed and eight unchanged MPNs resourced; factory BOM/CPL packet | Full-feature factory-assembly prototype |
| D SC12 | [rev_d](rev_d/README.md) | 52 × 64 mm, four layers, regulated 12 V + 5 V, 104 fitted parts, rail-health handling, protocol v3 | Regulated industrial-sensor successor; unbuilt prototype |
| D-2 SC12 | [rev_d2](rev_d2/README.md) | Same D circuit and telemetry; 0.5.0 CAN service/bootloader; 27 passive substitutions, sourcing changes, removable 2 mm voltage headers; 98 SMT + 9 hand-fitted parts; factory BOM/CPL | Cost-reduced assembly variant; unbuilt prototype |
| E SC12 | [rev_e](rev_e/README.md) | Software NPN/PNP/push-pull/float/keeper bias; 52 × 70 mm; 111 SMT + 9 hand-fitted parts; hardware 5/protocol 4 | Independent per-input setup; unbuilt prototype |

## A to B

PCB area falls by 55.7%, from 9,216 to 4,080 mm², by reducing the input count to three and rearranging the power, input and programming sections. Rev B supplies a buck-plus-boost nominal 5 V sensor rail over its 5–22 V connector-input target. Both revisions supply switched battery voltage as a separate rail.

B uses three 2-pole Weidmüller 1824420000 and three 3-pole 1824430000 terminals. Their /90 wire entry is parallel to the PCB. Two solder pins per pole require the specific 7 mm row spacing; the earlier /135 footprint is not interchangeable. A Phoenix PTSM connector was considered during development but is not in either current B BOM.

The B/B-2 service pads use the TC2050-IDC-NL mechanical contact pattern with a **custom electrical mapping**. Do not use an assumed standard ARM cable pinout. A's 2.54 mm service header also has a project-specific pinout; follow the matching wiring guide.

The ten B/B-2 loose shunts provide three sensor voltage selectors, three input bias selectors, three input threshold selectors and one CAN termination selector. These make sensor configuration visible and avoid adding electronic switching hardware. Their settings and the retained bypass capacitors are explained in the wiring and passive-review guides.

## B to B-2

B-2 changes 37 resistors to same-value UNI-ROYAL 0805 equivalents and twelve 100 nF capacitors to Samsung CL21B104KCFNNNE (100 V, X7R, 0805). Nominal electrical values, PCB pads/tracks, connector MPNs and firmware remain equivalent to B. See the exact [part changes](rev_b2/docs/PART_CHANGES.md) and [variant verification](rev_b2/reports/variant_verification.json).

B-2 keeps 128 SMT and 16 through-hole placements, plus ten loose configuration shunts. A factory must source the MCU and Weidmüller terminals and review placement rotations, panel handling and THT assembly. Estimated consumed component cost is $46.35 versus B's $59.30; this is not an assembled-board quote.

## Documentation and 3D model refresh

The repository overview now covers all revisions and links their matching CAD, BOM, firmware instructions and releases. All maintained guides identify their revision. Final renders are embedded in the overviews.

The B/B-2 horizontal connector models now use official Weidmüller STEP geometry, with a documented rigid translation to the existing pin origins and project display colors. Earlier simplified boxes are superseded. The PCB routing, holes, BOM connector codes and electrical targets are unchanged by this visual correction. [Connector details](rev_b/docs/CONNECTORS.md).

Git excludes local browser captures, compiler intermediates, downloaded test dependencies, router scratch boards and raw simulation traces. Release ZIPs, native designs, final firmware images, reports and published review images remain tracked. Previously tracked ignored files are removed from the current Git index while retained locally; past commits are not rewritten.

All revisions remain unbuilt and require their documented physical qualification. Historical packages retain their original reports and checksum identities; current packages include the refreshed guides and visuals.

## B/B-2 to C Lite

Rev C is the simplified three-input interface: 89 fitted components versus 144, 33 resistors versus 63, and 29 capacitors versus 34. PCB area is 2,912 mm² versus 4,080 mm², a 28.6% reduction. All parts are placed from the top: 83 SMT plus six horizontal Weidmüller terminals. Two mounting holes replace four. The programming pattern remains compact TC2050 with the documented custom pin map.

One direct 5 V buck replaces buck-plus-boost, changing the minimum supply target from 5 V to 6 V. Both rail current-limiters remain, but software enable, rail ADC monitoring and fault-report networks are removed. Sensor power is hardware-only, with power-cycle reset after a latched overload. Three inputs use one fixed threshold reference, six solder selectors choose power/bias, and a seventh selects CAN termination. There are no purchased pin headers or shunts.

Protocol v2 uses different API IDs and new Lite Java/C++ drivers. Old rail-health fields are absent; a CAN input state cannot establish sensor power health. Broadcast disable stops telemetry and aborts pending transmissions, while independent sensor power continues. Old firmware/host drivers must not be paired with Rev C.

[Rev C simplification details](rev_c/docs/SIMPLIFICATION.md), [wiring](rev_c/docs/WIRING.md), [qualification](rev_c/docs/VALIDATION.md), [factory packet](rev_c/order/RevC_Lite_Factory_Upload.zip). The $43.90 dated component estimate is not a China assembly quote. Previous revision native files and release packages remain unchanged.

## C Lite to D SC12

Rev D replaces the battery sensor output with a synchronous 12 V buck-boost supply while retaining the 5 V rail, three fixed-threshold inputs, horizontal connectors, compact programming pattern and seven solder bridges. It targets 6–22 V input and 300 mA per shared rail. Board area grows from 2,912 to 3,328 mm²; the four-layer construction reserves both inner layers for ground.

Fitted parts increase from 89 to 104, including the integrated converter, shielded 3.3 µH inductor, Kelvin-connected 0.1 ohm resistor and local capacitors. The separate battery high-side switch and its support parts are removed. Most passives remain 0805 or larger; four 0402 capacitors and the converter HotRod QFN require more careful reflow than C. Dated DigiKey quantity-one parts increase by $10.99 to $54.89; no factory PCBA quote is claimed.

Firmware 0.4.0/protocol v3/hardware 4 reports qualified 12 V PG and 5 V no-fault indications, freezes counters during faults and re-baselines after 100 ms stable recovery. Drivers reject stale/faulted inputs and wrong protocol versions. Neither indication is a calibrated voltage measurement. The 12 V current limit recovers automatically; the 5 V output switch retains latch-off behavior.

[Rev D design review](rev_d/docs/SIMPLIFICATION.md), [wiring/model exceptions](rev_d/docs/WIRING.md), [prototype qualification](rev_d/docs/VALIDATION.md), [factory packet](rev_d/order/RevD_SC12_Factory_Upload.zip). A/B/B-2/C native designs and their released artifacts remain unchanged. Enclosure design follows later user review of the D mechanical handoff.

## D to D-2

D-2 keeps the electrical features, outline, four copper layers and hardware-4/protocol-v3 identity. It changes 16 ordinary 0805 resistors and eleven 100 nF bypass capacitors to documented equivalents, selects lower supplier prices for unchanged MPNs, and replaces three solder power selectors with removable 2 mm headers/caps. Sensor-area routing changes to accommodate plated holes; bias and CAN termination remain solder settings. All components stay on the top side.

Factory files contain 98 SMT placements. The user fits six terminal blocks and three headers and supplies three caps. D-2’s first-tier consumed-parts estimate is $44.16 versus D’s $54.89; minimum-order purchasing is $40.40 / $34.69 / $32.23 per board at 5 / 10 / 25 boards. These exclude PCB, assembly and freight. [Price assumptions](rev_d2/docs/COST_REDUCTION.md), [factory scope](rev_d2/docs/FACTORY_ORDER.md), [wiring and retention](rev_d2/docs/WIRING.md). Earlier releases remain intact.

D-2 now includes [CAN setup/update firmware and tools](rev_d2/docs/CAN_SERVICE.md), with protected bootloader and one-time SWD migration. Normal hardware-4/protocol-v3 telemetry remains compatible; 0.4.0 is retained in Rev D and history. Software verification passes; physical qualification remains open.

## D2 to E

Rev E removes the three input-bias solder selectors and replaces them with six MOSFETs and seven added resistors. Each channel independently supports pull-up, pull-down, bias off, floating detection or keeper, with software active-state interpretation. The pull-up is referenced to 3.3 V, independent of the removable 5 V/12 V sensor-power caps. The comparator and field protection remain.

The board grows 6 mm in height to 52 × 70 mm while preserving top-side assembly and critical converter/crystal routes. There are 120 fitted parts plus three loose caps. Ten-board parts purchasing is approximately $35.14 per board, about $0.45 above D2, excluding fabrication/assembly/shipping. Firmware 0.6.0 uses hardware identity 5 and protocol 4, with persistent CAN service and Java/C++ runtime mode APIs. Prior firmware images are rejected; use the complete matching revision.

[Input behavior and limitations](rev_e/docs/INPUT_MODES.md), [wiring](rev_e/docs/WIRING.md), [cost basis](rev_e/docs/COST_REDUCTION.md), [qualification](rev_e/docs/VALIDATION.md). This is an independent implementation with similar input-mode choices to CANdi; it does not speak Phoenix or GrappleHook.
