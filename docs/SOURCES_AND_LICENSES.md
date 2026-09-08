**Source register and third-party notices**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Sources were consulted on 2026-09-07. Exact purchase SKUs, product-page links, stock observations and quantity-one prices are stored in `bom/catalog_selected.json` and `BOM_grouped.csv`. They are dated distributor observations, sometimes from indexed listings, not reserved inventory or proof of worldwide delivery. All fitted purchase lines use DigiKey order codes. Alternative MPNs are candidates for engineering review, not approved substitutions.

**Primary technical references**

| Subject | Primary source | Used for |
| --- | --- | --- |
| Functional reference | [CTRE CANdi](https://store.ctr-electronics.com/products/candi), [user guide](https://ctre.download/files/user-manual/CANdi%20User%27s%20Guide.pdf) | Sensor-to-CAN role and regulated/battery sensor outputs; no inherited ratings/protocol |
| Robot electrical rules | [FIRST 2026 manual](https://firstfrc.blob.core.windows.net/frc2026/Manual/HTML/2026GameManual.htm) | Protected power branch, wiring, isolation and CAN constraints; recheck season rules |
| CAN addressing | [WPILib CAN device addressing](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html) | Team Use manufacturer, device type, Broadcast Disable |
| Robot CAN API | [WPILib 2026.2.1 source](https://github.com/wpilibsuite/allwpilib/tree/v2026.2.1), [Java CAN API](https://github.wpilib.org/allwpilib/docs/release/java/edu/wpi/first/wpilibj/CAN.html) | Actual Java/C++ transport interfaces |
| MCU | [STM32F042x4/x6 datasheet](https://www.st.com/resource/en/datasheet/stm32f042f6.pdf), [ES0243 errata](https://www.st.com.cn/resource/en/errata_sheet/es0243-stm32f042x4x6-device-errata-stmicroelectronics.pdf) | LQFP32 pin map, voltage/clock/ADC limits, calibration delay |
| CAN PHY | [TCAN3413 datasheet](https://www.ti.com/lit/ds/symlink/tcan3413.pdf) | SOIC8 pin map, supply, standby and bus protection |
| Buck regulator | [LMR51420 datasheet](https://www.ti.com/lit/ds/symlink/lmr51420.pdf) | X=500 kHz PFM variant, L/C, reference, layout and current limits |
| Logic regulator | [AP2112 datasheet](https://www.diodes.com/assets/Datasheets/AP2112.pdf) | SOT25 pin map and output-capacitor requirements |
| Battery switch | [TPS1H200A-Q1 Rev. E](https://www.ti.com/lit/ds/symlink/tps1h200a-q1.pdf) | DGN pin map/land pattern, limit, latch delay, diagnostics |
| 5 V switch | [TPS2553 datasheet](https://www.ti.com/lit/ds/symlink/tps2553.pdf) | DBVR-1 latch variant, current-limit equations, fault timing |
| Comparator | [LM2901B datasheet](https://www.ti.com/lit/ds/symlink/lm2901b.pdf), [TI simulation model](https://www.ti.com/lit/zip/slcj010) | B-grade electrical limits, quad pin map, transient macro-model |
| Reverse protection | [AO4485](https://www.aosmd.com/res/data_sheets/AO4485.pdf) | MOSFET pinout, gate/drain ratings, resistance and pulse limits |
| Fuse | [Littelfuse 451/453 datasheet](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) | 1.5 A package, interrupt rating, resistance and nominal melting integral |
| Bias diode | [BAT46W](https://www.vishay.com/docs/86406/bat46w.pdf) | 100 V reverse rating, forward drop and package |
| CAN protection | [ESD2CAN24-Q1](https://www.ti.com/lit/ds/symlink/esd2can24-q1.pdf) | SOT23 H/L/GND mapping and bus protection |
| Inductor | [SRP7028A](https://www.bourns.com/docs/product-datasheets/srp7028a.pdf) | 10 µH current ratings and mechanical outline |
| Crystal | [ABM3B](https://abracon.com/Resonators/abm3b.pdf) | 8 MHz, 18 pF load, ESR/C0, drive level and outline |
| Connectors | [691137710003](https://www.we-online.com/components/products/datasheet/691137710003.pdf), [691137710002](https://www.we-online.com/components/products/datasheet/691137710002.pdf) | Exact 5 mm pitch, pin geometry, body, strip length and torque |
| Capacitor derating | Samsung CL31A226KAHNNNE manufacturer characteristics saved in `sources/datasheets/samsung_CL31A226_characteristics.json` | Typical DC-bias curve used by calculation; not guaranteed minimum capacitance |
| Aluminum capacitor | [Panasonic FK series](https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/3128) | EEE-FK1V470P dimensions, ripple/impedance and handling cautions |
| ESP32 comparison | [Espressif ESP32-C3 TWAI](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/twai.html) | CAN controller still requires an external transceiver |

Local datasheets and extracted text are research references. Files for rejected parts remain in `sources/datasheets` to preserve research history; only the current BOM and circuit determine what to purchase. `sources/source_manifest.json` records local-file hashes and provenance where available. Manufacturer documents and models retain their owners' copyright and terms; they are not relicensed as original project material.

**Libraries and software**

KiCad standard footprints and package models came from the verified KiCad 10.0.6 distribution. Their original names are retained in each part's `source_footprint` field. Project-local copies make the design portable. The [KiCad library license](https://www.kicad.org/libraries/license/) is CC BY-SA 4.0 with its design-output exception; the notice and legal text are retained in `licenses`. Original custom footprints cover the selected Wurth terminals and TI exposed-pad package. The Abracon crystal footprint adapts the KiCad body/model to the manufacturer's recommended land pattern, with its derivation recorded in the footprint provenance file. Six original simplified STEP models are listed with drawing sources in `hardware/library/3d/original_models.json`. They are not supplier-certified models.

Firmware includes ST CMSIS device headers/startup and Arm CMSIS headers with their original license files. WPILib headers/jars are used for integration compilation and retain the WPILib notice. InteractiveHtmlBom generates the standalone assembly page; its license is included. TI's original LM2901 model and copyright header are preserved, and the ngspice-compatible adaptation changes only the diode area-parameter syntax needed by the simulator. See `licenses/` and the respective third-party directories for the complete notices.

No blanket public license has been selected for the user's original hardware, firmware or documentation in this repository. Third-party licenses continue to apply to their own material. The project is versioned in Git; no physical board has been built and no manufacturing order has been placed. CTRE, FIRST, WPILib, DigiKey and component names identify compatibility targets or sources, not endorsement.
