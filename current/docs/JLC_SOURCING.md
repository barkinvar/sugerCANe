# JLCPCB sourcing candidate - approval before simulation

The updated Rev H BOM has **55 of 55 SMT part types matched to JLC codes**, covering 130 top-side placements. Public stock observed September 9, 2026 in California (September 10 UTC) covers **54 types for ten boards**, including a conservative attrition allowance. **U5 remains a sourcing hold:** [STM32F042K6T6 / C69216](https://jlcpcb.com/partdetail/C69216) has no available public stock. No parts have been purchased or reserved.

**Assembly audit: Standard PCBA is required by D10; C1's reflow profile is unresolved.** A matching catalog code does not establish solder-process compatibility. These are additional order holds, independent of the electrical simulations.

Review these substitutions and resolve whether C1 needs a hardware change before the long simulation run. After user approval, rerun the power/input simulations and cross-check the final design. Resolve exact MCU availability and the factory stack/process quotation before issuing the final order package. The user places the order after reviewing the results. Existing simulation reports describe the preceding BOM; they are retained as baseline evidence, not new validation of this candidate. Full coupled startup was already incomplete before this change.

## Implemented substitutions

These six substitutions change only the MPN at nine placements. Values, tolerances, footprints and nets are retained. A subsequent user-requested [branch cleanup](ROUTING_RULES.md) changes routing only; fresh CAD/DC checks and renders accompany it. Rev H firmware, MCU, component positions and four-layer stack remain unchanged.

| References | Original MPN | Replacement MPN / JLC code | Retained specification |
|---|---|---|---|
| C25, C26 | C0805C300J5GACTU | CC0805JRNPO9BN300 / [C107114](https://jlcpcb.com/partdetail/C107114) | 30 pF, 50 V, NP0/C0G, 5%, 0805 |
| R61 | RC0805FR-0711K5L | 0805W8F1152T5E / [C17418](https://jlcpcb.com/partdetail/C17418) | 11.5 kohm, 1%, 0.125 W, 0805 |
| R101, R201, R301 | RC0805FR-07220KL | 0805W8F2203T5E / [C17556](https://jlcpcb.com/partdetail/C17556) | 220 kohm, 1%, 0.125 W, 0805 |
| R10 | RC0805FR-0759KL | 0805W8F5902T5E / [C17763](https://jlcpcb.com/partdetail/C17763) | 59 kohm, 1%, 0.125 W, 0805 |
| R51 | RC0805FR-075K23L | 0805W8F5231T5E / [C17739](https://jlcpcb.com/partdetail/C17739) | 5.23 kohm, 1%, 0.125 W, 0805 |
| R42 | RC1206FR-07120RL | 1206W4F1200T5E / [C17909](https://jlcpcb.com/partdetail/C17909) | 120 ohm, 1%, 0.25 W, 1206 |

The original parts have zero stock or insufficient stock after the allowance. Replacement resistors retain 100 ppm/degree C TCR; the 0805 parts have a 150 V working rating and the 1206 part 200 V. The crystal capacitors remain class-1 dielectric. Manufacturer specifications: [Uniroyal thick-film family](../sources/datasheets/uniroyal_thick_film.pdf), [Yageo NP0 family](../sources/datasheets/yageo_np0.pdf). Download provenance and hashes are in the [dated snapshot](../bom/jlc_sourcing.json).

The remaining previously blank SMT codes now point to the existing exact manufacturer/MPN. The MCU, comparators, power switches, inductors and protection devices are retained. Matching is by manufacturer as well as MPN; listings from a different maker with the same short part name are not substitutes.

## Assembly scope and remaining availability

JLC fits the 130 SMT parts. Keep the ten through-hole parts in [Hand_solder_BOM.csv](../bom/Hand_solder_BOM.csv), plus three loose caps in [ACCESSORIES.csv](../bom/ACCESSORIES.csv). Genuine Weidmuller 1824420000 has no public JLC stock, 1824430000 has no exact public match, and the Harwin voltage headers have only 11 available against 30 needed. The stocked J8 socket remains in the existing manual scope. A low-priced “JLCPCB Assembly” placeholder is not evidence of genuine stocked Weidmuller connectors.

JLC can source the exact MCU through its parts service, subject to availability and a quotation. Preordered parts must arrive at JLC before they can be selected for assembly; a displayed preorder minimum is not a confirmed delivery date. See [JLC parts sourcing](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction) and [preorder terms](https://jlcpcb.com/help/article/pre-ordering-parts-terms-conditions). This is **not yet an entirely in-stock direct checkout**. Avoid changing MCU package or silicon solely to chase today's stock in this final-layout candidate.

Other small stock margins are U9 (25 available), L2 (39), R2 (89) and U7 (110). The [sourcing audit](../reports/manufacturing/jlc_sourcing.json) checks all exact codes, reference sets and ten-board quantities. Recheck live stock when ordering; nothing is allocated by these files.

## Solder-process audit

[D10 / C2890035](https://jlcpcb.com/partdetail/OPSCOOptoelectronics-SK6805EC15/C2890035) is explicitly **Standard Only, MSL 4** in JLC's catalog. Use Standard PCBA and have the factory control moisture exposure and any required baking using the exact OPSCO part instructions. U5 and U7 are listed MSL 3. Unspecified MSL fields for other parts are not proof of unrestricted handling.

**C1 / EEE-FK1H470P is not qualified for JLC's nominal Standard profile.** Panasonic's current [FK table, page 4](../sources/datasheets/panasonic_fk.pdf) assigns this 8 × 6.2 mm part to profile (2). The [soldering specification, page 1](../sources/datasheets/panasonic_reflow.pdf) gives a **235°C peak, 5 seconds at peak, 60 seconds at or above 200°C, one cycle**. JLC publishes **240 ±5°C** for Standard and **255 ±5°C, not adjustable**, for Economic. The catalog nevertheless lists C1 for both services; the manufacturer limit takes precedence. [JLC process capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

Before manufacture, obtain a factory-qualified profile meeting C1's limits and the remaining BOM, or review a high-temperature capacitor replacement and its footprint. No profile has been approved. The stocked Panasonic EEEFT1H470AP / C92059 is a possible review candidate with 47 µF / 50 V and high-temperature reflow support, but its **6.3 × 5.8 mm body requires a different land-pattern review**; it is not an approved substitution. Retain the current BOM until that review is complete. [Manufacturer specifications](https://industrial.panasonic.com/kr/products/pt/aluminum-cap-smd/models/EEEFT1H470AP).

Do not infer a reflow recipe from an LED's solder-heat reliability test. This audit identifies known constraints; it does not claim that every component's complete production profile has been qualified. Simulations cannot resolve factory solder-process limits.

## Cost and files

At ten boards, the revised parts estimate is **$25.61 per board before SMT attrition**, down $3.38 from the prior mixed-supplier estimate. With the conservative displayed-attrition allowance, budget **$26.48 per board**: $17.78 SMT and $8.70 hand-fitted parts/caps. This includes a provisional MCU price despite its shortage. Most savings come from matching existing parts to JLC prices and removing distributor pack minimums; this is not a circuit cost comparison or a final quote.

The observed catalog has 12 basic, one preferred extended and 42 ordinary extended SMT types. **Economic is ineligible for this BOM because of D10**; the previous Economic estimate was not an available ordering option. Posted Standard setup/stencil/loading and two $8.21 fixtures total **$134.34 per order** at ten boards. These fees exclude PCB, placement, X-ray, handling, packing, programming/test, freight and tax. Standard requires rails and a panel meeting its 70 × 70 mm minimum; the delivered board remains 52 × 74 mm. Reflow compatibility and final fees belong to the reviewed quote. [JLC fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price).

Further basic/preferred resistor substitutions at R63, R103/R203/R303, R104/R204/R304 and R109/R209/R309 were considered. Standard charges loading for every part type, so these equal-value swaps do not remove feeder fees and offer only pennies of parts savings. Keep the present resistors, precision sensing network, protection components and top-side assembly. Resolving C1 and MCU procurement is more useful than another passive sourcing change.

Use the clearly labeled [review package](../order/README.md) for file review or quotation. It contains matched BOM/CPL and fabrication files, and does not authorize manufacture. The fabrication requirement remains four layers with nominal 35 um copper on **every** layer; do not silently accept JLC's default 0.5 oz inner copper. Confirm the supplier stack and component orientation preview as described in [factory instructions](FACTORY_ORDER.md).

No arrival date is confirmed. MCU procurement, CAM/assembly timing and destination-specific shipping must be known before relying on delivery within a month.
