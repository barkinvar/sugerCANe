# Revision history

[Repository overview](README.md)

| Revision | Location | Main changes | Status |
|---|---|---|---|
| A | [Rev A](REV_A.md), root design directories | Four inputs, 96 × 96 mm, 6–18 V target, Würth terminals, 2.54 mm service header | Archived design baseline; unbuilt |
| B, earlier connector iteration | [Historical package](rev_b/history/before_horizontal_connectors/README.md) | Compact three-input design with angled /135 terminals | Superseded; retained for traceability |
| B, current | [rev_b](rev_b/README.md) | 60 × 68 mm, 5–22 V target, horizontal Weidmüller /90 terminals, compact pogo pattern | Current hand-assembly prototype |
| B-2 | [rev_b2](rev_b2/README.md) | Same B circuit/geometry; 49 equivalent passive placements changed and eight unchanged MPNs resourced; factory BOM/CPL packet | Current factory-assembly prototype |

## A to B

PCB area falls by 55.7%, from 9,216 to 4,080 mm², by reducing the input count to three and rearranging the power, input and programming sections. Rev B supplies a buck-plus-boost nominal 5 V sensor rail over its 5–22 V connector-input target. Both revisions supply switched battery voltage as a separate rail.

B uses three 2-pole Weidmüller 1824420000 and three 3-pole 1824430000 terminals. Their /90 wire entry is parallel to the PCB. Two solder pins per pole require the specific 7 mm row spacing; the earlier /135 footprint is not interchangeable. A Phoenix PTSM connector was considered during development but is not in either current B BOM.

The B/B-2 service pads use the TC2050-IDC-NL mechanical contact pattern with a **custom electrical mapping**. Do not use an assumed standard ARM cable pinout. A's 2.54 mm service header also has a project-specific pinout; follow the matching wiring guide.

The ten B/B-2 loose shunts provide three sensor voltage selectors, three input bias selectors, three input threshold selectors and one CAN termination selector. These make sensor configuration visible and avoid adding electronic switching hardware. Their settings and the retained bypass capacitors are explained in the wiring and passive-review guides.

## B to B-2

B-2 changes 37 resistors to same-value UNI-ROYAL 0805 equivalents and twelve 100 nF capacitors to Samsung CL21B104KCFNNNE (100 V, X7R, 0805). Nominal electrical values, PCB pads/tracks, connector MPNs and firmware remain equivalent to B. See the exact [part changes](rev_b2/docs/PART_CHANGES.md) and [variant verification](rev_b2/reports/variant_verification.json).

B-2 keeps 128 SMT and 16 through-hole placements, plus ten loose configuration shunts. A factory must source the MCU and Weidmüller terminals and review placement rotations, panel handling and THT assembly. Estimated consumed component cost is $46.35 versus B's $59.30; this is not an assembled-board quote.

## Documentation and 3D model refresh

The repository overview now covers all three revisions and links their matching CAD, BOM, firmware instructions and releases. All maintained guides identify their revision. Final renders are embedded in the overviews.

The B/B-2 horizontal connector models now use official Weidmüller STEP geometry, with a documented rigid translation to the existing pin origins and project display colors. Earlier simplified boxes are superseded. The PCB routing, holes, BOM connector codes and electrical targets are unchanged by this visual correction. [Connector details](rev_b/docs/CONNECTORS.md).

Git excludes local browser captures, compiler intermediates, downloaded test dependencies, router scratch boards and raw simulation traces. Release ZIPs, native designs, final firmware images, reports and published review images remain tracked. Previously tracked ignored files are removed from the current Git index while retained locally; past commits are not rewritten.

All revisions remain unbuilt and require their documented physical qualification. Historical packages retain their original reports and checksum identities; current packages include the refreshed guides and visuals.
