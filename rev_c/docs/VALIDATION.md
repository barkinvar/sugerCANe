# Rev C Lite validation and prototype qualification

**Unbuilt prototype.** These are computational design checks. No physical power, sensor, CAN, thermal, EMI, ESD, pogo or assembly test has been performed.

## Completed evidence

- Native KiCad 10.0.6 ERC/DRC, zero reported violations and zero unrouted connections: [ERC](../reports/erc/final.json), [DRC](../reports/drc/final.json). Reports list ignored optional checks; not every possible KiCad check is enabled.
- Independent component/pin/net comparison between explicit design, exported schematic and PCB: [parity](../reports/design_parity.json).
- Gerbonara comparison of Gerber pad identities/nets/coordinates, all drills, BOM and placements: [export verification](../reports/manufacturing/verification.json).
- Shapely copper-union/barrel graph finds no opens, shorts or unassigned islands on 70 identified nets: [connectivity](../reports/manufacturing/gerber_connectivity.json). It does not model defective plating or impedance.
- Exported copper edge/net/mount clearance, annular rings, hole spacing and mask/paste geometry: [geometry](../reports/manufacturing/gerber_geometry.json).
- Official Weidmüller CAD/pin alignment checked for six connectors; native model references resolve locally.
- Firmware compiles with warnings as errors. Sanitized host tests exercise CRC/torn configuration, debounce/inversion, counter/timer rollover, malformed commands, configuration/clock/CAN failure, broadcast disable, UART overflow and watchdog scheduling: [firmware tests](../reports/firmware-tests.log).
- Java tests include stale/malformed data and no transmissions from reads; Python/C++ check versions, channel/reserved fields and commands. Actual WPILib 2026.2.1 transport headers/jars compile: [driver tests](../reports/driver/tests.log).

## Electrical budgets

Full formulas and assertions: [check_electrical.py](../scripts/check_electrical.py), [results](../reports/electrical/electrical_checks.json). Signal resistor budget is 1.75% including tolerance, drift and extra allowance. Logic rail ±3%; comparator offset allowance ±5.5 mV; per-input bias ±50 nA; output leakage 100 nA. TI specifies typical, not guaranteed maximum, input bias/leakage. These assumptions require temperature/lot measurements.

The 4,096 evaluated threshold extrema give rising 1.665–2.272 V and falling 1.401–1.933 V. Targets LOW ≤1.2 V / HIGH ≥2.4 V include ±0.1 V ground offset within the model. Nominal hysteresis is about 0.31 V; filter time constant about 18 µs. Sense voltage stays below 2.59 V at 30 V input. The 220 kΩ series resistor dissipates about 4 mW; the PNP pulldown about 92 mW worst budget, so it stays 1206 /0.25 W.

The precision buck divider targets 5.067 V. Reference/divider/leakage budget is 4.953–5.182 V; separate ±40 mV regulation allowance extends it to 4.913–5.222 V. After conservative load-switch drop, the lower 5 V rail budget is **4.871 V before PCB/connector/wire losses**. This does not establish 5 V ±5% at a remote sensor. Three 22 µF output parts give approximately 25.9 µF under typical DC-bias and extra budgets, not a guaranteed minimum.

At 6 V input, 300 mA per sensor rail plus pullups and 100 mA logic allowance, assumed 80% buck efficiency and 0.276 Ω entry resistance give approximately 0.773 A input and 5.787 V protected input. Duty budget is below 95%. Measure actual fuse/FET/trace loss, efficiency, dropout and ripple. Below 6 V the regulated sensor supply is not promised. The 3.3 V LDO loss allowance is about 0.192 W; thermal rise is unmeasured.

Limiter budgets are approximately 0.403–0.626 A battery and 0.394–0.506 A 5 V. They protect **shared rails**, not individual ports. Battery latch delay is roughly 11 ms typical. A heavily loaded rail with capacitive sensors can trip at startup: 40 µF at 22 V with only 83 mA charging margin already takes about 10.6 ms, leaving little margin. No arbitrary external-capacitance rating is established. Characterize actual inrush and delay extremes.

SMBJ22A standoff is 22 V, specified pulse clamp 35.5 V. Buck absolute maximum is 40 V; main bulk capacitor 50 V. Wiring inductance/overshoot can consume the margin; TVS protection is not sustained overvoltage regulation or load-dump qualification. Input SMAJ30A parts are transient clamps, not a continuous negative-voltage rating. CAN protection/common ground do not provide isolation.

## Required bench work

| Test | Exercise and record |
|---|---|
| Assembly / mechanics | Connector orientation/fill, U3 exposed pad, holes/washers, button access, pogo mapping and fixture fit |
| Power | 6/12/22 V no/full shared loads; simultaneous startup; inrush/capacitance sweep; rail voltages, ripple, dropout, efficiency |
| Faults | Separate/simultaneous rail shorts; power-cycle recovery; protected reverse-input test; sensor backfeed |
| Temperature | FET, fuse, buck, inductor, LDO, limiters and pulldowns at load/ambient extremes; derate to measurements |
| Inputs | NPN/PNP and 3.3/5 V push-pull, OFF leakage, LOW residual, thresholds, hysteresis, cable offsets, pulse/debounce limits |
| CAN / firmware | Robot bus loading, bus-off, unplug/replug, broadcast disable/resume, unique IDs, brownout/HSE faults, watchdog |
| Disturbance | Conducted transient, ESD and EMC testing; actual peak clamps and recovery |
| Robot | Sensor supply through battery sag, stale/unpowered-sensor handling, WPILib integration and applicable season rules |

Production qualification and FRC approval have not been established. No sensor supply health detection remains in Rev C.
