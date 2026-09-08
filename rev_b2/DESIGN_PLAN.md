# Rev B-2 factory-assembly design plan and outcome

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

The aim is a lower-cost China-assembled prototype of the 60 x 68 mm horizontal-connector Rev B, preserving its three channels, 5-22 V input target, 5 V / VBAT sensor power, service pads and firmware.

1. Freeze the reviewed Rev B circuit, pad positions and copper. Preserve its separate hand-assembly release.
2. Search manufacturer specifications first, then dated LCSC and DigiKey listings for exact MPN/stock/price/MOQ. Never equate LCSC stock with JLCPCB factory allocation. Use official assembly-house capability and fee documents.
3. Approve only same-value, same-land-pattern substitutions whose voltage, power, tolerance, TCR, dimensions and soldering constraints fit the existing design. Keep protective and timing functions intact. Do not adopt 0402 or another MCU merely because it is smaller or has a lower unit price.
4. Maintain native KiCad files and an explicit circuit model. Regenerate schematic and BOM. Compare model/schematic/PCB MPNs, pin nets and placement data. Record a frozen base signature to prove the change scope.
5. Run native ERC/DRC and independent Gerber connectivity, drill/geometry and electrical checks. Reuse firmware test evidence only after verifying unchanged source and binary hashes.
6. Produce a complete turnkey BOM, factory-centered CPL, pad/polarity coordinates, stencil/rail/THT-process instructions, source observations and delivered-cost model. Include all THT parts and bagged shunts, not just SMT placements.
7. Visually review PCB and PDF exports, check file links and hashes, unpack the delivered archive and verify the native files. Keep physical qualification and factory procurement/rotation/panel review explicit.

Outcome: 37 resistors and 12 capacitors have reviewed same-value replacements; eight unchanged MPNs have cheaper observed sourcing. Consumed first-tier component cost is $46.35 vs $59.30. The board still has 50 fitted part types, so factory setup and sourcing dominate a small order. The result is a prototype quotation/build-data package, not a qualified retail product or a submitted order.

Remaining gates are supplier sourcing/placement/panel approval and physical power, thermal, surge, sensor, CAN and programming tests. No capacitor removal is approved; C13/C24/C42 can be evaluated on hardware in a subsequent revision.
