# Rev D-2 purchasing files

- [Factory_BOM.csv](Factory_BOM.csv): 98 SMT placements / 46 exact MPNs, top side only.
- [BOM_JLCPCB.csv](BOM_JLCPCB.csv): JLC matching aid; blank part IDs require matching from the exact-MPN factory BOM.
- [Hand_solder_BOM.csv](Hand_solder_BOM.csv): six terminals and three headers, purchased and fitted by the user.
- [ACCESSORIES.csv](ACCESSORIES.csv): three loose closed-top 2 mm caps.
- [DigiKey_hand_solder_import.csv](DigiKey_hand_solder_import.csv): manual parts/caps for ONE board; multiply quantities for your lot.
- [BOM_grouped.csv](BOM_grouped.csv) and [BOM_per_reference.csv](BOM_per_reference.csv): complete finished board.
- [cost_estimate.csv](cost_estimate.csv) / [cost_detail.csv](cost_detail.csv): supplier tier/MOQ arithmetic for 1, 5, 10 and 25 boards; not a PCBA quote.
- [catalog_china.json](catalog_china.json): dated supplier observations and source links; [substitutions.json](substitutions.json): the 27 changed placements.

The first-tier $44.16 consumed-parts figure does not include buying minimum quantities. The one-board parts purchase model is $55.27. Factory sourcing can differ from distributor purchasing and may add attrition or procurement fees. LCSC stock and part numbers do not establish JLCPCB allocation, Basic/Extended classification or order eligibility. See [cost details](../docs/COST_REDUCTION.md) and [factory scope](../docs/FACTORY_ORDER.md).
