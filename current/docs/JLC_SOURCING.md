# JLCPCB sourcing and assembly plan

The updated Rev H BOM has **55 of 55 SMT part types matched to JLC codes**, covering 130 top-side placements. The previous complete 55-type check was through JLC's public catalog on **September 9, 2026, 7:23–7:24 p.m. PDT (September 10, 02:23–02:24 UTC)**. Orderable stock covers **54 types for ten boards**, including a conservative attrition allowance. **U5 remains a sourcing hold:** [STM32F042K6T6 / C69216](https://jlcpcb.com/partdetail/STMicroelectronics-STM32F042K6T6/C69216) has **zero orderable pieces**. Its total-stock field says two; those are not available to this order. No parts have been purchased or reserved.

**All tiny parts stay factory fitted.** Use Standard PCBA for all 130 SMT placements, including U5, D10 and C1. The user only fits ten through-hole parts and three loose shunts. C1 now uses EEEFT1H470AP / C92059 with manufacturer size-D lands. This resolves the known Standard peak-temperature conflict; the factory must meet the documented dwell limits.

The C1 replacement is implemented and CAD checked. Review the final BOM before the long simulation run. After user approval, rerun the power/input simulations and cross-check the final design. Resolve exact MCU availability and the factory stack/process quotation before issuing the final order package. The user places the order after reviewing the results. Existing simulation reports describe the preceding BOM; they are retained as baseline evidence, not new validation of this candidate. Full coupled startup was already incomplete before this change.

## Implemented substitutions

The following six earlier substitutions change only the MPN at nine placements; their values, tolerances, footprints and nets are retained. The separate C1 update below also changes its footprint. A subsequent user-requested [branch cleanup](ROUTING_RULES.md) changes routing only; fresh CAD/DC checks and renders accompany it. Rev H firmware, MCU, component positions and four-layer stack remain unchanged.

