# sugarCANe underside artwork

[sugarCANe.svg](sugarCANe.svg) is the original vector master, 52 × 74 mm, viewed from the underside. White artwork spans approximately 45.6 × 43.2 mm between the connector fields. Three jointed pixel stalks and stair-step leaves stand on a floating island with a raised, convex top and a stepped, tapering underside. The large **sugarCANe** name uses bold pixel lettering. There are no corner decorations, borders or additional text on the underside.

The lettering is drawn specifically for this wordmark in [build_brand_artwork.py](../../scripts/build_brand_artwork.py), without an external font. Most stems are two cells thick; the lowercase bodies are seven rows high and CAN is nine rows high. The g has a descending tail, and the final lowercase e has a clear crossbar and an open right side. A 0.616 mm letter grid and 0.924 mm inter-letter spacing keep the shapes separated at PCB scale. No Minecraft texture, logo or font is included. SC12 Rev H remains the hardware identity on the component side and in the engineering files.

The vector master is retained as historical artwork. The 44 × 48 mm board uses 79 underside SMT placements, so its active markings are a compact native-text sugarCANe wordmark plus TERM and GND labels. `kicad-python scripts/apply_bottom_artwork.py` applies these compact markings; `finish_markings.py` refreshes both faces. Rebuilding the historical SVG does not change the compact PCB.

All active markings are on B.Silkscreen. Refresh the silkscreen Gerber, assembly drawings, interactive BOM and renders after editing, then check the exported mask clearances and final image. Electrical qualification status is unchanged.
