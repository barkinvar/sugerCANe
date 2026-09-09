# Rev F cost and assembly basis

Rev F implements the approved protected boost, passive sourcing and PCB-area reductions. The existing connectors, removable voltage jumpers, electronic input modes and top-side-only assembly are retained.

| Change | Ten-board purchasing saving per board |
|---|---:|
| Protected 5 V → 12 V stage and shared-part price breaks | $6.66 (original target $3.60–5.60) |
| Passives outside the replaced stage | $1.30 (target $1–2) |
| Total parts saving against Rev E | About $7.96; about 22.7% |
| PCB area: 52 × 70 → 52 × 64 mm | 8.6% less area; dollar saving requires a quotation |

The unrounded baseline is $35.1354 and Rev F is $27.1738; separately rounded displayed prices differ by $7.97. Shared MPN price breaks are attributed to the power-stage line so they are not counted twice. [Reproducible comparison](../reports/variant_verification.json).

| Boards | Parts purchasing per board | Parts purchasing for the lot |
|---|---:|---:|
| 1 | $47.80 | $47.80 |
| 5 | $30.93 | $154.67 |
| 10 | $27.17 | $271.74 |
| 25 | $24.98 | $624.61 |

These September 8, 2026 observations include supplier minimums, terminals, headers and three loose caps. PCB fabrication, assembly, attrition, programming/test, freight, tax and duty are extra. First-tier consumed parts total $34.56; buying minimum packs for one board costs $47.80. The [cost CSV](../bom/cost_estimate.csv), [per-MPN purchases](../bom/cost_detail.csv), [supplier observations](../bom/catalog_china.json) and [BOM](../bom/BOM_grouped.csv) expose the arithmetic. This is not a PCBA quotation or allocated stock.

## What changed outside the power stage

| References | Change | Electrical scope |
|---|---|---|
| C101, C201, C301 | Same CC0805JRNPO9BN102, sourced from LCSC C62774 | 1 nF, 50 V, C0G, 0805 unchanged |
| C7, C23 | CC0805KKX7R9BB105 → Samsung CL21B105KBFNNNE, C28323 | 1 µF, 50 V, X7R, 0805 unchanged |
| C8, C24 | TMK212AB7475KG-T → Samsung CL21B475KAFNNNE, C98195 | 4.7 µF, 25 V, X7R, 0805 unchanged |

The LDO capacitor screen assumes 50% DC-bias retention and further temperature/tolerance/aging allowances, leaving about 1.71 µF against a 1 µF requirement. This is an engineering allowance, not a measured manufacturer curve. Validate effective capacitance/ESR and startup on the prototype. Precision input resistors, crystal loading, MCU, CAN and protection parts outside the replaced stage are retained.

## Assembly and delivery

There are 110 top SMT placements across 48 exact MPN types and nine user-soldered through-hole parts (39 joints). The new boost has visible VSSOP leads and removes the former QFN power package, Kelvin shunt and four 0402 capacitors. Fewer placements and simpler inspection may help, but the published Standard setup/stencil/feeder/fixture subtotal remains $123.63 per order before the other charges. A smaller PCB can also stay in the same minimum-price tier.

[Partial assembly scenarios](../bom/assembly_scenarios.csv) use the [published JLCPCB fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price). Economic eligibility, exact part matching, procurement charges and allocation need confirmation. LCSC stock does not establish JLCPCB Basic/Extended classification or order eligibility. Request the same top-SMT-only scope from the chosen Chinese assembler; the user fits the large terminals and power headers.

No supplier has been contacted and no order or delivered quotation is included. Delivery inside one month cannot be confirmed without the lot quantity, destination, allocated parts, assembly slot and courier/customs allowance. [Factory handoff](FACTORY_ORDER.md).
