**Revision A electrical review — calculated and simulated evidence**

The authoritative circuit is `hardware/design/circuit.py`, exported into the native KiCad schematic. The final PCB is checked against its exported netlist and this model. This review describes the actual 171-symbol / 161-purchased-component revision, including Q1 reverse-polarity protection and the final 101 kΩ feedback resistor.

**Input levels and component stress**

Each channel divides SIGNAL through 220 kΩ total into 20 kΩ to ground, with 910 kΩ comparator feedback. The LM2901B is powered from VIN_PROT and its open-collector output is pulled to 3.3 V. Logic thresholds use the parallel 7.15 kΩ reference resistor; industrial thresholds leave that branch open. Two series 110 kΩ resistors distribute signal-voltage stress.

The corner script enumerates 8192 combinations per mode, using ±1.75% total ordinary-resistor allowance, ±3% 3.3 V supply, ±5.5 mV comparator offset, ±50 nA input bias, output LOW up to 0.55 V and 100 nA high-state leakage. The resistor allowance includes 1% initial tolerance, 100 ppm/°C across a 65 °C excursion, and an additional 0.1% allowance. It is an engineering budget, not a qualified board temperature range.

| Mode | Calculated rising threshold | Calculated falling threshold | Declared prototype logic targets |
| --- | --- | --- | --- |
| Logic | 1.571–2.240 V | 0.938–1.425 V | LOW ≤0.8 V, HIGH ≥2.4 V |
| Industrial | 5.352–6.779 V | 4.718–5.960 V | LOW ≤4 V, HIGH ≥7 V |

The 4.7 kΩ 2010 pulldown dissipates at most about 0.195 W at 30 V with the resistor allowance, against a 0.75 W nominal rating before ambient derating. A PNP output leaking 0.5 mA produces about 2.39 V at worst, below the industrial LOW target. An NPN output with 0.5 mA leakage and a 10 V port pull-up releases to at least about 6.87 V in the model. A 3.3 V open-drain output with 50 µA off leakage releases to about 2.315 V under the selected diode/supply allowance. The pull-up calculation uses a 0.60 V engineering diode-drop allowance; the released open-drain value remains above the calculated 2.240 V maximum logic rising threshold. These bounds depend on actual sensor residual voltage, leakage and diode temperature behavior.

The 30 V standoff TVS is transient protection, not a continuous regulator. Its dynamic clamp can reach 48.4 V under its specified pulse condition; the series divider keeps the comparator input much lower. The unidirectional TVS conducts strongly for negative signal voltage, so sustained negative/AC input is not supported. Bias diodes are 100 V BAT46W parts; a common 30 V BAT54 is not an equivalent substitution.

Seven transient cases use TI's LM2901 macro-model under ngspice, with a narrow PSpice area-parameter syntax adaptation retained alongside the original. They cover 3.3/5 V logic, 12/30 V industrial, NPN/PNP leakage and 3.3 V open-drain. A 49 µs glitch is rejected and a valid transition counted once at all 100 sample phases per case using the production C debounce code. This is 700 modeled phase runs. Typical-model transition latency at 2 ms debounce is approximately 2–3.1 ms. Models do not establish worst-case comparator delay, cable EMC immunity or a guaranteed pulse-width specification.

**Power regulation and distribution**

The selected LMR51420XDDCR is the 500 kHz PFM version. Its reference/regulation budget and 101 kΩ / 13.7 kΩ feedback pair yield 5.023 V nominal, with a calculated DC interval 4.922–5.176 V including ±0.3% total feedback-resistor allowance. Do not substitute the Y variant (different frequency) without reviewing L/C and loop behavior.

Three Samsung CL31A226KAHNNNE 22 µF/25 V output capacitors provide 66 µF nameplate capacitance. The manufacturer's typical DC-bias curve loses about 39.5% at 5.176 V. Applying tolerance, temperature, aging and extra modeling allowances gives about 26.10 µF effective output capacitance, above the 25 µF design target. This is a typical-curve engineering estimate, not a manufacturer-guaranteed minimum. An 8 µH minimum inductance and 450 kHz minimum frequency produce about 1.006 A peak-to-peak ripple at 18 V input. L1 has 6 A stated saturation current, above the selected 4.2 A regulator stress criterion.

The first-order 300 mA load-step estimate is about 0.102 V. Therefore the 4.75–5.25 V sensor target is a **steady-state target**; full transient compliance remains a bench test. The regulator is PFM at light load. Check ripple, overshoot, dropout and load-step settling with actual capacitors and PCB parasitics.

