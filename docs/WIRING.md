**Revision A wiring and configuration**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

The [offline setup worksheet](../output/documentation/setup_worksheet.html) can produce a per-channel jumper table and a UART provisioning command for the common modes below. The [two-page bench card](../output/documentation/wiring_card.pdf) shows the actual top-view connector orientation and six illustrated jumper examples.

Disconnect board power before moving jumpers or wiring terminals. Use the square pad, pin number and assembly drawing to identify pin 1; connector orientation on the page is not a pin-number definition.

| Connector | Pin 1 | Pin 2 | Pin 3 |
| --- | --- | --- | --- |
| J1, board supply | Positive 6–18 V | Ground | — |
| J2, J3, CAN trunk | CAN H | CAN L | — |
| J4, channel 1 | Selected sensor POWER | Ground | SIGNAL |
| J5, channel 2 | Selected sensor POWER | Ground | SIGNAL |
| J6, channel 3 | Selected sensor POWER | Ground | SIGNAL |
| J7, channel 4 | Selected sensor POWER | Ground | SIGNAL |

J2 and J3 are electrically parallel. Continue the twisted CAN pair through these connectors, keeping untwisted sections and stubs short. Use the robot's common power ground; the CAN connectors themselves contain no ground pin. This board is not isolated. Fit JP2 only at a physical end of the CAN trunk. With the robot unpowered and all devices connected, two 120 Ω end terminations normally measure about 60 Ω between H and L.

Feed J1 from **one protected power-distribution branch**. A 5 A fuse branch with 18 AWG red/black copper input wiring is a conservative starting choice; select a fuse type allowed for the actual distribution device and season. The onboard 1.5 A fuse is additional board protection. Do not connect this board to battery terminals, the main unprotected distribution input, or the dedicated roboRIO/radio branch. Keep the PCB electrically isolated from the robot frame. Review the current [FIRST robot electrical rules](https://firstfrc.blob.core.windows.net/frc2026/Manual/HTML/2026GameManual.htm), including R610, R611, R615, R617, R620, R622 and R716; this project has no inspection approval.

The selected Wurth terminals specify 6 mm wire stripping and 0.4 N·m screw torque. Verify the current part drawing and use a suitable torque tool; do not leave exposed strands. Match sensor cable wire size and ferrules to the connector and sensor documentation. Brown/blue/black are common sensor power/ground/output colors, but **the sensor's own pinout controls**. Two-wire sensors need a separate compatibility assessment; these examples are for three-wire DC outputs.

**Per-channel jumpers**

| Channel | Power selector | Threshold selector | Bias selector |
| --- | --- | --- | --- |
| 1 | JP101 | JP102 | JP103 |
| 2 | JP201 | JP202 | JP203 |
| 3 | JP301 | JP302 | JP303 |
| 4 | JP401 | JP402 | JP403 |

Power selector: pins **1–2 = regulated 5 V**, **2–3 = protected battery**, open = no board power at that port. Install one shunt at most. Bridging all three pins joins two power rails and is prohibited.

Threshold selector: **open = industrial**, shunt fitted = **3.3/5 V logic**. Industrial mode targets LOW ≤4 V and HIGH ≥7 V. Logic mode targets LOW ≤0.8 V and HIGH ≥2.4 V. Voltages between each pair are not a defined logic level; hysteresis intentionally retains the prior state over part of this interval.

Bias selector is a 2×3 header. Pin pairs are across each row: **1–2 = pull up to selected port power**, **3–4 = pull up to 3.3 V**, **5–6 = pull down to ground**. Install one horizontal shunt at most, or leave all open for a driven signal. Each branch contains 4.7 kΩ; pull-ups also contain a blocking diode. The assembly drawing marks pin 1.

| Sensor/output | Power selection | Threshold | Bias | Typical software inversion |
| --- | --- | --- | --- | --- |
| 10–30 V three-wire NPN, active-low output | Battery, if sensor works over actual battery range | Industrial/open | Port pull-up, 1–2 | Invert its channel bit |
| 10–30 V three-wire PNP, active-high output | Battery, if compatible | Industrial/open | Pulldown, 5–6 | Usually none |
| 5 V push-pull | 5 V, if power is needed | Logic/fitted | Open | Match desired meaning |
| 3.3 V push-pull from another controller | Open; separate compatible supply | Logic/fitted | Open | Match desired meaning |
| 3.3 V open-drain output | Compatible supply; 5 V only if sensor permits | Logic/fitted | 3.3 V pull-up, 3–4 | Usually invert |
| Dry contact to ground | Open | Logic/fitted | 3.3 V pull-up, 3–4 | Usually invert |

The board does not provide a general 3.3 V sensor-power output. J8 pin 1 is a service reference, not a sensor supply. Selecting 5 V port power does not make a 3.3 V-only sensor safe to power.

For an externally powered 24 V sensor, connect its ground and output to the port's GND and SIGNAL, leave POWER disconnected, and leave the power selector open. A PNP output can use the onboard pulldown. An NPN output needs a suitable external pull-up to its sensor supply, or the onboard 3.3 V pull-up with logic thresholds if the sensor's off leakage and low-state voltage meet the logic limits. **Never feed external voltage into a POWER pin.** External supply arrangements must also comply with the robot rules.

The 300 mA limit is a design load budget for each entire rail, including all attached sensors and pull-up currents. It is not 300 mA per connector. A short or excessive startup current disables every sensor on that rail. Battery output is lower than board input by protection, switch and wiring losses; it is not regulated 12 V. Qualify low-battery behavior using the real sensor. A device needing at least 10 V may become unreliable well before this board resets.

Industrial examples assume low-state voltage ≤4 V and off leakage ≤0.5 mA; the NPN release calculation uses a 10 V port supply. The 3.3 V open-drain example budgets ≤50 µA off leakage and low voltage ≤0.8 V. Check the actual sensor data rather than its NPN/PNP label alone. Continuous positive SIGNAL voltage is limited to 30 V. The TVS does not make negative DC, AC mains, or higher continuous voltage acceptable.

**Service connector J8**

This is a **custom 2×5, 2.54 mm header**, not a standard Cortex debug cable pinout. Use individual labeled wires or a verified adapter.

| Pin | Signal | Connection |
| --- | --- | --- |
| 1 | 3.3 V reference output | Programmer VTref input only; no external power |
| 2 | SWDIO | Programmer SWDIO |
| 3 | GND | Programmer ground |
| 4 | SWCLK | Programmer SWCLK |
| 5 | GND | UART ground, if convenient |
| 6 | UART TX from board | 3.3 V USB-UART RX |
| 7 | BOOT0 | Normally low; leave open |
| 8 | UART RX into board | 3.3 V USB-UART TX |
| 9 | GND | Additional service ground |
| 10 | NRST | Programmer reset, if used |

Leave the USB-UART power wire disconnected. Do not use a 5 V TTL output or an RS-232 voltage interface. JP1 briefly shorts NRST to ground for reset; do not leave a shunt installed. For ROM bootloader recovery, connect BOOT0 to the board's 3.3 V reference with a temporary wire, reset, use the documented STM32 UART bootloader, then remove the wire and reset. SWD programming is the primary supported procedure.

Software configuration and explicit fault recovery are described in [firmware instructions](../firmware/README.md). Do not configure a rail on until its wiring and jumpers have been inspected.

See [representative sensor checks](SENSOR_EXAMPLES.md) for NPN, PNP and 5 V break-beam examples and the extra supply/leakage checks each requires.
