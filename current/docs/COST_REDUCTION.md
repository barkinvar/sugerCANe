# Rev H cost and assembly basis

The [JLC sourcing candidate](JLC_SOURCING.md) lowers the ten-board parts estimate from $28.99 to **$25.68 per board before SMT attrition**. With a conservative allowance for displayed assembly losses/minimums, budget **$26.55 per board**. MCU sourcing is unresolved, so its quoted catalog price remains provisional. This is a supplier/pricing update with six earlier passive substitutions and the C1 reflow replacement, not a reduction in power protection.

| Ten-board basis | Parts per board |
|---|---:|
| Previous mixed-supplier H estimate, before SMT attrition | $28.99 |
| JLC-matched H estimate, before SMT attrition | $25.68 |
| JLC-matched SMT parts with conservative attrition | $17.85 |
| Hand-fitted parts and three caps | $8.70 |
| Combined candidate budget with conservative attrition | **$26.55** |

JLC prices/stock were checked September 9 in California (September 10 UTC). Hand-purchased parts retain their September 8 supplier observations. Most savings come from direct catalog matching and purchase minimums. The $3.31 difference compares estimates before SMT attrition; it is not a guaranteed invoice saving. PCB fabrication, assembly, programming/testing, freight, tax and duty remain extra.

| Boards | Parts purchasing per board, before SMT attrition | Lot parts purchasing |
|---|---:|---:|
| 1 | $40.80 | $40.80 |
| 5 | $28.16 | $140.79 |
| 10 | $25.68 | $256.75 |
| 25 | $23.56 | $588.89 |

These arithmetic scenarios do not establish supported assembly quantities or stock for that lot. The sourcing audit checks ten boards only, and currently identifies the MCU shortage. At one board, fitted consumption is $31.58 while purchase minimums raise cash outlay to $40.80; an actual PCBA order has its own minimum quantity.

[Cost CSV](../bom/cost_estimate.csv) · [per-MPN purchases](../bom/cost_detail.csv) · [public JLC evidence](../bom/jlc_sourcing.json) · [sourcing audit](../reports/manufacturing/jlc_sourcing.json).

For historical context, the original H RGB/header change added $0.18 in parts versus G at the old supplier-price basis. Repricing the whole BOM now means the current H-to-G budget difference is not an isolated LED cost. Layout and silkscreen add no fitted parts, board area or second-side assembly.

## Assembly and programming choices

There are **130 top-side SMT placements across 55 exact MPN types** and **ten hand-soldered through-hole parts (49 joints)**. Hand fit J1–J6, J8 and JP101/JP201/JP301. The output eFuse's exposed-pad paste pattern and thermal vias remain required.

Compared with G, the two additional SMT types add approximately $3.06 per Standard assembly order in feeder fees, or $0.31 per board at ten, before placement/inspection changes. D10 requires Standard PCBA, so an Economic assembly comparison is not available for the current BOM. Those historical increments are not a complete assembled-price comparison for the newly sourced BOM. [JLCPCB fee basis, checked 2026-09-09](https://jlcpcb.com/help/article/pcb-assembly-price).

The recessed service socket avoids buying a dedicated pogo cable. Reuse one programmer and mapped harness for all boards; an existing suitable ST-Link can avoid buying a new probe. [Programming options and one-time tool cost](STATUS_AND_PROGRAMMING.md).

## What double-sided assembly might change

The implemented board remains **52 × 74 mm**, with all components on top. Moving suitable small components underneath might reduce area by **15–25%**, approximately **52 × 56–63 mm**; a reasonable planning target is **52 × 60 mm, 19% smaller**. This is an engineering estimate, not a completed/routed alternative. Connectors, mounting clearances, hot power components and return-current paths limit the saving. The enclosure must also allow bottom component clearance.

At ten boards, budget **$3–6 extra per board** for assembly on both sides, assuming Standard assembly in both cases. JLCPCB's posted extra setup ($25.56) and extra stencil ($8.21) alone total $33.77 per order, or **$3.38 per board at ten**. Other fees, panelization and any change from Economic to Standard may change that substantially. Bare-PCB savings at this size may be small or zero within the same price bracket. Retain top-side assembly for this cost-sensitive ten-board batch unless the enclosure specifically needs the size reduction.

## Quotation and delivery

Use the matched JLC BOM/CPL for **Standard PCBA** with top-side SMT. The exact OPSCO LED is Standard Only. Posted setup/stencil/loading fees total $134.34 including two fixtures at ten boards; placement, X-ray, PCB/panel rails, handling and shipping are additional. Standard charges loading for all 55 types, including basic/preferred parts; additional resistor swaps would save only pennies, so they were not implemented. The C1 replacement adds $0.063 per board at this quantity and removes the known peak-temperature conflict; factory dwell/profile confirmation remains required. [Assembly audit](JLC_SOURCING.md#solder-process-audit).

The [assembly scenarios](../bom/assembly_scenarios.csv) are partial fee calculations, before attrition. No supplier has been contacted or order placed. The exact MCU must be sourced, while U9 and L2 have limited stock. No inventory is allocated.

One-month delivery requires confirmed component arrival, an assembly slot and destination-specific freight/customs timing. No arrival date is confirmed. [Factory instructions](FACTORY_ORDER.md).

The MCU Global Sourcing charge is not yet quoted. DigiKey’s observed ten-piece price is $3.277 each, but JLC’s procurement price/fees can differ; do not treat the retained provisional MCU catalog price as an accepted quote.
