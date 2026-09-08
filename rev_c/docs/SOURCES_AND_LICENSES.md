# Rev C source evidence and notices

KiCad library/model notices are retained under `licenses/`, together with Arm CMSIS, ST device-header and WPILib notices. Firmware third-party directories and InteractiveHtmlBom output retain their notices. Original project work has no selected blanket license. Manufacturer documents/CAD remain their owners' material; retaining a file is not a redistribution-license grant.

| Subject | Primary reference |
|---|---|
| Buck and capacitors | [TI LMR51420](https://www.ti.com/lit/ds/symlink/lmr51420.pdf) |
| Battery limiter, IN tied to VS standalone mode | [TI TPS1H200A-Q1](https://www.ti.com/lit/ds/symlink/tps1h200a-q1.pdf), section 6.3.3 in reviewed Rev E |
| 5 V latch-off limiter | [TI TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf), -1 variant |
| Comparator/leakage caveats | [TI LM339LV](https://www.ti.com/lit/ds/symlink/lm339lv.pdf) |
| CAN interface / bypass | [TI TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf) |
| STM32 pinout, supplies, clock | [ST STM32F042](https://www.st.com/resource/en/datasheet/stm32f042t6.pdf) |
| Example industrial output residual levels | [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html) |
| Terminal geometry and exact MPNs | [Weidmüller 1824420000](https://eshop.weidmueller.com/p/1824420000), [1824430000](https://eshop.weidmueller.com/p/1824430000) |
| CAN addressing / broadcast disable | [WPILib](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html) |

Samsung CL31A226KAHNNNE typical characteristic data is retained in `sources/datasheets/samsung_CL31A226_characteristics.json`, inherited from the earlier design's manufacturer retrieval. Typical curves do not establish guaranteed capacitance. DigiKey URLs, exact codes and dated observations are in `bom/catalog_selected.json`. Vendor STEP URLs, hashes and transforms are in `hardware/library/3d/vendor_connectors.json`.

Equivalent parts need engineering review; distributor substitution suggestions do not establish electrical/mechanical equivalence. Availability and season rules can change after these observations.
