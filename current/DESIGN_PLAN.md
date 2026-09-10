# Rev H power and input design

Rev H retains G's protected power circuit and adds RGB status and ordinary-header programming. The [regression report](reports/variant_verification.json) records every change against the frozen G circuit.

## Supply path

```text
6–22 V → fuse / reverse protection / TVS → internal 5 V, 2 A
                                          ├─ 3.3 V MCU / CAN / comparators
                                          ├─ U4 latch limiter → SENSOR_5V
                                          └─ U8 boost → reservoir → U9 eFuse → SENSOR_12V
SENSOR_5V / SENSOR_12V → removable jumper per port → sensor power
```

U1 remains LMR51420XDDCR. U8 remains TPS61085DGKR, with the 3.3 µH shielded inductor, B240A diode and 13 kΩ / 33 nF compensation. C61 is now a 1 µF local bypass. C60 remains 22 µF, and C62–C64 remain three 22 µF reservoir capacitors. Their effective capacitance at 12 V is much smaller than their nameplate value; the checks include both explicit derated and nameplate cases.

A boost has a direct path through its inductor and diode. Rev H puts **TPS259620DDAR after the reservoir**, so a sensor short cannot discharge that reservoir directly through the port. R62=2.61 kΩ sets about 357 mA nominal output current limit; the tolerance budget is in [electrical_checks.json](reports/electrical/electrical_checks.json). Useful sensor load remains **300 mA shared per rail**. C70=47 nF controls output slew; C65/C71 provide local input/output bypassing. D5 clamps negative output transients and D6 limits raw-rail transients. These parts do not authorize reverse powering a sensor port.

U9's UVLO divider requires approximately 11.1 V on the raw boost before connection. OVCSEL is intentionally open for its **13.8 V-class fault clamp**, not a precision 12 V ceiling. R70 pulls Q2's gate from raw 12 V, holding UVLO low by default. PB7 HIGH enables Q3, which removes that inhibit. R75 holds Q3 off without MCU power. U4's PA15 enable has a hardware pulldown. Both branches therefore start disabled; their current limits operate independently of firmware.

Firmware starts 5 V after 10 ms and 12 V after 60 ms. It allows 200 ms for startup, requires 100 ms healthy voltage before counting inputs, and latches a running low-voltage fault after 20 ms. Hardware fault indications or excessive measured voltage disable the affected rail. Removing a short does not automatically restart it: use the explicit CAN power-reset command. The bootloader keeps both rails off.

## Rail measurement and signals

PB0/ADC8 and PB1/ADC9 measure the protected 5 V and 12 V rails. Each divider uses two 100 kΩ precision series resistors, a 20 kΩ bottom resistor and a 10 nF filter. Firmware uses 239.5-cycle acquisition and the factory VREFINT calibration value. Readback and rail states are available through CAN service. This measures the board rails, not the voltage at a remote sensor.

The former coarse fourth comparator is unused, with defined inputs and an unconnected output. The three signal comparators and electronic NPN/PNP/push-pull/float/keeper circuits retain their original values. Two pulldown controls move to PB5/PB6; channel 3 stays on PB4. Selecting 12 V sensor power never changes the signal pull-up from 3.3 V.

External inputs remain digital: target LOW ≤1.2 V, HIGH ≥2.4 V, positive 0–30 V and common ground. Sensor off-state leakage, cable capacitance and residual voltage must meet the [input-mode limits](docs/INPUT_MODES.md). Rail ADCs do not add external analog or encoder support.

## Layout and assembly

The board is 52 × 74 mm with four copper layers and all 140 fitted components on top. The factory places 129 SMT parts; the user hand solders the DigiKey STM32F042K6T6 MCU, six terminals, three voltage headers and one J8 service socket, then fits three loose caps. U9 uses a split-paste exposed pad and surrounding thermal vias. No blind/buried vias or second-side assembly is required.

One inner layer provides continuous ground; the other also carries a few slow control/service connections. Switching, feedback, compensation and crystal routes remain on top. Native and independently reconstructed fabrication geometry are checked separately.

Use hardware 8, application 0.9.0, bootloader 1.1.0 and protocol 4 from the same release. [Verification](docs/VALIDATION.md) distinguishes calculations and simulation from physical qualification. [Cost basis](docs/COST_REDUCTION.md) includes supplier minimums and excludes assembly/freight/tax.

Rev H design envelope: at most 100 µF total external capacitance on the shared 12 V rail, and 22 µF on the shared 5 V rail, at 300 mA per rail. The startup calculation includes +20% capacitance and the current-limit minimum; the 470 µF simulation is a typical diagnostic beyond that envelope. Qualify nonlinear sensor inrush separately.

## RGB diagnostics and low-volume programming

H replaces the single green LED with one SK6805-EC15, a 5 V AHCT buffer, data pulldown, series resistor and local bypass capacitors. PB3 remains the status pin and uses timer/DMA serialization. J8 is a hand-fitted recessed female 2×5 2.54 mm socket with the same electrical pin numbers and odd/even physical pattern as the preceding Rev H header. [Status, case opening and inexpensive programmer](docs/STATUS_AND_PROGRAMMING.md).
