# Rev G cost and assembly basis

Rev G keeps the lower-cost 5 V-fed boost and passive sourcing from F, then adds protection, fault reset and voltage measurement. These additions cost about **$1.64 per board at ten boards**, while retaining about **$6.32 of the savings against E**.

| Ten-board parts purchasing | Per board |
|---|---:|
| Rev E | $35.14 |
| Rev F | $27.17 |
| Rev G | $28.81 |

The circuit uses the same B240A diode for the boost and output clamp, the same BSS138 transistor family for bias and inhibit control, and existing resistor/capacitor purchasing lines where appropriate. Precision divider and current-limit parts retain their specified tolerances.

| Boards | Parts purchasing per board | Lot parts purchasing |
|---|---:|---:|
| 1 | $53.23 | $53.23 |
| 5 | $32.95 | $164.74 |
| 10 | $28.81 | $288.12 |
| 25 | $26.36 | $658.93 |

Supplier observations are dated September 8–9, 2026. Prices include minimum packs, six terminals, three headers and three loose caps. PCB fabrication, assembly, attrition, programming, functional testing, freight, tax and duty are extra. At quantity one, consumed parts are $35.94; minimum purchase quantities raise the cash outlay to $53.23. These are estimates, not an allocated cart or factory quote.

[Cost CSV](../bom/cost_estimate.csv) · [per-MPN purchases](../bom/cost_detail.csv) · [supplier observations](../bom/catalog_china.json) · [revision comparison](../reports/variant_verification.json).

## Assembly choices

There are 126 top-side SMT placements across 53 exact MPN types and nine hand-soldered through-hole parts (39 joints). The 12 V eFuse has an exposed thermal pad; its supplied paste pattern and thermal vias must be retained. Standard reflow assembles it on the same side as the remaining components.

The board grows from 52 × 64 mm to 52 × 74 mm to provide room for the output protection and measurement circuit. This reverses F's area reduction; do not claim a PCB-area saving for G. Fabrication may still fall within the same supplier price bracket, but only a quotation establishes that.

Ask the Chinese assembler to quote top-side SMT only, with exact-MPN allocation and functional test priced separately. The user hand solders J1–J6 and JP101/JP201/JP301. Compare Economic and Standard eligibility using the same scope. LCSC stock does not guarantee JLCPCB allocation; TPS259620 stock was limited when observed. No supplier has been contacted or order placed.

The [assembly scenarios](../bom/assembly_scenarios.csv) are partial fee calculations. One-month delivery requires allocated-part dates, an assembly slot and destination-specific freight/customs timing. No arrival date is confirmed. [Factory instructions](FACTORY_ORDER.md).
