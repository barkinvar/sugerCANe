# JLCPCB sourcing and assembly plan

The selected build uses **54 JLC SMT types / 129 top-side placements**. **U5 / STM32F042K6T6 is purchased from DigiKey and hand soldered by the user**, together with the existing ten through-hole parts. The BOM, CPL and factory stencil all omit U5. The native circuit and footprint are unchanged. [Complete ordering guide](FACTORY_ORDER.md).

The September 10, 2026, 03:43 UTC public JLC check found enough orderable stock for all **54 factory types at ten boards**, including displayed attrition/minimums. U9 has 25 available and L2 has 39. No inventory is reserved. Final electrical simulation review, factory stack/process/inspection confirmation and quotation remain pending; the package is REVIEW_ONLY. Older simulation evidence is not a fresh pass for the sourced BOM.

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

Factory: 129 SMT placements, including high-reflow C1, D10, U7–U10 and all passives. User: U5 plus J1–J6, J8 and JP101/JP201/JP301, then three loose caps. [Assembly plan](../bom/assembly_plan.json) is the generator's source for this split. All 140 finished-board parts remain on top.

The exact MCU is DigiKey **497-14647-ND / STM32F042K6T6**, LQFP32. It is absent from JLC BOM/CPL and its 32 stencil apertures are omitted. JLC C69216 remains zero-stock history, not a factory shortage for the selected order. No Global Sourcing, My Parts or overseas MCU consignment is required. The QFN alternative was not implemented.

