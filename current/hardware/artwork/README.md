# sugarCANe underside artwork

[sugarCANe.svg](sugarCANe.svg) is the original vector master, 52 × 74 mm, viewed from the underside. The white ink spans approximately 45.9 × 47.2 mm between the connector fields. Three jointed pixel stalks, a small floating soil block and sparse pixel accents sit above the large **sugarCANe** name. No other text is printed on the underside.

The illustration uses an original block/pixel style inspired by sugar cane in voxel games. No Minecraft texture, logo or font is included. The lettering is **Pixelify Sans Bold (700)** by Stefie Justprince, converted to filled outlines. SC12 Rev H remains the hardware identity on the component side and in the engineering files.

Font source: [Google Fonts, pinned commit 8b0a1d0](https://raw.githubusercontent.com/google/fonts/8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5/ofl/pixelifysans/PixelifySans%5Bwght%5D.ttf). The unmodified [font file](../../sources/fonts/PixelifySans.ttf) and its [SIL Open Font License 1.1](../../licenses/PixelifySans-OFL.txt) are retained. Font SHA-256: `9ba86cd010a4de309d263ceff8e8044092c9db7efda869620cb9ff1c4389e8a5`.

Rebuild the vector source with `python scripts/build_brand_artwork.py` from `current/`. Apply it with `kicad-python scripts/apply_bottom_artwork.py`. The importer mirrors the artwork once into native PCB coordinates and uses KiCad's filled cut-contour polygons to preserve letter/stalk holes without a font dependency or raster image. `finish_markings.py` also reapplies this artwork after refreshing the top labels.

All artwork lives on B.Silkscreen, in the **sugarCANe artwork** group. It changes no copper, solder mask, holes, pads, components or top markings. Refresh the bottom silkscreen Gerber, bottom drawing, interactive BOM and render after editing; check the actual exported mask clearances and the final image. Small via holes remain visible through the artwork in the CAD render. Electrical qualification status is unchanged.
