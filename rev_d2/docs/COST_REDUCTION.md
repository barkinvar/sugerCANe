# Rev D-2 cost reduction and sourcing

Pricing basis: USD supplier observations collected 2026-09-07 through 2026-09-08. These are parts budgets, not a factory quote or a reserved basket. Some unchanged-part observations are carried forward from the D/B-2 catalogs. The selected sources and price breaks are recorded in [catalog_china.json](../bom/catalog_china.json).

## Implemented changes

1. Sixteen ordinary 0805 resistors change to same-value UNI-ROYAL 1%, 125 mW equivalents; eleven 100 nF 0805 bypass capacitors change to Samsung CL21B104KCFNNNE, X7R, 10%, 100 V (formerly 50 V). Footprints and electrical values remain unchanged. Precision resistor grades, power ratings, bulk banks, converter bypass capacitance/compensation values and protection are retained. [Per-reference substitutions](../bom/substitutions.json).
2. Unchanged active/power MPNs use lower supplier observations when available: these are procurement changes, not unreviewed circuit substitutions. LCSC candidates include the fuse, reverse-polarity MOSFET, 5 V switch, buck, CAN transceiver and selected capacitors.
3. Factory scope is only 98 SMT placements on the top side. The user fits six terminals plus three voltage headers and supplies three closed-top caps. This avoids factory through-hole labor and connector procurement while retaining the existing connector geometry and quality. It does not eliminate the cost of buying connectors.
4. Three removable 2 mm voltage selectors replace D’s permanent solder settings. No slide switches or bottom-side components are introduced. Four copper layers remain: assembly side count and copper layer count are separate choices.

There are still **46 SMT MPN types**. Substituting cheaper resistors lowers component cost but does not by itself reduce feeder count or establish Basic-part status.

## Batch parts budget

| Boards | Parts purchase cash per board | Parts purchase cash for lot |
|---|---|---|
| 1 | $55.27 | $55.27 |
| 5 | $40.5 | $202.49 |
| 10 | $34.69 | $346.87 |
| 25 | $32.23 | $805.83 |

Includes all SMT parts, six terminal blocks, three headers, three caps, and distributor minimum-order/multiple rounding. At ten boards, SMT purchasing is $26.10 per board and manual parts/caps are $8.59. The calculation uses the price break earned by the actual purchase quantity; [details](../bom/cost_detail.csv) show every line and leftover quantity. No attrition allowance is included because the factory’s requirements are unknown.

D’s $54.89 figure was a quantity-one consumed-parts estimate. D-2’s consumed-parts figure at each supplier’s first saleable tier is $44.16, about 19.5% lower, including the new headers/caps. Buying distributor minimums for just ONE D-2 board instead costs $55.27 in this model. **A single board is not a good cost target with this BOM.** Batch pricing is the larger saving; comparing D’s one-board figure to D-2’s ten-board figure would exaggerate the substitution savings.

PCB fabrication, stencil, setup/feeders, placement, inspection, sourcing fees, attrition, programming, functional testing, freight, duties/taxes and your assembly time are excluded. The exact factory unit price may differ from these public distributor prices.

## Assembly allowance

[JLCPCB’s published assembly fees](https://jlcpcb.com/help/article/pcb-assembly-price), updated 2026-08-20, separate Economic and Standard service. For this one-sided board, Standard’s $25.56 setup, $8.21 stencil and 46 × $1.53 feeder loading total **$104.15 per order** before placement and other charges. Their two-fixture allowance for 1–29 boards is another $16.42. At ten boards these two items alone allocate $12.06 per board.

Placement, leadless-package X-ray, packing and quote-specific adjustments add to that. Hand soldering avoids the published $3.58 order labor charge plus $0.0164 per manual joint (39 finished-board joints per board), if those charges otherwise apply. It is a useful process simplification, not a $10-per-board saving by itself. Confirm the factory’s final scope and fee calculation.

Economic service has lower setup costs but charges extended-part feeder fees and depends on exact inventory/eligibility. Do not budget zero extended fees until every factory part is matched. Request both quotes for the same SMT-only scope. With ten boards, roughly $35 in purchased parts plus about $12 in Standard setup/feeder/fixture allocation already approaches $47 before other assembly charges, bare PCB and freight. A delivered sub-$50 board is therefore **not established** by this revision.

## Remaining major costs

At ten-board quantities the six specified Weidmüller terminals are about $7.85 per board; TPS552872-Q1 is $5.42 and STM32F042K6T6 is $3.28. Together they account for about $16.55 before the inductor, regulators, protection and passives. Large further savings would need a reviewed connector or power/MCU redesign, or a materially better factory quote; passives alone cannot remove those costs.

The public listings used include [Weidmüller 1824420000](https://www.digikey.com/en/products/detail/weidm%C3%BCller/1824420000/1094358), [1824430000](https://www.digikey.com/en/products/detail/weidm%C3%BCller/1824430000/1094359), [TPS552872-Q1](https://www.digikey.com/en/products/detail/texas-instruments/TPS552872QWRYQRQ1/21737567), [STM32F042K6T6](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F042K6T6/4815294), [Samsung bulk capacitor](https://www.lcsc.com/product-detail/C3844168.html), and [selected 100 nF capacitor](https://www.lcsc.com/product-detail/C28233.html). Sources can change without notice.

## China sourcing and one-month delivery

Start with an exact-MPN SMT quote and the [factory package](../order/RevD2_SC12_Factory_Upload.zip). The [JLCPCB MCU listing](https://jlcpcb.com/partdetail/STMicroelectronics-STM32F042K6T6/C69216) identifies a library part, but does not confirm allocation for this order. MCU and converter procurement are potential schedule bottlenecks. LCSC stock is distinct from JLCPCB factory inventory. The observed bulk-cap stock was only 220 pieces against seven fitted per board; larger lots plus attrition need fresh confirmation.

[JLCPCB’s lead-time explanation](https://jlcpcb.com/help/article/smt-service-lead-time-overview) describes assembly time after bare boards are ready and explicitly calls out review and component-preparation dependencies. Fast SMT alone is not the complete delivery time.

**Planning judgment:** delivery within a month is plausible with all parts allocated, prompt review and tracked air express. Allow 2–4 weeks for planning, subject to a destination-specific quote; procurement delays, customs or production holds can push it beyond a month. Order quantity and destination/postcode are still unspecified, so no shipping price or arrival date is claimed. Buy the manual components in parallel. No order, payment or supplier message has been sent.
