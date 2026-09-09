# Rev H purchasing files

Use **Factory_BOM + CPL** for top-side SMT assembly. The user buys and fits the terminals, power headers and J8 service header separately.

| File | Purpose |
|---|---|
| [Factory_BOM.csv](Factory_BOM.csv) | 130 SMT placements, 55 exact MPN types |
| [BOM_JLCPCB.csv](BOM_JLCPCB.csv) | Factory matching aid; blank LCSC IDs need exact-MPN matching |
| [Hand_solder_BOM.csv](Hand_solder_BOM.csv) | Six terminals, three 2 mm voltage headers and one 2.54 mm J8 header |
| [ACCESSORIES.csv](ACCESSORIES.csv) | Three loose closed-top 2 mm caps |
| [DigiKey_hand_solder_import.csv](DigiKey_hand_solder_import.csv) | DigiKey subset for one board; J8 is purchased separately from LCSC; scale to the lot |
| [BOM_grouped.csv](BOM_grouped.csv), [BOM_per_reference.csv](BOM_per_reference.csv) | Complete finished-board purchasing and reference lists |
| [catalog_china.json](catalog_china.json) | Exact supplier codes, dated observations, price tiers and URLs |
| [cost_estimate.csv](cost_estimate.csv), [cost_detail.csv](cost_detail.csv) | Minimum-pack/tier purchasing arithmetic for 1, 5, 10 and 25 boards |
| [assembly_scenarios.csv](assembly_scenarios.csv) | Partial fee comparison, not a quotation |

Pair the factory BOM with [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv) and the [Gerber ZIP](../order/README.md). Do not include the ten hand-fitted components in factory SMT placement. [Cost explanation](../docs/COST_REDUCTION.md) includes substitutions and exclusions; [factory instructions](../docs/FACTORY_ORDER.md) define the scope.
