# Rev H purchasing files

Use **Factory_BOM + CPL** for top-side SMT assembly. The user buys and fits the terminals, power headers and J8 service header separately.

| File | Purpose |
|---|---|
| [Factory_BOM.csv](Factory_BOM.csv) | 130 SMT placements, 55 exact MPN types |
| [BOM_JLCPCB.csv](BOM_JLCPCB.csv) | All 55 SMT types have exact JLC codes; MCU stock remains unresolved |
| [jlc_sourcing.json](jlc_sourcing.json) | Dated public JLC stock, price tiers, substitution and datasheet evidence |
| [Hand_solder_BOM.csv](Hand_solder_BOM.csv) | Six terminals, three 2 mm voltage headers and one 2.54 mm J8 header |
| [ACCESSORIES.csv](ACCESSORIES.csv) | Three loose closed-top 2 mm caps |
| [DigiKey_hand_solder_import.csv](DigiKey_hand_solder_import.csv) | DigiKey subset for one board; J8 is purchased separately from LCSC; scale to the lot |
| [BOM_grouped.csv](BOM_grouped.csv), [BOM_per_reference.csv](BOM_per_reference.csv) | Complete finished-board purchasing and reference lists |
| [catalog_china.json](catalog_china.json) | Exact supplier codes, dated observations, price tiers and URLs |
| [cost_estimate.csv](cost_estimate.csv), [cost_detail.csv](cost_detail.csv) | Minimum-pack/tier purchasing arithmetic for 1, 5, 10 and 25 boards |
| [assembly_scenarios.csv](assembly_scenarios.csv) | Partial fee comparison, not a quotation |

Pair the factory BOM with [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv) and the [Gerber ZIP](../order/README.md). Do not include the ten hand-fitted components in factory SMT placement. [Cost explanation](../docs/COST_REDUCTION.md) includes substitutions and exclusions; [factory instructions](../docs/FACTORY_ORDER.md) define the scope.

This is a [JLC sourcing candidate](../docs/JLC_SOURCING.md), pending user approval and new simulations. The September 9, 2026 live recheck covers every factory type: 54 of 55 have enough orderable stock for ten boards; U5 needs exact-part sourcing. No inventory is reserved or delivery promised.

C1 / EEEFT1H470AP remains in factory SMT assembly. All fine-pitch parts, passives and the RGB LED must arrive already soldered. U5 / STM32F042K6T6 stays in the BOM/CPL for factory assembly using JLC Global Sourcing / My Parts; do not omit it from the order or plan to hand solder it. Follow the [procurement steps](../docs/FACTORY_ORDER.md#ordering-sequence).