| References | Original MPN | Replacement MPN / JLC code | Retained specification |
|---|---|---|---|
| C25, C26 | C0805C300J5GACTU | CC0805JRNPO9BN300 / [C107114](https://jlcpcb.com/partdetail/C107114) | 30 pF, 50 V, NP0/C0G, 5%, 0805 |
| R61 | RC0805FR-0711K5L | 0805W8F1152T5E / [C17418](https://jlcpcb.com/partdetail/C17418) | 11.5 kohm, 1%, 0.125 W, 0805 |
| R101, R201, R301 | RC0805FR-07220KL | 0805W8F2203T5E / [C17556](https://jlcpcb.com/partdetail/C17556) | 220 kohm, 1%, 0.125 W, 0805 |
| R10 | RC0805FR-0759KL | 0805W8F5902T5E / [C17763](https://jlcpcb.com/partdetail/C17763) | 59 kohm, 1%, 0.125 W, 0805 |
| R51 | RC0805FR-075K23L | 0805W8F5231T5E / [C17739](https://jlcpcb.com/partdetail/C17739) | 5.23 kohm, 1%, 0.125 W, 0805 |
| R42 | RC1206FR-07120RL | 1206W4F1200T5E / [C17909](https://jlcpcb.com/partdetail/C17909) | 120 ohm, 1%, 0.25 W, 1206 |

These substitutions addressed earlier sourcing constraints. The fresh review compares original and replacement manufacturer specifications and the actual nine footprints in the native PCB. The five resistor types retain 1% tolerance, 100 ppm/degree C TCR, rated power and -55 to +155°C operation. Both families derate above 70°C; working voltage is limited by both power dissipation and the 150 V (0805) / 200 V (1206) ceiling. Their specified five-second overload test uses the same voltage limits; this does not qualify repetitive robot transients. Sources: [original Yageo RC family](../sources/datasheets/yageo_rc_original.pdf), [replacement Uniroyal family](../sources/datasheets/uniroyal_thick_film.pdf).

C25/C26 retain 30 pF, 5%, 50 V, C0G/NP0, ±30 ppm/°C and -55 to +125°C. Both specify at most 0.1% dissipation factor at this capacitance. The specified insulation resistance changes from KEMET's 100 Gohm to Yageo's 10 Gohm minimum; that leakage is negligible against the roughly 663-ohm capacitive reactance at 8 MHz. Body thickness also differs. These are suitable replacements for this crystal-load application, with compatible existing pads; they are not identical in every manufacturer parameter. Oscillator startup remains a board-level qualification item. Sources: [original KEMET part](../sources/datasheets/kemet_original.pdf), [replacement Yageo NP0 family](../sources/datasheets/yageo_np0.pdf).

All nine replacements are nonpolar two-terminal parts, so there is no active-device pinout conversion. Actual PCB pads are 1.025 × 1.4 mm for 0805 resistors, 1.125 × 1.75 mm for R42 and 1 × 1.45 mm for the two capacitors. The sourcing checker now verifies these reviewed dimensions and pad positions. Download provenance, hashes and the per-substitution review are in the [dated snapshot](../bom/jlc_sourcing.json).

The remaining previously blank SMT codes now point to the existing exact manufacturer/MPN. The MCU, comparators, power switches, inductors and protection devices are retained; C1 is the separately reviewed exception among the capacitors. Matching is by manufacturer as well as MPN; listings from a different maker with the same short part name are not substitutes.

## Assembly scope and remaining availability

JLC fits the 130 SMT parts. Keep the ten through-hole parts in [Hand_solder_BOM.csv](../bom/Hand_solder_BOM.csv), plus three loose caps in [ACCESSORIES.csv](../bom/ACCESSORIES.csv). Genuine Weidmuller 1824420000 has no public JLC stock, 1824430000 has no exact public match, and the Harwin voltage headers have only 11 available against 30 needed. The stocked J8 socket remains in the existing manual scope. These are the only parts the user needs to solder; ICs, small passives, the RGB LED and C1 must arrive factory assembled. A low-priced “JLCPCB Assembly” placeholder is not evidence of genuine stocked Weidmuller connectors.

The MCU alternatives were also checked: **STM32F042K6T6TR / C529323 has zero orderable stock**, and **STM32F042K6T7 / C1337340 has zero orderable stock** despite six in its total-stock field. ST's ordering table confirms that `TR` changes packing to tape-and-reel, while `T7` retains LQFP32 and extends the temperature grade to +105°C. Neither resolves this order's shortage. No MCU substitution was made. [ST datasheet, ordering table on page 113](https://www.st.com/resource/en/datasheet/stm32f042k6.pdf#page=113).

JLC offers exact-part procurement, subject to availability and a quotation. Preordered parts must arrive at JLC before assembly selection; a displayed preorder minimum is not a delivery date. JLC’s overview lists **9–15 days**, while its detailed Global Sourcing guide says **9–20 business days plus review**. These are differing service estimates, not an allocated MCU delivery date. Use the exact quote before relying on a deadline. See [JLC parts sourcing](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction) and [preorder terms](https://jlcpcb.com/help/article/pre-ordering-parts-terms-conditions). This is **not yet an entirely in-stock direct checkout**. Request exact MCU allocation and arrival timing before relying on a tight delivery deadline.

Other small stock margins are U9 (25 available), L2 (39), R2 (89) and U7 (110). The [sourcing audit](../reports/manufacturing/jlc_sourcing.json) checks all exact codes, reference sets and ten-board quantities. Recheck live stock when ordering; nothing is allocated by these files.

The separate manual-parts check found J8 / C492399 available (36,672), but the specified loose shunt SPN02SVEN-RC / C6495598 has zero JLC stock. Keep the existing separate manual purchase; the older distributor observations in its BOM do not establish current availability or delivery. No substitute terminal blocks, headers or shunts were approved by this audit.

## Solder-process audit

[D10 / C2890035](https://jlcpcb.com/partdetail/OPSCOOptoelectronics-SK6805EC15/C2890035) is explicitly **Standard Only, MSL 4** in JLC's catalog. Use Standard PCBA and have the factory control moisture exposure and any required baking using the exact OPSCO part instructions. U5 and U7 are listed MSL 3. Unspecified MSL fields for other parts are not proof of unrestricted handling.

**C1 peak-temperature conflict resolved:** EEE-FK1H470P has been replaced by **EEEFT1H470AP / [C92059](https://jlcpcb.com/partdetail/C92059)**. The new part had 1,815 orderable public pieces in the September 9, 7:38 p.m. PDT recheck. Its 6.3 × 5.8 mm can replaces the 8 × 6.2 mm can at the same center and orientation. Manufacturer size-D lands are now 3.2 × 1.6 mm with a 1.8 mm gap; pin 1 remains positive. All traces and vias are unchanged.

Both published part tables specify 47 µF, 50 V, ±20%, 195 mA ripple at 100 kHz/105°C, 0.68 Ω maximum ESR at 100 kHz/20°C, 0.10 dissipation factor and 2,000-hour endurance at 105°C. This retains the input-reservoir electrical basis without assigning a new hand-soldering task. The new can also has more nominal clearance to the board edge. [FT specification and lands](../sources/datasheets/panasonic_ft.pdf) · [previous FK specifications](../sources/datasheets/panasonic_fk.pdf).

Panasonic assigns the new part to **profile (5)**: case-top peak ≤260°C; at/above 250°C ≤5 s, 230°C ≤30 s, 217°C ≤40 s and 200°C ≤70 s; at most two cycles. The published Standard peak is 240 ±5°C, so the earlier peak conflict is removed. The factory must still confirm dwell and moisture handling for the complete BOM; no production profile has been approved by these files. [Panasonic reflow limits](../sources/datasheets/panasonic_reflow.pdf) · [JLC capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

Do not infer a reflow recipe from an LED's solder-heat reliability test. This audit identifies known constraints; it does not claim that every component's complete production profile has been qualified. Simulations cannot resolve factory solder-process limits.

## Cost and files

At ten boards, the revised parts estimate is **$25.68 per board before SMT attrition**, down $3.31 from the prior mixed-supplier estimate. With the conservative displayed-attrition allowance, budget **$26.55 per board**: $17.85 SMT and $8.70 hand-fitted parts/caps. This includes a provisional MCU price despite its shortage. Most savings come from matching existing parts to JLC prices and removing distributor pack minimums; this is not a circuit cost comparison or a final quote.

The observed catalog has 12 basic, one preferred extended and 42 ordinary extended SMT types. **Economic is ineligible for this BOM because of D10**; the previous Economic estimate was not an available ordering option. Posted Standard setup/stencil/loading and two $8.21 fixtures total **$134.34 per order** at ten boards. These fees exclude PCB, placement, X-ray, handling, packing, programming/test, freight and tax. Standard requires rails and a panel meeting its 70 × 70 mm minimum; the delivered board remains 52 × 74 mm. Reflow compatibility and final fees belong to the reviewed quote. [JLC fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price).

Further basic/preferred resistor substitutions at R63, R103/R203/R303, R104/R204/R304 and R109/R209/R309 were considered. Standard charges loading for every part type, so these equal-value swaps do not remove feeder fees and offer only pennies of parts savings. Keep the present resistors, precision sensing network, protection components and top-side assembly. The C1 issue has been addressed; MCU allocation and the factory quote are the remaining purchasing work.

Use the clearly labeled [review package](../order/README.md) for file review or quotation. It contains matched BOM/CPL and fabrication files, and does not authorize manufacture. The fabrication requirement remains four layers with nominal 35 um copper on **every** layer; do not silently accept JLC's default 0.5 oz inner copper. Confirm the supplier stack and component orientation preview as described in [factory instructions](FACTORY_ORDER.md).

No arrival date is confirmed. MCU procurement, CAM/assembly timing and destination-specific shipping must be known before relying on delivery within a month.

## Complete ten-board stock check

“Needed” includes the displayed attrition and minimum quantities. “Available” means orderable public stock, not total inventory. Availability is a dated observation, not a reservation. C1 is the later 7:38 p.m. PDT replacement check; other rows retain the earlier full audit, with U5 reconfirmed unavailable.

| Exact MPN | JLC code | Per board | Needed for 10 | Available | Stock result |
|---|---|---:|---:|---:|---|
| 0451003.MRL | [C13982](https://jlcpcb.com/partdetail/C13982) | 1 | 12 | 45,245 | Enough |
| 0805W8F1001T5E | [C17513](https://jlcpcb.com/partdetail/C17513) | 4 | 50 | 29,797,798 | Enough |
| 0805W8F1002T5E | [C17414](https://jlcpcb.com/partdetail/C17414) | 12 | 130 | 52,936,609 | Enough |
| 0805W8F1003T5E | [C149504](https://jlcpcb.com/partdetail/C149504) | 8 | 90 | 4,758,023 | Enough |
| 0805W8F3300T5E | [C17630](https://jlcpcb.com/partdetail/C17630) | 1 | 20 | 2,318,391 | Enough |
| ABM3B-8.000MHZ-B2-T | [C83312](https://jlcpcb.com/partdetail/C83312) | 1 | 10 | 7,026 | Enough |
| AO3401A | [C15127](https://jlcpcb.com/partdetail/C15127) | 3 | 34 | 311,819 | Enough |
| AO4485 | [C51499](https://jlcpcb.com/partdetail/C51499) | 1 | 10 | 72,841 | Enough |
| AP2112K-3.3TRG1 | [C51118](https://jlcpcb.com/partdetail/C51118) | 1 | 10 | 60,541 | Enough |
| B240A-13-F | [C92506](https://jlcpcb.com/partdetail/C92506) | 2 | 24 | 164,252 | Enough |
| BAT46W-E3-18 | [C5557780](https://jlcpcb.com/partdetail/C5557780) | 3 | 34 | 4,733 | Enough |
| BSS138BK,215 | [C282529](https://jlcpcb.com/partdetail/C282529) | 5 | 54 | 70,842 | Enough |
| CC0805JRNPO9BN300 | [C107114](https://jlcpcb.com/partdetail/C107114) | 2 | 30 | 342,783 | Enough |
| CC0805JRNPO9BN102 | [C62774](https://jlcpcb.com/partdetail/C62774) | 3 | 40 | 1,143,347 | Enough |
| CC0805KRX7R9BB333 | [C107150](https://jlcpcb.com/partdetail/C107150) | 1 | 20 | 1,800,261 | Enough |
| CL21B103KBANNNC | [C1710](https://jlcpcb.com/partdetail/C1710) | 2 | 30 | 2,678,768 | Enough |
| CL21B104KCFNNNE | [C28233](https://jlcpcb.com/partdetail/C28233) | 14 | 150 | 1,391,143 | Enough |
| CL21B105KBFNNNE | [C28323](https://jlcpcb.com/partdetail/C28323) | 5 | 60 | 3,097,023 | Enough |
| CL21B473KBCNNNC | [C53134](https://jlcpcb.com/partdetail/C53134) | 1 | 20 | 218,653 | Enough |
| CL21B475KAFNNNE | [C98195](https://jlcpcb.com/partdetail/C98195) | 2 | 28 | 225,867 | Enough |
| CL31A226KAHNNNE | [C12891](https://jlcpcb.com/partdetail/C12891) | 8 | 84 | 783,341 | Enough |
| CL32B106KBJNNWE | [C3844168](https://jlcpcb.com/partdetail/C3844168) | 1 | 10 | 626 | Enough |
| EEEFT1H470AP | [C92059](https://jlcpcb.com/partdetail/C92059) | 1 | 10 | 1,815 | Enough |
| ESD2CAN24DBZRQ1 | [C5736151](https://jlcpcb.com/partdetail/C5736151) | 1 | 10 | 2,427 | Enough |
| LM339LVDR | [C22427665](https://jlcpcb.com/partdetail/C22427665) | 1 | 10 | 110 | Enough |
| LMR51420XDDCR | [C5246146](https://jlcpcb.com/partdetail/C5246146) | 1 | 10 | 4,040 | Enough |
| MMSZ12T1G | [C72599](https://jlcpcb.com/partdetail/C72599) | 1 | 14 | 6,517 | Enough |
| 0805W8F1152T5E | [C17418](https://jlcpcb.com/partdetail/C17418) | 1 | 20 | 3,238 | Enough |
| RC0805FR-0713KL | [C137592](https://jlcpcb.com/partdetail/C137592) | 1 | 20 | 13,578 | Enough |
| RC0805FR-0720KL | [C114566](https://jlcpcb.com/partdetail/C114566) | 3 | 40 | 1,915,416 | Enough |
| 0805W8F2203T5E | [C17556](https://jlcpcb.com/partdetail/C17556) | 3 | 40 | 289,620 | Enough |
| RC0805FR-072K61L | [C273965](https://jlcpcb.com/partdetail/C273965) | 1 | 20 | 2,680 | Enough |
| RC0805FR-072M2L | [C137552](https://jlcpcb.com/partdetail/C137552) | 3 | 40 | 6,944 | Enough |
| 0805W8F5902T5E | [C17763](https://jlcpcb.com/partdetail/C17763) | 1 | 20 | 6,289 | Enough |
| 0805W8F5231T5E | [C17739](https://jlcpcb.com/partdetail/C17739) | 1 | 20 | 2,225 | Enough |
| RC0805JR-070RL | [C96345](https://jlcpcb.com/partdetail/C96345) | 1 | 20 | 2,040,265 | Enough |
| RC1206FR-0710KL | [C132649](https://jlcpcb.com/partdetail/C132649) | 3 | 40 | 1,937,212 | Enough |
| 1206W4F1200T5E | [C17909](https://jlcpcb.com/partdetail/C17909) | 1 | 20 | 710,078 | Enough |
| RT0805BRD07100KL | [C122537](https://jlcpcb.com/partdetail/C122537) | 6 | 68 | 533,568 | Enough |
| RT0805BRD07102KL | [C865126](https://jlcpcb.com/partdetail/C865126) | 1 | 14 | 9,215 | Enough |
| RT0805BRD0712K1L | [C865169](https://jlcpcb.com/partdetail/C865169) | 1 | 14 | 6,666 | Enough |
| RT0805BRD0713K7L | [C865183](https://jlcpcb.com/partdetail/C865183) | 1 | 14 | 89 | Enough |
| RT0805BRD0720KL | [C469660](https://jlcpcb.com/partdetail/C469660) | 2 | 24 | 26,836 | Enough |
| SK6805-EC15 | [C2890035](https://jlcpcb.com/partdetail/C2890035) | 1 | 12 | 233,479 | Enough |
| SMAJ13A-13-F | [C110519](https://jlcpcb.com/partdetail/C110519) | 1 | 12 | 12,888 | Enough |
| SMAJ30A | [C148230](https://jlcpcb.com/partdetail/C148230) | 3 | 32 | 29,435 | Enough |
| SMBJ22A-E3/52 | [C3698580](https://jlcpcb.com/partdetail/C3698580) | 1 | 12 | 177 | Enough |
| SN74AHCT1G125DBVR | [C7484](https://jlcpcb.com/partdetail/C7484) | 1 | 12 | 16,260 | Enough |
| SRP5030TA-3R3M | [C2042118](https://jlcpcb.com/partdetail/C2042118) | 1 | 10 | 39 | Enough |
| SRP7028A-100M | [C2687402](https://jlcpcb.com/partdetail/C2687402) | 1 | 10 | 5,146 | Enough |
| STM32F042K6T6 | [C69216](https://jlcpcb.com/partdetail/C69216) | 1 | 10 | 0 | **HOLD** |
| TCAN3413DR | [C22433320](https://jlcpcb.com/partdetail/C22433320) | 1 | 10 | 2,422 | Enough |
| TPS2553DBVR-1 | [C111738](https://jlcpcb.com/partdetail/C111738) | 1 | 10 | 13,075 | Enough |
| TPS259620DDAR | [C2155773](https://jlcpcb.com/partdetail/C2155773) | 1 | 10 | 25 | Enough |
| TPS61085DGKR | [C113659](https://jlcpcb.com/partdetail/C113659) | 1 | 10 | 2,041 | Enough |

## Exact MCU procurement

Keep U5 as **STM32F042K6T6 / C69216**, factory fitted. The public JLC recheck still shows zero available pieces. [DigiKey 497-14647-ND](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F042K6T6/4815294) shows 3,071 pieces and $3.277 each at ten, providing an exact-part procurement candidate. This is supplier stock, not allocated JLC stock or an accepted JLC quote.

Use **Parts Manager → Order Parts → Global Sourcing Parts** in the user’s JLC account. Search the exact MPN, choose the quoted supplier and sufficient quantity (ten fitted MCUs plus JLC’s final attrition requirement), and confirm the arrival date and total procurement charge before paying. After arrival, select U5 from **My Parts** during BOM matching. U5 remains present in the supplied BOM and CPL. [Global Sourcing instructions](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service) · [using My Parts](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order).

No JLC login, paid procurement, allocation or factory quotation has been completed here. Overseas self-consignment adds handling and shipping work, so Global Sourcing is the preferred route for this batch. Do not accept a missing MCU or a different microcontroller as a shortcut.
