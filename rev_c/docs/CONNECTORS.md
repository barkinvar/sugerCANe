# Horizontal Weidmüller terminals

| References | Exact MPN | Series description | DigiKey |
|---|---|---|---|
| J1–J3 | **1824420000** | LSF-SMT 3.50/02/90 3.5SN BK TU | 281-2020-ND |
| J4–J6 | **1824430000** | LSF-SMT 3.50/03/90 3.5SN BK TU | 281-2021-ND |

Manufacturer pages: [2-pole](https://eshop.weidmueller.com/p/1824420000), [3-pole](https://eshop.weidmueller.com/p/1824430000). `/90` gives horizontal wire entry parallel to the PCB. `/135` is the angled version and is not used. Phoenix PTSM is not fitted.

These are through-hole/THR parts despite “SMT” in the family name. Pitch is 3.5 mm, with two solder legs per pole and 7 mm row spacing. PCB drills are 1.1 mm. Housing widths are 7.7 mm / 11.2 mm. Manufacturer CAD is 14.3 mm deep; the footprint conservatively reserves 14.75 mm. Height is 8.5 mm above the mounting surface; nominal pin tips reach 3.5 mm below that surface (about 1.9 mm beyond a 1.6 mm PCB).

Current renders use the official STEP solids with a rigid translation (-2.13,-12.625,-3.5) mm into the footprint origin. They are not approximate connector boxes. Display colors are assigned by the project. Original files, transformed files, URLs, hashes, pin/drill checks and nominal bounds are in [vendor_connectors.json](../hardware/library/3d/vendor_connectors.json). Script `import_connector_models.py` checks all six placed pad patterns and the two vendor models. Do not regenerate models merely to change routing: STEP exporters can alter file headers without changing geometry.

Top terminals face outward at the power/CAN edge; three sensor terminals face outward at the opposite edge. Conservative complete footprint envelope is 52 ×64.1 mm; add room for cable bend, strain relief and button access. Renders do not validate conductor retention, tool clearance in an enclosure, molding tolerances or actual solder fit.
