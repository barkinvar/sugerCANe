# Rev E cost and assembly basis

Rev E preserves D2's lower-cost passive sourcing, top-side SMT assembly and user-soldered through-hole parts. It adds electronic bias: six MOSFETs, six gate resistors and one rail-bleed resistor. Three existing pull-up resistors change to 1 kΩ, using an existing BOM MPN. The three unpurchased bias solder selectors disappear.

| Boards | Total parts purchase per board | Difference from D2 |
|---|---:|---:|
| 1 | $56.42 | +$1.15 |
| 5 | $40.96 | +$0.56 |
| 10 | $35.14 | +$0.45 |
| 25 | $32.72 | +$0.49 |

These September 8, 2026 estimates include supplier minimums, terminals, power headers and three loose caps. PCB, assembly, attrition, programming/test, freight, tax and duty are extra. First-tier consumed parts are $44.69; purchasing enough minimum packs for one board costs $56.42. Batch purchasing remains the strongest saving without changing the product's hardware functions.

[Cost CSV](../bom/cost_estimate.csv), [supplier observations](../bom/catalog_china.json), [BOM](../bom/BOM_grouped.csv) and [assembly scenarios](../bom/assembly_scenarios.csv) expose the assumptions. AO3401A is [LCSC C15127](https://www.lcsc.com/product-detail/C15127.html); BSS138BK,215 is [C282529](https://www.lcsc.com/product-detail/C282529.html). The six MOSFETs consume about $0.49 at first supplier tiers. Stock observations are not factory allocations; these exact parts still need confirmed sourcing.

The board grows from 52 × 64 to 52 × 70 mm, a 9.4% area increase. All 111 SMT parts remain on top, with nine through-hole parts hand soldered after factory assembly. There are 48 SMT MPN types, two more than D2. This adds $3.06 per order in the published Standard feeder-fee model, plus placement and any quote adjustments. No second-side assembly fee is introduced. The [published assembly fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price) is an estimate input, not a quotation.

The main remaining expenses are the exact MCU, regulated 12 V power stage, horizontal connectors, multilayer PCB and small-order assembly overhead. The comparator is retained because it gives the existing digital threshold/hysteresis behavior across the input range. Removing it or the power protection solely to lower the BOM would require a separate electrical redesign and qualification.

Request the [exact-MPN SMT quote](FACTORY_ORDER.md), confirm Economic/Standard eligibility, component allocation and destination-specific express shipping. China delivery within one month is not confirmed; the earlier 2–4 week allowance is a planning estimate subject to sourcing, production and customs. No order or supplier contact has been made.
