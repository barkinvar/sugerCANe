# Rev H status and service models

`LED_SK6805_EC15.step` is a project-generated nominal 1.5 × 1.5 × 0.65 mm envelope from the OPSCO SK6805-EC15 A/1 mechanical drawing. Color and internal construction are illustrative. It is not a manufacturer optical model or a solder-joint/fit qualification.

The project LED footprint reserves a 6 mm diameter circular courtyard for a future non-contact light duct. This is enclosure clearance, not the LED body size. D10 is at (48,39.5) mm in the top-left board coordinate system, with its local bypass C75 immediately above the reserved area. See the enclosure dimensions in [status and programming](../../../docs/STATUS_AND_PROGRAMMING.md).

Source: https://datasheet.lcsc.com/datasheet/pdf/0f4b58ac8908ccf8037b2d7ca0ec1e91.pdf?productCode=C2890035

`Service_2x05_P2.54mm.step` is a project-generated nominal XFCN PM254V-12-10P-H85 female socket envelope. The drawing specifies 2.54 mm pitch, a 13.10 ±0.40 × 5.00 ±0.15 mm insulator, height 8.50 ±0.15 mm and 3.20 ±0.25 mm tails. The model's recessed openings and internal contacts are illustrative. Reproduce it with `scripts/build_service_model.py`.

The custom PCB pad numbering is retained; it must not be replaced by a standard socket footprint with mirrored pin assignments. The 0.64 × 0.40 mm tails fit the retained 1.10 mm plated holes and 1.70 mm pads. The native courtyard encloses the stated maximum housing envelope; confirm insertion and neighboring-part clearance on the first assembly.

Source: https://datasheet.lcsc.com/datasheet/pdf/c2f8cbae228e3b2f37560392ef75a391.pdf?productCode=C492399

Neither model establishes physical fit. J8 has a custom electrical mapping and requires male-ended mapped programming leads.
