# Rev B-2 fabrication notes

Use all Gerber and Excellon files in this directory from the same release. Outline: **60 × 68 mm**, two copper layers, nominal **1.6 mm FR-4 and 35 µm / 1 oz copper per side**. All components mount on top. Files are in millimeters.

The project uses 0.20 mm minimum electrical copper clearance and a 0.30 mm copper-to-edge rule. The narrowest signal traces are 0.18 mm. Standard small vias are 0.60 mm copper diameter with 0.30 mm drill; other sizes also occur. Preserve all drill diameters from the Excellon files. Fabrication must support a nominal 0.15 mm annular ring and the reported hole-to-hole web. Review the independent geometry report and the fabrication house's CAM results.

Provide solder mask on both sides and tent ordinary vias where supported. Do not omit solder mask near fine-pitch leads. **ENIG is preferred for the programming contacts**: they need flat, clean exposed contact surfaces. Do not put solder paste or hand-applied solder on J8's ten pogo pads. Its three alignment holes are nonplated, approximately 0.991 mm nominal; the cable drawing specifies ±0.076 mm. The four mounting holes are 3.2 mm nonplated.

Top paste is supplied for surface-mount assembly. A 0.10 mm stencil is the prototype starting point. U3's exposed pad needs proper paste/reflow and inspection; keep its thermal-via and paste geometry intact. Fit the through-hole push-in terminals and headers afterward. Bottom paste is intentionally empty.

The connector and inductor footprints were checked against manufacturer land drawings. The STEP assembly is a placement/envelope aid; its custom mechanical models are not tooling-certified. The supplied reports are computational checks. This board has not been fabricated or physically qualified, and no manufacturing order has been placed.