The actual routed positive power paths were analyzed using copper geometry at 85 °C, 35 µm copper and a 20 µm via-plating assumption. The graph uses one shortest resistive path and ignores parallel copper benefits; pads are lumped and ground-plane/connector resistance is an added allowance. The longest 5 V rail route is about 103 mm and the longest battery route about 162 mm. With 300 mA sensor current plus a conservative 10 mA bias/bleed allowance concentrated at one connector, U4's 135 mΩ hot maximum, 460 mA upstream budget and 60 mΩ additional contact/shunt/return allowance, predicted minimum regulated connector voltage is **4.806 V**. This calculation is not a field-solved thermal/current-density result.

At 6 V input with both rails supplying 300 mA, 150 mA conservative 5 V logic budget and 80% buck efficiency, estimated input current is 0.830 A including additional 20 mA battery and 10 mA regulated-rail bias/bleed allowances. A 0.196 Ω total entry resistance allowance gives 5.837 V at VIN_PROT. Q1's estimated dissipation is 27.5 mW. The 40 mΩ hot Q1 allowance is not a guaranteed hot resistance at every gate voltage. AP2112 dissipation at the full conservative logic budget is about 0.281 W and requires thermal verification on this PCB.

**Fault protection and startup**

The 5 V switch's 59 kΩ current-limit resistor gives approximately 394–506 mA over the selected equation/tolerance budget. Its overload fault deglitch is 5–10 ms and it latches off. The battery switch's 3.9 kΩ setting gives approximately 428–600 mA; specified accuracy requires VS−OUT≥2.5 V. The 33 nF delay capacitor gives about 11.03 ms nominal hardware latch delay, using typical timing-current/reference values. Actual timing must be measured. Both rails are intended for 300 mA total continuous sensor load, not for actuators.

At 18 V, 40 µF external capacitance plus a 1.1 µF onboard allowance and 320 mA steady load including bias/bleed takes about 6.82 ms to charge at the minimum calculated current limit. The longer 33 nF timing choice improves margin for sensor startup. Timing parameters are typical, so this is not a guaranteed capacitance rating. Sensor startup current can exceed steady current, and larger loads may latch off. There is no automatic retry. Hardware pulldowns keep rails off during reset; software provides manual recovery, watchdog-reset latching and Broadcast Disable handling.

Q1 AO4485 is a 40 V P-channel MOSFET with its drain toward the fused input. D3 clamps its gate-source voltage near 12 V. The topology protects reversed input polarity, but an enhanced MOSFET conducts both directions; it does not block an externally powered output from feeding upstream. External POWER-pin injection is prohibited.

F1 is a 1.5 A fast Littelfuse 451 with nominal 0.853 A²s melting integral and 300 A interrupt rating at 32 V DC. It supplements the protected robot branch; it is not a substitute for upstream distribution protection. SMBJ18A has 18 V standoff and 29.2 V specified clamp at its test current. Continuous board supply is limited to the 6–18 V target; the TVS does not authorize sustained higher voltage.

A 54-case passive hot-plug sweep varies 6/12/18 V, source resistance, harness inductance and bulk-capacitor ESR. It predicts up to about 25.32 V at VIN_PROT, 9.90 mJ TVS energy and 0.0797 A²s input integral in the selected scenarios. A brief input-current peak reaches about 112.75 A. The model treats Q1 as already on and does **not** model gate charging, body-diode safe operating area, fuse temperature, switch failures or standardized surge waveforms. It is a sensitivity study and a reason to measure hot-plug stress, not proof that protection is qualified.

**Clock, CAN and assembly constraints**

The final review corrected the battery switch's open-load interaction: its FAULT output can assert below 10–20 mA even when output voltage is healthy. R23 now senses SENSOR_VBAT, and firmware samples both switched outputs every millisecond. A measured output below 4.5 V latches that enabled rail off after 5 ms startup blanking; ADC failure latches both. The battery switch's autonomous current/thermal protection remains active. Tests specifically cover a healthy asserted open-load FAULT, true output loss with and without FAULT, startup ramp/timeout and runtime ADC failure.

R4 is 1 kΩ and R14 is 10 kΩ. Using BAT46W's 15 µA maximum leakage at 50 V/60 °C as an allowance for four positive signals up to 30 V, plus a conservative feedback-current estimate, the resistor model predicts at most about 0.075 V on unpowered 3V3 and 0.560 V on the battery output. These are leakage-path estimates, not guaranteed powered-off behavior or a 125 °C leakage specification. The qualification target is 0–60 °C ambient; no operating-temperature range has yet been physically established. Characterize the comparator, contamination, cables and power sequencing on real hardware.

