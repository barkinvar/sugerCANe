# Rev D design choices and component count

Rev D adds regulated 12 V while retaining three inputs and a 52 × 64 mm PCB. Compared with Rev C's 52 × 56 mm, area grows 14.3%; it is still 18.4% smaller than the 60 × 68 mm B versions. Rev C has 89 fitted parts; D has 104. The increase buys regulation across the battery's 12 V crossing and explicit power-health handling.

## What saves space and parts

- A four-switch synchronous TPS552872-Q1 integrates the buck-boost switches and output-current-limit control. It replaces the raw-battery rail and its separate TPS1H200A switch, current-set resistor and three capacitors.
- Its driver uses the existing internal 5 V buck rail, avoiding the high-input-voltage loss of its internal linear bias regulator. The 5 V design reserves 100 mA for this supply. Startup and brownout sequencing must be checked on the prototype.
- One 0.1 ohm 1206 resistor sets the 12 V current limit. Separate PCB Kelvin taps carry the feedback signals; they are copper features, not extra components. This resistor dissipates about 9 mW at 300 mA.
- Both internal copper layers are ground. Signal and power routing stay on the outer layers. The return planes and local ground vias help a compact switching layout; this is not a measured EMI claim.
- MCU internal pullups read the two open-drain health outputs without two external resistors. The converter's unused current-limit and cable-compensation status/functions are omitted.
- 10k compensation resistance reuses an existing BOM line. Firmware inversion/debounce, fixed input thresholds and one status LED retain Rev C's simpler interface.

## Why the remaining capacitors matter

The converter has two bootstrap capacitors, two high-frequency supply bypasses, input/output energy-storage banks, a driver-bias capacitor and compensation capacitor. They serve different current paths. Moving or merging a bootstrap/bypass capacitor into a distant bulk capacitor is not equivalent.

The six added 10 µF 50 V X7R 1210 capacitors share one MPN. Samsung's typical bias curves plus explicit tolerance, temperature and aging allowances give approximately 7.10 µF for the two-cap input bank at 22 V, 15.32 µF for the three-cap output bank at 12.22 V, and 6.20 µF for driver bypass at 5.22 V. TI calls for at least 4.7 µF effective input, 10 µF output and 4.7 µF bias capacitance. These are engineering budgets from typical curves, not manufacturer-guaranteed minima. Substitution needs the same review.

The existing three 22 µF capacitors on the 5 V buck retain its effective-capacitance budget. Input TVS/filter/feedback parts handle industrial wiring and noise. Each MCU/CAN/comparator bypass remains at its local supply pins. [Numerical checks](../reports/electrical/electrical_checks.json) record the assumptions.

## Assembly compromise

There are 39 resistors, 37 capacitors and 28 other fitted parts. Only four capacitors are 0402; other small passives are largely 0805, with 1206/1210 parts where power or effective capacitance requires them. The converter is a 5 × 3 mm HotRod QFN with five long electrical power pads, not a generic exposed-pad QFN. Its footprint follows TI drawing RYQ0021B. A laser stencil, controlled reflow and joint inspection are required for repeatable assembly. This is less forgiving than Rev C's mostly leaded packages.

No per-port electronic power switch, output driver, encoder interface, ADC voltage/current telemetry, wireless radio or USB connector is added. All three ports share each rail's load budget. There are six solder selectors (power and bias per input) and one optional CAN termination bridge, with no loose jumper headers.

## Efficiency and stability scope

Nominal switching frequency is 781.25 kHz; automatic light-load mode is enabled. The shielded 3.3 µH inductor is sized for converter peak-current protection, not just the 300 mA load rating. The low-value shunt and external 5 V gate bias reduce avoidable loss. No measured efficiency percentage is claimed.

The boost continuous-conduction analytical model screens 192 corners using TI equations 19–26, capacitor derating, inductance tolerance, a ±20% transconductance allowance and an assumed full-cycle delay. It is not a switching simulation. PFM, current limiting, line steps, load steps, startup and the buck/boost transition still require measurement. See [loop report](../reports/electrical/converter_loop.json) and [plot](../reports/electrical/converter_loop.png).

At these modest sensor loads, operation can enter discontinuous/light-load mode; the 192-corner CCM model is a screening model rather than a prediction of the normal light-load waveform. The 3.3 µH choice keeps the inductor small with adequate saturation margin, while automatic light-load operation avoids unnecessary circulating current. Measure ripple and input power with the actual sensors.
