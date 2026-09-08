# Revision C Lite design plan

Purpose: a compact three-channel digital sensor-to-CAN interface that is easier to assemble than B/B-2. Previous revisions remain available. This is an unbuilt prototype, not a validated commercial product.

## Design choices

- One 5 V buck, then a 3.3 V LDO. Supply target becomes **6–22 V**; no guarantee of regulated 5 V from a 5 V input.
- Three digital inputs supporting 3.3/5 V push-pull and industrial NPN/PNP outputs. One shared fixed threshold, no separate industrial threshold or onboard 3.3 V pullup.
- Horizontal Weidmüller 1824420000 and 1824430000 connectors, using their official STEP models.
- Two solder selectors per input: 5 V/battery power, and NPN/PNP/open bias. Default open. No pin headers or shunts. Optional CAN termination also uses solder pads.
- Retain both hardware current limiters in standalone latch-off operation. Power-cycle after correcting an overload. Remove software enables, rail monitoring dividers, fault GPIO networks, and associated firmware.
- One status LED. Retain MCU clock, local bypass, input TVS/filter/hysteresis and CAN protection.
- Mostly 0805 passives, leaded MCU/transceiver/comparator. The battery limiter still has an exposed thermal pad: use the heatbed/paste step for that IC.
- Final board: **52 × 56 mm**, 28.6% less area than B. The initial 52 mm square trial crowded the clock and input filters, so it was lengthened. Two M3 mounting holes; all 89 fitted parts on top.

## Evidence and verification

1. Use KiCad 10 native editable schematic and PCB; generate from explicit component/net data with portable project libraries.
2. Check manufacturer pin tables, absolute/operating limits, application circuits and package drawings. Use DigiKey for exact orderable MPNs and dated stock/price observations.
3. Calculate input threshold tolerance/leakage budgets, 30 V input stress, buck output/effective capacitance and current-limit ranges. Distinguish datasheet guarantees from engineering assumptions.
4. Check schematic ERC, independently compare exported netlist against model and PCB, then native PCB DRC. Protect switching, feedback, clock, bypass and programming geometry before general routing.
5. Audit exported Gerbers, drill files, placement and BOM against native PCB; inspect actual CAD renders and schematic/assembly PDFs.
6. Update the small CAN protocol and host driver together; compile firmware and exercise debounce, counter, configuration, stale data and fault paths in host tests.
7. Package fabrication/assembly files, wiring guide, firmware, measured-vs-unmeasured validation status and release hashes. Update revision index and push the reviewable result to Git.

## Prototype qualification still required

Power-up and load steps at 6/12/22 V; sensor rail shorts and recovery; brownout; both CAN bus states and bus-off recovery; crystal startup; input threshold/pulse sweeps; ESD/transients; thermal measurements; connector and programming-fixture fit. Passing software checks does not replace these physical tests or establish FRC rules compliance.
