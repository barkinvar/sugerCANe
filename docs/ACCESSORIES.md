**Programming, mounting and bench accessories**

These are reusable tools and mounting supplies, separate from the board's US$49.61 component estimate. Use equipment already owned when it meets the stated requirements. The [accessory CSV](../bom/Accessories_DigiKey.csv) records exact order codes and dated observations; nothing has been purchased.

| Item | Selected part | Observed USD | Purpose |
| --- | --- | --- | --- |
| SWD programmer | [STMicroelectronics ST-LINK/V2](https://www.digikey.com/en/products/detail/stmicroelectronics/ST-LINK-V2/2214535), 497-10484-ND | 25.65 | Flash and debug the STM32 |
| Service jumper leads | [Adafruit 1950](https://www.digikey.com/en/products/detail/adafruit-industries-llc/1950/6827084), 1528-1961-ND | 1.95 | Twenty 150 mm female/female 2.54 mm jumper wires; use five for SWD |
| USB/UART cable | [Adafruit 954](https://www.digikey.com/en/products/detail/adafruit-industries-llc/954/7064488), 1528-2128-ND | 9.95 | Configure board ID and startup settings using 3.3 V logic |
| Optional reusable hardware kit | [Adafruit 4685](https://www.digikey.com/en/products/detail/adafruit-industries-llc/4685/13180686), 1528-4685-ND | 16.95 | M3 nylon screws and standoffs; many boards per kit |

The programming tools above total US$37.55 before shipping/tax. Including the optional hardware kit gives US$54.50. Stock observations on 2026-09-07 were 7,207 programmers, 10,997 jumper-wire packs, 5,225 UART cables and 78 hardware kits. Listings can change and the kit observation was an indexed distributor page. The manufacturer's own kit page showed no stock. Recheck the exact DigiKey order code before ordering.

**ST-LINK/V2 to J8**

J8 is a custom 2 × 5 header on **2.54 mm pitch**. It is not a standard Cortex 10-pin connector. Use individual female jumper wires, with power disconnected while attaching them. This mapping applies to the **non-isolated ST-LINK/V2 CN3 20-pin connector**, as defined by [ST UM1075](https://www.st.com/resource/en/user_manual/um1075-stlinkv2-incircuit-debuggerprogrammer-for-stm8-and-stm32-stmicroelectronics.pdf). Other probe connectors have different pin assignments.

| ST-LINK/V2 CN3 | Signal | Board J8 |
| --- | --- | --- |
| 1, VAPP | Target voltage reference input | 1, 3V3 reference output |
| 7 | SWDIO | 2 |
| 9 | SWCLK | 4 |
| 15 | NRST | 10 |
| 4 | Ground | 3 |

Leave the probe's pin 19 supply output disconnected. Power the board through J1 from a current-limited supply; J8 pin 1 reports the board's voltage to the probe and must not be used to feed the board. Keep SWD wires short and start at 1 MHz adapter speed. The ST-LINK/V2-ISOL and STLINK-V3MINIE require their own verified connector mappings; a ribbon cable cannot be assumed to fit this header.

**UART cable to J8**

Adafruit 954 has 3.3 V TX/RX logic and a separate **5 V power lead**. Connect its ground to J8 pin 5 or 9, cable TX to J8 pin 8 (board RX), and cable RX to J8 pin 6 (board TX). Insulate and leave its power lead disconnected. Confirm lead identities against the supplied cable documentation; do not infer TX/RX from a generic cable's colors. Use 115200 baud, 8 data bits, no parity, one stop bit and no flow control.

Power the board before connecting an active UART transmitter so the service input is not driven while its 3.3 V supply is off. Disconnect UART and SWD leads before installing the board in the robot. The firmware guide contains the exact flash and provisioning commands.

**Mounting and robot wiring**

Use four M3 insulating standoffs at least 10 mm high, four M3 × 6 mm nylon screws on the PCB side, and suitable base-side fasteners. The optional 4685 kit includes these sizes. Check screw engagement in the actual standoff; avoid bottoming screws against one another. The 3.2 mm mounting holes are on an 88 × 88 mm square. Nylon mounting does not replace strain relief or an insulating cover.

Use stranded robot-rated wire sized for the actual protected power branch; 18 AWG is the recommended input wiring choice for this prototype. Use a twisted CAN H/L pair and the appropriate terminals at the robot's power-distribution device. Do not use the 28 AWG service jumper wires for robot power or sensor harnesses. Sensor cable gauge, flex rating and pinout depend on the actual sensor. Terminal strip length is 6 mm and nominal screw torque is 0.4 N·m for the selected Wurth connectors.

For qualification, provide a current-limited 0–30 V bench supply, multimeter, oscilloscope with short ground connection, adjustable load or suitable power resistors, and a 1 Mbit/s CAN interface or roboRIO. A 5 V 300 mA dummy load is approximately 16.7 Ω and dissipates 1.5 W; choose a resistor with adequate thermal margin and guard it against contact. A resistor load does not reproduce a sensor's startup capacitance or internal converter behavior.

The [regional sourcing review](SOURCING.md) records additional observations for critical PCB parts. [Representative sensor examples](SENSOR_EXAMPLES.md) are separate from both the board and accessory BOMs.