The 8 MHz crystal has 18 pF specified load. Two 30 pF capacitors assume approximately 3 pF parasitic load. The calculated transconductance startup margin is about 7.9 using the datasheet ESR/C0 bounds and MCU minimum drive parameter. Verify startup and ≤100 µW crystal drive physically. R20 permits later series-drive tuning.

TCAN3413 uses 3.3 V logic and supply, with standby and TXD pull-ups. The separate ESD2CAN24 protects H/L. Optional 120 Ω termination is open by default. Ground is common with the robot; the bus has no galvanic isolation. A 1 Mbit/s timing configuration of BRP=3, BS1=13, BS2=2 at 48 MHz yields an 87.5% sample point. Board routing checks do not establish bus EMC compliance.

U3's exposed pad is grounded through copper and four thermal vias. Its footprint and stencil windows were built from the selected DGN package drawing. All part pin mappings are explicit in the source model; KiCad ERC, PCB DRC and model/schematic/board parity checks pass. Those checks detect modeled connectivity/clearance errors, not incorrect datasheet interpretation, solder defects or environmental failure. See [VALIDATION.md](VALIDATION.md) for the evidence boundaries and [BRING_UP.md](BRING_UP.md) for remaining physical tests.

**Buck layout and simulation scope**

The [colored power-layout drawing](../output/assembly/power_layout_review.pdf) shows actual exported copper on both layers, viewed from the top. C3 connects directly to the adjacent U1 VIN/GND pins. The final VOUT feedback pickup is at C13's positive terminal; its bottom-layer route stays outside the inductor body. The high-impedance FB node remains short on the top layer beside R1/R2. This follows the regulator's placement guidance but does not establish EMI performance; the prototype still needs ripple, load-step and emissions checks.

The actual X-variant TI transient model, [SLUM848](https://www.ti.com/lit/zip/slum848), was downloaded and inspected. It is encrypted for PSpice 17.4 and cannot run in the installed ngspice engine. No closed-loop buck transient simulation is claimed. The archive and its features/limitations document remain in `sources/models/lmr51420x_ti`. Its header also notes a shortened simulated hiccup interval and no temperature-dependent behavior. The calculated capacitance/ripple/load-step allowances still require the physical tests in the bring-up plan.

**Ground return and manufacturing geometry**

A separate DC resistor-sheet model reconstructs the GND copper from the exported Gerbers, then joins the two layers through the 85 ground-connected plated barrels. It assumes 35 µm copper at 85 °C, 20 µm barrel plating and equipotential top-side contact pads. The solver passes an analytic rectangular-sheet calibration and reciprocity/residual checks. Meshes of 0.15 mm and 0.10 mm agree within 4.4% for the examined routes; the finer mesh solves about 1.26 million unknowns.

Estimated sensor-ground resistance to the buck output-capacitor ground is 3.46–3.57 mΩ, corresponding to about 1.11 mV at 310 mA on the worst examined port. This supports, but does not replace, the existing 60 mΩ contact/shunt/return allowance. Mesh-center edge approximations, filled pad interiors, contact placement and nominal copper/plating dimensions limit accuracy. It models no switching inductance, ground bounce, thermal rise, EMC or manufactured defects. See `reports/electrical/ground_return_model.json` and its two plots for the assumptions and exact Gerber hashes.

Independent exported-geometry checks also find minimum different-net clearance of 0.200 mm, copper-to-board-edge clearance of 0.5005 mm, mounting-center clearance of 3.512 mm, and approximately 0.150 mm minimum plated-hole annular copper. The minimum hole-to-hole web is 0.558 mm. Arc polygons have a 1 µm approximation tolerance. Top mask openings have at least 0.200 mm between separate openings; bottom component paste is empty. These checks screen nominal files and do not guarantee a fabricator's registration, drill wander, plating or stencil process. See `reports/manufacturing/gerber_geometry.json`.

The final layout clears a 3.60 mm nominal-radius region under C1's can on both copper layers, with only its footprint lands permitted. Its VIN via and connecting traces exit outside that body projection. This follows Panasonic's guidance to avoid circuit patterns beneath the aluminum capacitor. C1's ground land connects solidly to the surrounding ground pour; the ceramic input capacitor remains close to U1 for the high-frequency switching loop.
