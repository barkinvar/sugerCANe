# Rev D source evidence and notices

KiCad library/model notices are retained under `licenses/`, together with Arm CMSIS, ST device-header and WPILib notices. Firmware third-party directories and InteractiveHtmlBom output retain their notices. Original project work has no selected blanket license. Manufacturer documents/CAD remain their owners' material; retaining a file is not a redistribution-license grant.

| Subject | Primary reference |
|---|---|
| Input fuse interruption / derating | [Littelfuse 451/453](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) |
| Buck and capacitors | [TI LMR51420](https://www.ti.com/lit/ds/symlink/lmr51420.pdf) |
| Regulated 12 V converter / exact RYQ0021B package | [TI TPS552872-Q1](https://www.ti.com/lit/ds/symlink/tps552872-q1.pdf), SLVSHF9 August 2023 |
| Shielded 3.3 µH inductor | [Bourns SRP5030TA](https://www.bourns.com/docs/product-datasheets/srp5030ta.pdf) |
| Input/output/bias capacitor curve | [Samsung CL32B106KBJNNW](https://product.samsungsem.com/mlcc/CL32B106KBJNNW.do) |
| Banner supply/residual voltage exceptions | [QS18 product manual](https://info.bannerengineering.com/cs/groups/public/documents/literature/197052.pdf) |
| 5 V latch-off limiter | [TI TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf), -1 variant |
| Comparator/leakage caveats | [TI LM339LV](https://www.ti.com/lit/ds/symlink/lm339lv.pdf) |
| CAN interface / bypass | [TI TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf) |
| STM32 pinout, supplies, clock | [ST STM32F042](https://www.st.com/resource/en/datasheet/stm32f042t6.pdf) |
| Example industrial output residual levels | [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html) |
| Terminal geometry and exact MPNs | [Weidmüller 1824420000](https://eshop.weidmueller.com/p/1824420000), [1824430000](https://eshop.weidmueller.com/p/1824430000) |
| CAN addressing / broadcast disable | [WPILib](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html) |

Samsung CL31A226KAHNNNE typical characteristic data is retained in `sources/datasheets/samsung_CL31A226_characteristics.json`, inherited from the earlier design's manufacturer retrieval. Typical curves do not establish guaranteed capacitance. DigiKey URLs, exact codes and dated observations are in `bom/catalog_selected.json`. Vendor STEP URLs, hashes and transforms are in `hardware/library/3d/vendor_connectors.json`.

Equivalent parts need engineering review; distributor substitution suggestions do not establish electrical/mechanical equivalence. Availability and season rules can change after these observations.

Rev D retains the retrieved Samsung CL32B106 characteristic JSON and TI converter datasheet under `sources/datasheets/`. The project-created converter footprint/model is documented in `hardware/library/converter_package.json`; its STEP representation is parametric package geometry, not official manufacturer CAD. The horizontal connector STEP models are official vendor geometry.
