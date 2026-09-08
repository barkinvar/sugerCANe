# Rev E purchasing files

- [Factory_BOM.csv](Factory_BOM.csv): 111 SMT placements / 46 exact MPNs, top side only.
- [BOM_JLCPCB.csv](BOM_JLCPCB.csv): JLC matching aid; blank part IDs require matching from the exact-MPN factory BOM.
- [Hand_solder_BOM.csv](Hand_solder_BOM.csv): six terminals and three headers, purchased and fitted by the user.
- [ACCESSORIES.csv](ACCESSORIES.csv): three loose closed-top 2 mm caps.
- [DigiKey_hand_solder_import.csv](DigiKey_hand_solder_import.csv): manual parts/caps for ONE board; multiply quantities for your lot.
- [BOM_grouped.csv](BOM_grouped.csv) and [BOM_per_reference.csv](BOM_per_reference.csv): complete finished board.
- [cost_estimate.csv](cost_estimate.csv) / [cost_detail.csv](cost_detail.csv): supplier tier/MOQ arithmetic for 1, 5, 10 and 25 boards; not a PCBA quote.
- [catalog_china.json](catalog_china.json): dated supplier observations and source links; [substitutions.json](substitutions.json): the 27 changed placements.

Pair the factory BOM with [CPL_JLCPCB.csv](../output/assembly/CPL_JLCPCB.csv) and the [Gerber ZIP](../order/RevE_SC12_Gerbers.zip). Factory assembly is top-side SMT only. J1–J6 and JP101/JP201/JP301 are user-fitted; the complete BOM/placement drawings include them for reference.

| Boards | All parts purchase cost per board | Parts purchase cost for the lot |
|---|---:|---:|
| 1 | $55.27 | $55.27 |
| 5 | $40.40 | $202.01 |
| 10 | $34.69 | $346.87 |
| 25 | $32.23 | $805.83 |

Source: [cost_estimate.csv](cost_estimate.csv), from September 7–8, 2026 observations. Includes the connectors, headers, caps and supplier minimums; rounded per-board figures may not multiply exactly to the lot totals. PCB, assembly, attrition, freight and tax are excluded.

The first-tier $44.16 consumed-parts figure does not include buying minimum quantities. The one-board parts purchase model is $55.27. Factory sourcing can differ from distributor purchasing and may add attrition or procurement fees. LCSC stock and part numbers do not establish JLCPCB allocation, Basic/Extended classification or order eligibility. See [cost details](../docs/COST_REDUCTION.md) and [factory scope](../docs/FACTORY_ORDER.md).

[assembly_scenarios.csv](assembly_scenarios.csv) compares partial Economic/Standard fees. Quantity selection now minimizes purchasing cash across price breaks; quantities can exceed the minimum when doing so is cheaper. No delivered quote or stock allocation is implied.
