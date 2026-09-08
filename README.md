**FRC Sensor CAN — revision A prototype**

Current variants: [Rev B with horizontal Weidmüller connectors](rev_b/README.md) · [Rev B-2 for China factory assembly](rev_b2/README.md). Each revision has its own matching PCB, BOM and release package.

An original four-channel interface for industrial photoelectric sensors and 3.3 V / 5 V logic, with a native roboRIO CAN connection. The same nominal 12 V robot supply powers the board and its sensors. Each sensor port selects protected battery voltage or regulated 5 V; both rails can operate together.

This repository contains a routed, editable KiCad design, complete DigiKey BOM, firmware, Java/C++ robot interfaces, manufacturing files, and engineering checks. **The design has not been physically built or bench qualified.** Treat the electrical numbers below as prototype design targets, then perform the supplied bring-up tests before robot use.

| Item | Revision A |
| --- | --- |
| Board input | 6–18 V DC target, from one protected robot power-distribution branch |
| Sensor inputs | Four, 0–30 V DC positive signals; selectable industrial or logic thresholds |
| Sensor types | Three-wire DC NPN, PNP, push-pull; 3.3 V open-drain; dry contacts |
| Logic mode | LOW ≤0.8 V, HIGH ≥2.4 V; supports 3.3 V and 5 V logic |
| Industrial mode | LOW ≤4 V, HIGH ≥7 V; suitable for compatible 10–30 V sensor outputs |
| Sensor power | 300 mA usable target **per rail, shared across all four ports**; simultaneous 5 V and battery rails |
| Communication | 1 Mbit/s Classical CAN, documented 29-bit Team Use protocol |
| Data | Debounced digital states, rising-edge counts, supply diagnostics, rail faults |
| Construction | 96 × 96 mm, two layers, 1.6 mm FR-4, 1 oz copper; top SMD and through-hole terminals |
| Assembly | Mostly 0805 or larger passives; LQFP32, SOIC and SOT packages; one exposed-pad IC needs heatbed/reflow |
| Parts estimate | **US$49.61** at checked quantity-one prices, including 13 shunts; PCB, shipping, tax and tools extra |

The MCU is an STM32F042K6T6 with a CAN **controller**. The separate TCAN3413DR provides the CAN **transceiver**. The leaded MCU package, simple firmware, and checked stock made this a useful choice for hand assembly. This board uses its own protocol and does not appear as a CTRE device in Phoenix or Tuner.

Start with the [printable handbook](output/documentation/FRC_Sensor_CAN_RevA_Handbook.pdf) or the [offline sensor setup worksheet](output/documentation/setup_worksheet.html). The worksheet produces jumper settings and a provisioning command; it does not connect to the board.

Project files:

- [Design plan and research method](DESIGN_PLAN.md), [final architecture](docs/ARCHITECTURE.md), and [electrical review](docs/ELECTRICAL_REVIEW.md).
- [KiCad project](hardware/FRC_Sensor_CAN.kicad_pro), [schematic PDF](output/assembly/schematic.pdf), and [PCB](hardware/FRC_Sensor_CAN.kicad_pcb).
- [Interactive assembly BOM](output/assembly/interactive_bom.html), [DigiKey purchasing files](bom/README.md), [assembly guide](docs/ASSEMBLY.md), and [programming/mounting accessories](docs/ACCESSORIES.md).
- [Wiring and jumper settings](docs/WIRING.md), [printable connector/jumper card](output/documentation/wiring_card.pdf), [firmware instructions](firmware/README.md), and [CAN protocol](docs/CAN_PROTOCOL.md).
- [Robot integration](examples/README.md), [bench bring-up checklist](docs/BRING_UP.md), and [validation status](docs/VALIDATION.md).
- [Fabrication files](output/fabrication/README.md), [mechanical STEP model](output/mechanical/FRC_Sensor_CAN.step), [1:1 mounting template](output/documentation/mounting_template.pdf), and [board render](output/review/board_3d_final.png).

Important operating limits: battery output follows the battery; it does not generate regulated 12 V or 24 V. A sensor requiring 10 V can stop working during a robot battery sag while this interface continues running. The default logic mode does not guarantee 1.8 V recognition. PWM, quadrature, IO-Link, analog measurement, open-wire diagnosis, and CAN FD are outside this revision's implemented feature set. Keep external supply voltage off the sensor POWER pins.

All selected purchase lines had stock in the DigiKey listings checked on 2026-09-07. Those listings are dated observations, not reserved inventory or a guarantee of availability in every country. Recheck exact order codes before purchase. See [sources and third-party notices](docs/SOURCES_AND_LICENSES.md).
