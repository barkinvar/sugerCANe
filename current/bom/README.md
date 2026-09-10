# Rev H purchasing files

**Start with the [ordering guide](../docs/FACTORY_ORDER.md).** JLC fits 129 SMT parts; you fit STM32F042K6T6 / U5 and ten through-hole parts, then three caps.

| File | Purpose |
|---|---|
| [BOM_JLCPCB.csv](BOM_JLCPCB.csv) | JLC upload: 54 types / 129 placements, U5 excluded |
| [Factory_BOM.csv](Factory_BOM.csv) | Exact manufacturer/MPN cross-check for those 129 placements |
| [assembly_plan.json](assembly_plan.json) | Selected factory/manual split; MCU and stencil omission |
| [Hand_solder_BOM.csv](Hand_solder_BOM.csv) | U5 plus six terminals, three voltage headers and J8 |
| [ACCESSORIES.csv](ACCESSORIES.csv) | Three loose 2 mm caps per board |
| [DigiKey_5_boards.csv](DigiKey_5_boards.csv), [DigiKey_10_boards.csv](DigiKey_10_boards.csv) | Cart imports including two spare MCUs; J8 ordered separately from LCSC |
| [DigiKey_hand_solder_import.csv](DigiKey_hand_solder_import.csv) | Exact one-board DigiKey subset, without spare MCU |
| [BOM_grouped.csv](BOM_grouped.csv), [BOM_per_reference.csv](BOM_per_reference.csv) | Complete finished-board lists, including manual parts |
| [jlc_sourcing.json](jlc_sourcing.json) | Dated supplier evidence; excluded U5 JLC record is historical |
| [catalog_china.json](catalog_china.json) | Supplier codes, observations, tiers and links |
| [cost_estimate.csv](cost_estimate.csv), [cost_detail.csv](cost_detail.csv) | Batch arithmetic before JLC attrition and optional spares |
| [assembly_scenarios.csv](assembly_scenarios.csv) | Partial assembly fee estimates, not quotes |

Pair JLC BOM with [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv) and the matched [Gerber ZIP](../order/README.md). Do not upload the complete finished-board BOM as factory placement instructions. C1, the RGB LED and all SMT parts other than U5 remain factory fitted.

All 54 factory types had sufficient public stock for ten boards in the September 10, 2026, 03:43 UTC check. Stock is not reserved. Final simulations and factory quotation/stack/process/inspection review remain pending.
