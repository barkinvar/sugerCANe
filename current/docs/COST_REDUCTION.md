# Rev H cost and assembly basis

Rev H adds the RGB indicator and inexpensive header programming to Rev G. Parts purchasing rises by approximately **$0.13 per board at ten boards**, from $28.81 to **$28.94**. The 12 V output eFuse, controlled startup, rail measurement and removable power jumpers remain unchanged. The resulting parts budget remains about **$6.19 below Rev E**.

| Ten-board parts purchasing | Per board |
|---|---:|
| Rev E | $35.14 |
| Rev F | $27.17 |
| Rev G | $28.81 |
| Rev H | $28.94 |

The RGB LED and logic buffer cost about $0.20 together at the ten-board tier. Local bypass capacitors, a reset pulldown, series resistor and the hand-fitted J8 header complete the change. Removing the former green LED and sharing existing passive purchase packs offsets part of the added cost. See the exact circuit and procurement regression below; consumed-part prices and minimum-pack cash costs differ.

| Boards | Parts purchasing per board | Lot parts purchasing |
|---|---:|---:|
| 1 | $55.28 | $55.28 |
| 5 | $33.21 | $166.03 |
| 10 | $28.94 | $289.45 |
| 25 | $26.54 | $663.42 |

Supplier observations are dated September 8–9, 2026. Prices include minimum packs, six terminals, three voltage headers, one service header and three loose caps. PCB fabrication, assembly, attrition, programming, functional testing, freight, tax and duty are extra. At quantity one, consumed parts are $36.11; minimum purchase quantities raise the cash outlay to $55.28. These are estimates, not an allocated cart or factory quote.

[Cost CSV](../bom/cost_estimate.csv) · [per-MPN purchases](../bom/cost_detail.csv) · [supplier observations](../bom/catalog_china.json) · [revision comparison](../reports/variant_verification.json).

## Assembly and programming choices

There are **130 top-side SMT placements across 55 exact MPN types** and **ten hand-soldered through-hole parts (49 joints)**. Hand fit J1–J6, J8 and JP101/JP201/JP301. The output eFuse's exposed-pad paste pattern and thermal vias remain required.

Compared with G, the two additional SMT types add approximately $3.06 per Standard assembly order in feeder fees, or $0.31 per board at ten, before placement/inspection changes. If both are charged extended types under Economic assembly, the increment is approximately $0.61 per board. Exact eligibility and charges require a quote. The per-board $0.13 parts increment is therefore not a complete assembled-price increment. [JLCPCB fee basis, checked 2026-09-09](https://jlcpcb.com/help/article/pcb-assembly-price).

The ordinary service header avoids buying a dedicated pogo cable. Reuse one programmer and mapped harness for all boards; an existing suitable ST-Link can avoid buying a new probe. [Programming options and one-time tool cost](STATUS_AND_PROGRAMMING.md).

## What double-sided assembly might change

The implemented board remains **52 × 74 mm**, with all components on top. Moving suitable small components underneath might reduce area by **15–25%**, approximately **52 × 56–63 mm**; a reasonable planning target is **52 × 60 mm, 19% smaller**. This is an engineering estimate, not a completed/routed alternative. Connectors, mounting clearances, hot power components and return-current paths limit the saving. The enclosure must also allow bottom component clearance.

At ten boards, budget **$3–6 extra per board** for assembly on both sides, assuming Standard assembly in both cases. JLCPCB's posted extra setup ($25.56) and extra stencil ($8.21) alone total $33.77 per order, or **$3.38 per board at ten**. Other fees, panelization and any change from Economic to Standard may change that substantially. Bare-PCB savings at this size may be small or zero within the same price bracket. Retain top-side assembly for this cost-sensitive ten-board batch unless the enclosure specifically needs the size reduction.

## Quotation and delivery

Ask the Chinese assembler to quote top-side SMT only, with exact-MPN allocation and functional test priced separately. Compare Economic and Standard eligibility using the same scope. LCSC stock does not guarantee JLCPCB allocation; TPS259620 stock was limited when observed. No supplier has been contacted or order placed.

The [assembly scenarios](../bom/assembly_scenarios.csv) are partial fee calculations. One-month delivery requires allocated-part dates, an assembly slot and destination-specific freight/customs timing. No arrival date is confirmed. [Factory instructions](FACTORY_ORDER.md).
