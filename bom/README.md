# Revision A purchasing files

All 51 purchase lines have a DigiKey order code. The board uses 161 fitted components; buy 13 configuration shunts separately. Ten test pads and four mounting holes are PCB features.

Indicative one-board parts total: **US$49.61**, calculated conservatively using catalog quantity-one prices for every unit. This excludes PCB fabrication, stencil, shipping, tax, tools and mounting hardware. It is not a live quote. Stock and price observations were collected 2026-09-07; some distributor pages are indexed snapshots and disagree across regions. Reconfirm the exact SKU in a cart before ordering.

A readable version is available at `output/documentation/BOM_RevA.pdf`; programming and mounting accessories are listed separately in `Accessories_DigiKey.csv` and `docs/ACCESSORIES.md`.

Use `DigiKey_import_exact.csv` for exact assembly quantities or `DigiKey_import_with_spares.csv` for extra small parts suitable for hand assembly. `BOM_grouped.csv` contains ratings, source links, availability notes and suggested alternatives. `BOM_per_reference.csv` maps every fitted reference to its part.

The TPS1H100A battery switch was rejected when the current US listing showed no stock; the board uses the stocked TPS1H200A with a different footprint and pin map. Do not fit the older part. The input reverse-polarity element is Q1 AO4485 with a 12 V gate clamp; the earlier series-diode approach was replaced to improve low-battery headroom.

Alternatives in the catalog are review candidates, not an automatic substitution list. Verify package, pinout, voltage, temperature coefficient, leakage, capacitance under DC bias, and firmware behavior as applicable. Keep the 0.1% feedback resistors, C0G timing/filter capacitors, 100V bias diodes, and 2010 pulldown power resistors.

The 13 shunts allow four power selections, four bias selections, four logic-threshold selections and one CAN terminator. Install only the shunts required for your sensors. JP1 is momentary reset and must remain open in normal use.
