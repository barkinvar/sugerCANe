# Rev H status and service models

`LED_SK6805_EC15.step` is a project-generated nominal 1.5 × 1.5 × 0.65 mm envelope from the OPSCO SK6805-EC15 A/1 mechanical drawing. Color and internal construction are illustrative. It is not a manufacturer optical model or a solder-joint/fit qualification.

The project LED footprint reserves a 6 mm diameter circular courtyard for a future non-contact light duct. This is enclosure clearance, not the LED body size. D10 is at (48,39.5) mm in the top-left board coordinate system, with its local bypass C75 immediately above the reserved area. See the enclosure dimensions in [status and programming](../../../docs/STATUS_AND_PROGRAMMING.md).

Source: https://datasheet.lcsc.com/datasheet/pdf/0f4b58ac8908ccf8037b2d7ca0ec1e91.pdf?productCode=C2890035

`Service_2x05_P2.54mm.step` is the KiCad 10 PinHeader_2x05_P2.54mm_Vertical model, used as the nominal envelope for XFCN PZ254V-12-10P: 2.54 mm pitch, 12.70 × 5 mm insulator and 8.5 mm overall above-board height. XFCN drawing specifies 3 mm solder tails; verify actual seated projection. Existing KiCad library licensing applies. The PCB uses 1.10 mm finished holes and 1.70 mm pads for the specified 0.64 mm square pins.

Source: https://datasheet.lcsc.com/datasheet/pdf/50ec9710cee52ae98bff43fbb8887c5b.pdf?productCode=C492422

Neither model establishes physical fit. The ordinary header deliberately replaces the old pogo pattern; its electrical mapping remains custom.
