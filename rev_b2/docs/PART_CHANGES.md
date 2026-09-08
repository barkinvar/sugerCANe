# Rev B-2 part changes and substitution review

Rev B-2 changes procurement while preserving Rev B's circuit, 60 × 68 mm outline, horizontal connectors, copper routing, pin assignments and firmware. There are still 144 fitted components and ten loose shunts. No protection, filtering or decoupling part has been deleted.

| Rev B part | Rev B-2 fitted part | Count | Review basis |
|---|---|---:|---|
| Yageo RC0805FR-071KL | UNI-ROYAL 0805W8F1001T5E, C17513 | 7 | 1 kΩ, 0805, 1%, 125 mW, ±100 ppm/°C |
| Yageo RC0805FR-0710KL | UNI-ROYAL 0805W8F1002T5E, C17414 | 16 | 10 kΩ, same package/rating/tolerance/TCR |
| Yageo RC0805FR-074K7L | UNI-ROYAL 0805W8F4701T5E, C17673 | 7 | 4.7 kΩ, same package/rating/tolerance/TCR |
| Yageo RC0805FR-07100KL | UNI-ROYAL 0805W8F1003T5E, C149504 | 7 | 100 kΩ, same package/rating/tolerance/TCR |
| Yageo CC0805KRX7R9BB104 | Samsung CL21B104KCFNNNE, C28233 | 12 | 100 nF, X7R, 10%, 0805; voltage rating increases from 50 V to 100 V |

The resistor family is rated 150 V working voltage, with power derating above 70 °C. Original per-reference power and 1.75% total resistance budgets remain applicable to these 1%/100 ppm parts. The Samsung capacitor is 2.00 × 1.25 × 1.25 mm nominal and fits the existing 0805 lands; maximum height remains below the terminal envelope. Its effective capacitance, reflow profile and real circuit transients still need prototype validation. Changing rated voltage alone never establishes a converter's stability.

The original Yageo MPNs remain approved fallback parts if the assembler cannot source these alternatives. A fallback changes cost and must be recorded in the fitted BOM. No resistor value or dielectric may be changed as an informal substitution.

Eight additional MPNs stay electrically and physically identical but use cheaper observed LCSC procurement: TCAN3413DR, LMR51420XDDCR, TPS613222ADBVR, TPS2553DBVR-1, BAT46W-E3-18, CL31A226KAHNNNE, AO4485 and Littelfuse SMAJ30A. Remaining parts retain their exact DigiKey sourcing references. LCSC stock observations are not reservations or JLCPCB assembly-stock confirmations.

Keeping 0805 parts avoids a needless reroute and remains machine-assembly compatible. 0402 parts would not reduce the number of placements or distinct feeder setups. The premium Weidmüller connectors are retained as requested. Their DigiKey first-tier total is $11.25 per board; they are a substantial part of the cost.

There are 34 capacitors. Most are local bypass, regulator reservoir, crystal load, input filter or fault/reset timing components. C13, C24 and C42 are possible **bench evaluation** candidates for later reduction, not approved DNPs. See `PASSIVE_REVIEW.md` for every capacitor's purpose. Larger savings require functional circuit consolidation and hardware testing.

Primary specification sources: [UNI-ROYAL chip resistor family](https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C17513), [Samsung exact capacitor reference sheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/893/CL21B104KCFNNNE_Spec.pdf). Supplier IDs, source URLs, observed quantities, MOQ and prices are recorded in `bom/catalog_china.json` and the turnkey BOM.
