# Compact board: standard drilling, inner copper and placement origin

Use the newly matched Gerber ZIP, BOM and CPL from the [order packet](FACTORY_ORDER.md). Re-upload both the Gerber and CPL; do not combine the old placement file with the new order. Component selection is unchanged: 129 factory SMT placements, 54 exact MPN types, with U5 and ten through-hole parts fitted by the customer.

| JLC field | Current selection |
| --- | --- |
| Layers / thickness | 4 / 1.6 mm |
| Finished board | 44 × 48 mm; factory assembly rails may make the panel larger |
| Minimum via hole / land | 0.30 mm / 0.50 mm |
| Via covering | Tented; no plugging or filling |
| Outer copper | 1 oz / 35 µm nominal |
| Inner copper | 0.5 oz / 17.5 µm nominal |
| Stack | Symmetric standard FR-4, outer-to-inner dielectric ≤0.25 mm |
| Finish / assembly | ENIG / Standard PCBA, both sides |

The order now matches the 0.30 mm minimum-drill option and default half-ounce inner copper. Actual savings depend on the updated JLC quotation; no revised final price or factory allocation has been obtained. [JLC fabrication capabilities](https://jlcpcb.com/capabilities/Capabilities?type=1).

## What changed

Exactly **180 via holes changed from 0.20 to 0.30 mm**. Their existing 0.50 mm lands leave a **0.10 mm nominal annulus**; previously it was 0.15 mm. This is a deliberate fabrication-margin tradeoff within the published multilayer capabilities. Larger vias and component-hole lands retain their previous dimensions and annular-ring requirements. The small-via rule is restricted to this reviewed 0.50/0.30 mm combination; copper clearance, drill spacing and trace-width limits are unchanged. Registration, drill tolerances and remaining manufactured annulus are still factory DFM responsibilities.

Both inner copper layers changed from 35 to 17.5 µm nominal. Outer copper stays 35 µm. The nominal central dielectric grows by 0.035 mm to retain a 1.6 mm total stack; the factory may choose its own symmetric standard stack meeting the stated requirements.

**No components moved.** No pad geometry, trace path or width, via center or land diameter, keepout, native copper fill, artwork, schematic, component value or firmware changed. A structural comparison against commit `156d7dd` permits only the specified via-drill and stack-thickness changes. Gerber re-export may alter tiny zone-outline rounding while preserving the native design and passing independent geometry checks. [Exact scope and calculations](../reports/manufacturing/fabrication_options.json).

## Placement-file correction

The earlier CPL added 48 mm to Y to use the board's lower-left origin, while Gerbers and Excellon retained the native absolute origin. The correction removes that CPL-only offset. All three now use **the upper-left board origin, X right and Y up**, so board Y coordinates are negative. Both sides use the same coordinates; bottom X is not mirrored in the CPL.

All 129 factory placements are checked against 322 actual Gerber pad flashes. Regression cases reject the former +48 mm shift, bottom X mirroring, unexpected rotation and a shifted Gerber. Native rotations are retained. JLC library orientation differences still require the placement preview/pin-1 review; this local correction does not establish that JLC's preview has been approved. [JLC CPL format](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly).

If the new preview still shows a uniform shift after JLC adds its panel rails, ask CAM to align the entire board instance and CPL together. Do not manually drag 129 components or apply an unmeasured panel offset. Any isolated rotated part needs a part-specific pin/polarity check.

## Electrical assessment

The DC model now reads each native copper-layer thickness and uses JLC's published **18 µm average via plating**, rather than assuming 35 µm copper everywhere and 20 µm plating. The average plating value is an assumption, not a guaranteed production minimum. Both comparison columns below use the same revised solver and plating assumption.

| Positive-copper path | Previous compact, 1 oz throughout | Updated compact, 0.5 oz inner |
| --- | ---: | ---: |
| Buck to boost, conservative load case | 44.18 mV | 52.15 mV |
| Worst full sensor path at 300 mA | 14.08 mV | 23.18 mV |
| Input feed at 2 A | 112.40 mV | 136.35 mV |

The boost path remains below its **120 mV allowance** and every sensor path below **60 mV**. Input copper is 68.18 mΩ, leaving 207.82 mΩ of the existing 276 mΩ whole-entry planning allowance for the excluded fuse, MOSFET, connectors, wiring and return. The input-copper loss increase at the 2 A screening point is approximately 48 mW. These results support using half-ounce inner copper for this prototype.

This is an 85°C DC resistance screen, **not a thermal or ground-return simulation**. Inner-plane sheet resistance increases and lateral heat spreading decreases. The six local U9 thermal vias and all outer copper remain. Verify loaded temperature, supply ripple and voltage at the sensors on the first assembled board. Existing manufacturer-model transient decks remain unchanged and valid for their stated circuit scope; they do not model every PCB parasitic or the upstream buck. Firmware waveform replay is refreshed using the updated copper-drop evidence.

Native ERC/DRC, all-layer Gerber connectivity/geometry, package checks, placement-origin regression, routing checks and waveform replay remain part of the order review. The packet remains `REVIEW_ONLY` until factory stack/process/inspection review is complete; no assembled board has been physically qualified.

## Short order remarks

Paste [PCB_REMARK.txt](../order/PCB_REMARK.txt) into the PCB field and [ASSEMBLY_REMARK.txt](../order/ASSEMBLY_REMARK.txt) into the assembly field. Both are under 500 characters. Send the full capacitor reflow limits, LED moisture handling and inspection requirements from [FACTORY_ORDER.md](FACTORY_ORDER.md) through order-linked JLC chat as well.
