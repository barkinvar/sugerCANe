# Rev H source evidence and notices

KiCad library/model notices are retained under `licenses/`, together with Arm CMSIS, ST device-header and WPILib notices. Firmware third-party directories and InteractiveHtmlBom output retain their notices. Original project work has no selected blanket license. Manufacturer documents/CAD remain their owners' material; retaining a file is not a redistribution-license grant.

The sugarCANe underside uses an original pixel-cane illustration and outlined **IBM Plex Sans** lettering (weights 600 and 700) by IBM Corp. The original font is licensed under SIL OFL 1.1; [artwork provenance, pinned font and license](../hardware/artwork/README.md) are retained. No Minecraft asset is included. This branding changes the bottom silkscreen only; SC12 Rev H remains the hardware identity.

| Subject | Primary reference |
|---|---|
| Input fuse interruption / derating | [Littelfuse 451/453](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) |
| Buck and capacitors | [TI LMR51420](https://www.ti.com/lit/ds/symlink/lmr51420.pdf) |
| Regulated 12 V boost | [TI TPS61085](https://www.ti.com/lit/ds/symlink/tps61085.pdf), exact DGK VSSOP package |
| Shielded 3.3 µH inductor | [Bourns SRP5030TA](https://www.bourns.com/docs/product-datasheets/srp5030ta.pdf) |
| Input/output/bias capacitor curve | [Samsung CL32B106KBJNNW](https://product.samsungsem.com/mlcc/CL32B106KBJNNW.do) |
| Banner supply/residual voltage exceptions | [QS18 product manual](https://info.bannerengineering.com/cs/groups/public/documents/literature/197052.pdf) |
| Sensor 5 V latch-off limiter | [TI TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf), -1 variant |
| Sensor 12 V output eFuse | [TI TPS2596](https://www.ti.com/lit/ds/symlink/tps2596.pdf), TPS259620 latch-off variant |
| Comparator/leakage caveats | [TI LM339LV](https://www.ti.com/lit/ds/symlink/lm339lv.pdf) |
| CAN interface / bypass | [TI TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf) |
| STM32 pinout, supplies, clock | [ST STM32F042](https://www.st.com/resource/en/datasheet/stm32f042t6.pdf) |
| Example industrial output residual levels | [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html) |
| Terminal geometry and exact MPNs | [Weidmüller 1824420000](https://eshop.weidmueller.com/p/1824420000), [1824430000](https://eshop.weidmueller.com/p/1824430000) |
| CAN addressing / broadcast disable | [WPILib](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html) |

Samsung CL31A226KAHNNNE typical characteristic data is retained in `sources/datasheets/samsung_CL31A226_characteristics.json`, inherited from the earlier design's manufacturer retrieval. Typical curves do not establish guaranteed capacitance. DigiKey URLs, exact codes and dated observations are in `bom/catalog_china.json`. Vendor STEP URLs, hashes and transforms are in `hardware/library/3d/vendor_connectors.json`.

Equivalent parts need engineering review; distributor substitution suggestions do not establish electrical/mechanical equivalence. Availability and season rules can change after these observations.

Local source evidence includes the TI TPS61085/TPS2553 datasheets and Samsung CL31A226/CL32B106 characteristic JSON. Typical curves do not establish guaranteed minimum capacitance. U8's footprint and nominal STEP body are from the KiCad 10 Package_SO library. Horizontal connector STEP models are official vendor geometry. The new Samsung CL21B105/CL21B475 substitutions retain nominal ratings; the LDO derating allowance is analytical, not a measured characteristic curve.

Rev H sourcing URLs and tiers are in [catalog_china.json](../bom/catalog_china.json). [Header/cap geometry](CONNECTORS.md) links the Harwin and Sullins manufacturer drawings; [cost assumptions](COST_REDUCTION.md) links the assembly fee and lead-time sources. Stock observations are not factory allocations.

Rev H input bias references: [AO3401A](https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf), [BSS138BK](https://assets.nexperia.com/documents/data-sheet/BSS138BK.pdf), [BAT46W](https://www.vishay.com/docs/86406/bat46w.pdf). The local SOT-23 footprint/model comes from installed KiCad libraries under their existing library-license policy. [CTRE input-mode API](https://api.ctr-electronics.com/phoenix6/latest/java/com/ctre/phoenix6/signals/S1FloatStateValue.html) informed feature choices; no CTRE firmware or hardware design is included.

Power transient models: [TI TPS61085 SLIM133B](https://www.ti.com/lit/zip/slim133b), [TI TPS2553-1 SLVM426A](https://www.ti.com/lit/zip/slvm426a), [TI TPS259620 SLVMD54A](https://www.ti.com/lit/zip/slvmd54a), and [Diodes B240A](https://www.diodes.com/spice/download/94/B240A.spice.txt). [Local provenance and hashes](../sources/spice/manifest.json) distinguish original archive bytes from the diode model's plaintext transcription. Manufacturer notices remain in each file. They are manufacturer material, not covered by a project license. The harness only creates temporary compatibility adaptations: unique helper names, duplicate `PARAMS:` cleanup, and PSpice Boolean XOR conversion. It uses Gear integration after observing an artificial latch reset with trapezoidal integration. Simulator compatibility is described by the [ngspice manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf).

Input transient model: [TI LM393LV SNOM697A](https://www.ti.com/lit/zip/snom697a), linked by TI for [LM339LV](https://www.ti.com/product/LM339LV). [Input-model provenance](../sources/spice/input_manifest.json) records the original file hash and its family-level applicability. The original manufacturer notice is retained. This separate harness uses trapezoidal integration and half-timestep comparisons; the power harness keeps its independently checked Gear settings. Bias FETs and sensor outputs are documented circuit abstractions.

Rev H LED/header: [OPSCO SK6805-EC15 A/1](https://datasheet.lcsc.com/datasheet/pdf/0f4b58ac8908ccf8037b2d7ca0ec1e91.pdf?productCode=C2890035), [TI SN74AHCT1G125](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf), [XFCN PM254V-12-10P-H85](https://datasheet.lcsc.com/datasheet/pdf/c2f8cbae228e3b2f37560392ef75a391.pdf?productCode=C492399). [Local geometry provenance](../hardware/library/3d/status_service_models.md) describes the project-created nominal LED and female-socket envelopes. [ST UM2910](https://www.st.com/resource/en/user_manual/um2910-stlinkv3minie-debuggerprogrammer-tiny-probe-for-stm32-microcontrollers-stmicroelectronics.pdf) defines the programmer mapping. [ST RM0091](https://www.st.com/resource/en/reference_manual/dm00031936.pdf), DMA table 29, assigns TIM2_UP to DMA1 channel 2; STM32F042 AF2 maps PB3 to TIM2_CH2.