All six hand-purchased types were checked on their linked supplier pages on September 10 UTC: DigiKey lists the MCU, both Weidmüller terminals, Harwin headers and Sullins caps; LCSC lists the exact XFCN socket. Those listings are not allocations or delivery commitments. [Purchase quantities and links](FACTORY_ORDER.md#1-buy-the-parts-you-will-fit).

## Solder-process audit

[D10 / C2890035](https://jlcpcb.com/partdetail/OPSCOOptoelectronics-SK6805EC15/C2890035) is explicitly **Standard Only, MSL 4** in JLC's catalog. Use Standard PCBA and have the factory control moisture exposure and any required baking using the exact OPSCO part instructions. U7 is listed MSL 3. U5 is purchased separately and hand soldered by the user; follow its delivered moisture-handling label. Unspecified MSL fields for other parts are not proof of unrestricted handling.

**C1 peak-temperature conflict resolved:** EEE-FK1H470P has been replaced by **EEEFT1H470AP / [C92059](https://jlcpcb.com/partdetail/C92059)**. The new part had 1,815 orderable public pieces in the September 9, 7:38 p.m. PDT recheck. Its 6.3 × 5.8 mm can replaces the 8 × 6.2 mm can at the same center and orientation. Manufacturer size-D lands are now 3.2 × 1.6 mm with a 1.8 mm gap; pin 1 remains positive. All traces and vias are unchanged.

Both published part tables specify 47 µF, 50 V, ±20%, 195 mA ripple at 100 kHz/105°C, 0.68 Ω maximum ESR at 100 kHz/20°C, 0.10 dissipation factor and 2,000-hour endurance at 105°C. This retains the input-reservoir electrical basis without assigning a new hand-soldering task. The new can also has more nominal clearance to the board edge. [FT specification and lands](../sources/datasheets/panasonic_ft.pdf) · [previous FK specifications](../sources/datasheets/panasonic_fk.pdf).

Panasonic assigns the new part to **profile (5)**: case-top peak ≤260°C; at/above 250°C ≤5 s, 230°C ≤30 s, 217°C ≤40 s and 200°C ≤70 s; at most two cycles. The published Standard peak is 240 ±5°C, so the earlier peak conflict is removed. The factory must still confirm dwell and moisture handling for the complete BOM; no production profile has been approved by these files. [Panasonic reflow limits](../sources/datasheets/panasonic_reflow.pdf) · [JLC capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

Do not infer a reflow recipe from an LED's solder-heat reliability test. This audit identifies known constraints; it does not claim that every component's complete production profile has been qualified. Simulations cannot resolve factory solder-process limits.

## Cost and files

With the user-fitted DigiKey MCU, ten-board parts are about **$26.45 per board before SMT attrition**, or **$27.33** with conservative JLC allowances. Two recommended spare MCUs add about $6.55 per batch, not per board. PCB, assembly, inspection, freight and taxes are additional. [Cost basis](COST_REDUCTION.md).

Use Standard PCBA. Posted setup/stencil/loading plus two fixtures total **$132.81 per order** for 54 types; this is a partial fee estimate, not a quote. Confirm the panel/rails, 35 µm copper on every layer, reflow limits and U9 X-ray coverage before payment. [Review packet](../order/README.md).

## Complete ten-board factory stock check

“Needed” includes displayed attrition and minimum quantities. “Available” is orderable public stock. The excluded U5 JLC record is retained only as history in the JSON; it is not a factory placement.

| Exact MPN | JLC code | Per board | Needed for 10 | Available | Stock result |
|---|---|---:|---:|---:|---|
| 0451003.MRL | [C13982](https://jlcpcb.com/partdetail/C13982) | 1 | 12 | 45,245 | Enough |
| 0805W8F1001T5E | [C17513](https://jlcpcb.com/partdetail/C17513) | 4 | 50 | 29,783,840 | Enough |
| 0805W8F1002T5E | [C17414](https://jlcpcb.com/partdetail/C17414) | 12 | 130 | 52,921,658 | Enough |
| 0805W8F1003T5E | [C149504](https://jlcpcb.com/partdetail/C149504) | 8 | 90 | 4,752,691 | Enough |
| 0805W8F3300T5E | [C17630](https://jlcpcb.com/partdetail/C17630) | 1 | 20 | 2,314,746 | Enough |
| ABM3B-8.000MHZ-B2-T | [C83312](https://jlcpcb.com/partdetail/C83312) | 1 | 10 | 7,001 | Enough |
| AO3401A | [C15127](https://jlcpcb.com/partdetail/C15127) | 3 | 34 | 305,462 | Enough |
| AO4485 | [C51499](https://jlcpcb.com/partdetail/C51499) | 1 | 10 | 72,826 | Enough |
| AP2112K-3.3TRG1 | [C51118](https://jlcpcb.com/partdetail/C51118) | 1 | 10 | 60,534 | Enough |
| B240A-13-F | [C92506](https://jlcpcb.com/partdetail/C92506) | 2 | 24 | 163,752 | Enough |
| BAT46W-E3-18 | [C5557780](https://jlcpcb.com/partdetail/C5557780) | 3 | 34 | 4,733 | Enough |
| BSS138BK,215 | [C282529](https://jlcpcb.com/partdetail/C282529) | 5 | 54 | 70,842 | Enough |
| CC0805JRNPO9BN300 | [C107114](https://jlcpcb.com/partdetail/C107114) | 2 | 30 | 342,783 | Enough |
| CC0805JRNPO9BN102 | [C62774](https://jlcpcb.com/partdetail/C62774) | 3 | 40 | 1,143,220 | Enough |
| CC0805KRX7R9BB333 | [C107150](https://jlcpcb.com/partdetail/C107150) | 1 | 20 | 1,800,061 | Enough |
| CL21B103KBANNNC | [C1710](https://jlcpcb.com/partdetail/C1710) | 2 | 30 | 2,671,459 | Enough |
| CL21B104KCFNNNE | [C28233](https://jlcpcb.com/partdetail/C28233) | 14 | 150 | 1,390,137 | Enough |
| CL21B105KBFNNNE | [C28323](https://jlcpcb.com/partdetail/C28323) | 5 | 60 | 3,094,211 | Enough |
| CL21B473KBCNNNC | [C53134](https://jlcpcb.com/partdetail/C53134) | 1 | 20 | 218,593 | Enough |
| CL21B475KAFNNNE | [C98195](https://jlcpcb.com/partdetail/C98195) | 2 | 28 | 197,867 | Enough |
| CL31A226KAHNNNE | [C12891](https://jlcpcb.com/partdetail/C12891) | 8 | 84 | 756,677 | Enough |
| CL32B106KBJNNWE | [C3844168](https://jlcpcb.com/partdetail/C3844168) | 1 | 10 | 626 | Enough |
| EEEFT1H470AP | [C92059](https://jlcpcb.com/partdetail/C92059) | 1 | 10 | 1,695 | Enough |
| ESD2CAN24DBZRQ1 | [C5736151](https://jlcpcb.com/partdetail/C5736151) | 1 | 10 | 2,427 | Enough |
| LM339LVDR | [C22427665](https://jlcpcb.com/partdetail/C22427665) | 1 | 10 | 110 | Enough |
| LMR51420XDDCR | [C5246146](https://jlcpcb.com/partdetail/C5246146) | 1 | 10 | 4,040 | Enough |
| MMSZ12T1G | [C72599](https://jlcpcb.com/partdetail/C72599) | 1 | 14 | 6,517 | Enough |
| 0805W8F1152T5E | [C17418](https://jlcpcb.com/partdetail/C17418) | 1 | 20 | 3,238 | Enough |
| RC0805FR-0713KL | [C137592](https://jlcpcb.com/partdetail/C137592) | 1 | 20 | 13,578 | Enough |
| RC0805FR-0720KL | [C114566](https://jlcpcb.com/partdetail/C114566) | 3 | 40 | 1,914,116 | Enough |
| 0805W8F2203T5E | [C17556](https://jlcpcb.com/partdetail/C17556) | 3 | 40 | 289,433 | Enough |
| RC0805FR-072K61L | [C273965](https://jlcpcb.com/partdetail/C273965) | 1 | 20 | 2,680 | Enough |
| RC0805FR-072M2L | [C137552](https://jlcpcb.com/partdetail/C137552) | 3 | 40 | 6,844 | Enough |
| 0805W8F5902T5E | [C17763](https://jlcpcb.com/partdetail/C17763) | 1 | 20 | 6,289 | Enough |
| 0805W8F5231T5E | [C17739](https://jlcpcb.com/partdetail/C17739) | 1 | 20 | 2,225 | Enough |
| RC0805JR-070RL | [C96345](https://jlcpcb.com/partdetail/C96345) | 1 | 20 | 2,040,155 | Enough |
| RC1206FR-0710KL | [C132649](https://jlcpcb.com/partdetail/C132649) | 3 | 40 | 1,937,202 | Enough |
| 1206W4F1200T5E | [C17909](https://jlcpcb.com/partdetail/C17909) | 1 | 20 | 709,711 | Enough |
| RT0805BRD07100KL | [C122537](https://jlcpcb.com/partdetail/C122537) | 6 | 68 | 533,527 | Enough |
| RT0805BRD07102KL | [C865126](https://jlcpcb.com/partdetail/C865126) | 1 | 14 | 9,215 | Enough |
| RT0805BRD0712K1L | [C865169](https://jlcpcb.com/partdetail/C865169) | 1 | 14 | 6,666 | Enough |
| RT0805BRD0713K7L | [C865183](https://jlcpcb.com/partdetail/C865183) | 1 | 14 | 89 | Enough |
| RT0805BRD0720KL | [C469660](https://jlcpcb.com/partdetail/C469660) | 2 | 24 | 26,820 | Enough |
| SK6805-EC15 | [C2890035](https://jlcpcb.com/partdetail/C2890035) | 1 | 12 | 233,479 | Enough |
| SMAJ13A-13-F | [C110519](https://jlcpcb.com/partdetail/C110519) | 1 | 12 | 12,888 | Enough |
| SMAJ30A | [C148230](https://jlcpcb.com/partdetail/C148230) | 3 | 32 | 29,233 | Enough |
| SMBJ22A-E3/52 | [C3698580](https://jlcpcb.com/partdetail/C3698580) | 1 | 12 | 177 | Enough |
| SN74AHCT1G125DBVR | [C7484](https://jlcpcb.com/partdetail/C7484) | 1 | 12 | 16,214 | Enough |
| SRP5030TA-3R3M | [C2042118](https://jlcpcb.com/partdetail/C2042118) | 1 | 10 | 39 | Enough |
| SRP7028A-100M | [C2687402](https://jlcpcb.com/partdetail/C2687402) | 1 | 10 | 5,146 | Enough |
| TCAN3413DR | [C22433320](https://jlcpcb.com/partdetail/C22433320) | 1 | 10 | 2,422 | Enough |
| TPS2553DBVR-1 | [C111738](https://jlcpcb.com/partdetail/C111738) | 1 | 10 | 13,065 | Enough |
| TPS259620DDAR | [C2155773](https://jlcpcb.com/partdetail/C2155773) | 1 | 10 | 25 | Enough |
| TPS61085DGKR | [C113659](https://jlcpcb.com/partdetail/C113659) | 1 | 10 | 2,041 | Enough |

## Exact MCU procurement

Buy [STM32F042K6T6 / 497-14647-ND from DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F042K6T6/4815294) for shipment to yourself. Observed September 10 UTC: 3,071 in stock, $3.277 each at 10+. Buy one per board plus two optional spares. The unchanged LQFP32 footprint is not compatible with STM32F042K6U6TR / UFQFPN32. See [hand installation and initial programming](FACTORY_ORDER.md#6-finish-the-delivered-boards).
