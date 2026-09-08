**Source register and third-party notices**

Sources were consulted on 2026-09-07/08. Exact purchase SKUs, product-page links, stock observations and quantity-one prices are stored in `bom/catalog_selected.json` and `BOM_grouped.csv`. They are dated distributor observations, sometimes from indexed listings, not reserved inventory or proof of worldwide delivery. All fitted purchase lines use DigiKey order codes. Alternative MPNs are candidates for engineering review, not approved substitutions.

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
| Comparator | [LM339LV datasheet](https://www.ti.com/lit/ds/symlink/lm339lv.pdf) | 3.3 V operation, failsafe input range, quad pin map |
| Boost | [TPS61322 datasheet](https://www.ti.com/lit/ds/symlink/tps61322.pdf), [TI transient model](https://www.ti.com/lit/zip/slvmcm9) | Fixed 5 V converter, limits, startup model |
| Boost inductor | [SRP4020TA](https://www.bourns.com/docs/product-datasheets/srp4020ta.pdf) | 4.7 µH ratings and custom land dimensions |
| Reverse protection | [AO4485](https://www.aosmd.com/res/data_sheets/AO4485.pdf) | MOSFET pinout, gate/drain ratings, resistance and pulse limits |
| Fuse | [Littelfuse 451/453 datasheet](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) | 1.5 A package, interrupt rating, resistance and nominal melting integral |
| Bias diode | [BAT46W](https://www.vishay.com/docs/86406/bat46w.pdf) | 100 V reverse rating, forward drop and package |
| CAN protection | [ESD2CAN24-Q1](https://www.ti.com/lit/ds/symlink/esd2can24-q1.pdf) | SOT23 H/L/GND mapping and bus protection |
| Inductor | [SRP7028A](https://www.bourns.com/docs/product-datasheets/srp7028a.pdf) | 10 µH current ratings and mechanical outline |
| Crystal | [ABM3B](https://abracon.com/Resonators/abm3b.pdf) | 8 MHz, 18 pF load, ESR/C0, drive level and outline |
| Connectors | [Weidmuller 1885650000](https://datasheet.weidmueller.com/pdf/en/1885650000/scope/1/), [1885660000](https://datasheet.weidmueller.com/pdf/en/1885660000/scope/1/) | Exact 3.5 mm push-in geometry, two solder legs per pole, 135-degree entry |
| Programming contact | [Tag-Connect TC2050-IDC-NL](https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2050-IDC-NL_Datasheet_8.pdf) | Contact pitch, alignment holes, cable envelope and copper clearance; custom electrical mapping |
| Capacitor derating | Samsung CL31A226KAHNNNE manufacturer characteristics; original Rev A research file retained in the development workspace | 30 µF effective capacitance is an engineering simulation assumption for 44 µF nominal; confirm actual bias/temperature loss |
| Aluminum capacitor | [Panasonic FK series](https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/3128) | EEE-FK1H470P dimensions, ripple/impedance and handling cautions |
| ESP32 comparison | [Espressif ESP32-C3 TWAI](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/twai.html) | CAN controller still requires an external transceiver |

Local datasheets and extracted text are research references. Earlier research remains in the parent development workspace; only the current BOM and circuit determine what to purchase. The release manifest records included source-file hashes. Changed-part PDFs are retained in `sources/`; the research file named `weidmuller_3p_90.pdf` is a rejected different-pole-count variant and is excluded from delivery. Manufacturer documents and models retain their owners' copyright and terms; they are not relicensed as original project material.

**Libraries and software**

KiCad standard footprints and package models came from the verified KiCad 10.0.6 distribution. Their original names are retained in each part's `source_footprint` field. Project-local copies make the design portable. The [KiCad library license](https://www.kicad.org/libraries/license/) is CC BY-SA 4.0 with its design-output exception; the notice and legal text are retained in `licenses`. Original custom footprints cover the selected Weidmuller terminals and TI exposed-pad package. The Abracon crystal footprint adapts the KiCad body/model to the manufacturer's recommended land pattern, with its derivation recorded in the footprint provenance file. Original simplified STEP models retain their provenance; changed Rev B models are listed in `hardware/library/3d/rev_b_models.json`. They are not supplier-certified models.

Firmware includes ST CMSIS device headers/startup and Arm CMSIS headers with their original license files. WPILib headers/jars are used for integration compilation and retain the WPILib notice. InteractiveHtmlBom generates the standalone assembly page; its license is included. TI's original TPS613222A model and copyright header are preserved. The ngspice-compatible copy changes initial-condition syntax, and the test deck supplies the startup parameter documented in the engineering report. See `licenses/` and the respective third-party directories for the complete notices.

No blanket public license has been selected for the user's original hardware, firmware or documentation in this private workspace. Third-party licenses continue to apply to their own material. This project has not been published, sold, submitted to a manufacturer or ordered. CTRE, FIRST, WPILib, DigiKey and component names identify compatibility targets or sources, not endorsement.
