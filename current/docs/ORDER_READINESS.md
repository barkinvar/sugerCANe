# Rev F pre-order review

**Decision: HOLD a final hardware order.** Rev F is an unbuilt evaluation design. It does not currently meet the requirement to order once and fix only software afterward. Passing schematic checks or a typical simulation cannot establish that an assembled unit will start, survive wiring faults, or operate reliably on the robot.

The review retained the fitted hardware and BOM. Experimental component values are not purchasing instructions. Neither the factory packet nor the source ZIP is a hardware qualification certificate.

## What was cross-checked

| Area | Evidence and practical limit |
|---|---|
| Native schematic and PCB | Fresh KiCad checks: zero ERC/DRC violations and zero unconnected items |
| Circuit agreement | 122 modeled references, 341 pins and 68 named nets agree between model, schematic and PCB |
| Exported copper | Independent reconstruction of all four copper layers and plated connections finds no opens or shorts |
| MCU and CAN | Manufacturer pin functions agree for supplies, CAN, oscillator, SWD, reset and BOOT0; CAN has a hardware standby pull-up |
| Input interface | Comparator polarity and supplies match the manufacturer pinout; tolerance calculation covers the documented LOW/HIGH targets, with explicit leakage assumptions |
| Power budget | DC calculation remains below the buck's 2 A rating; this does not validate startup, regulator interaction or temperature |
| Assembly and recovery | All 119 fitted components remain on top. Programming contacts expose SWD, reset, BOOT0, UART and reference ground/voltage. The custom adapter mapping must be followed |

The existing firmware and driver evidence remains applicable because no firmware changed. Its mocked tests do not verify a physical MCU, flash chip, CAN bus or sensor.

Pin-function references: [STM32F042, LQFP32 pinout and alternate functions](https://www.st.com/resource/en/datasheet/stm32f042t6.pdf), [TCAN3413](https://www.ti.com/lit/ds/symlink/tcan3413.pdf), [LM339LV](https://www.ti.com/lit/ds/symlink/lm339lv.pdf). [Native/electrical evidence index](../reports/release_checks.json).

The native-route DC calculation estimates **79.5 mV** of copper/via drop from the buck feedback reference through the boost supply path at 1.1 A and 85°C, excluding the protection switch itself. The previous 50 mV PCB allowance was too small. The electrical budget now reserves **120 mV**, giving approximately **1.44 A** total normal buck load under its conservative efficiency assumptions, still below 2 A. The 512-corner averaged loop check also passes with the revised input budget. Nominal copper dimensions, ideal conducting pads and assumed via plating make this a planning calculation, not a thermal or manufacturing qualification.

## What prevents sign-off

1. **12 V startup under load.** The unchanged 100 nF soft-start circuit fails the conservative fixed-capacitance cases. The typical voltage-dependent ceramic model passes, so this is a margin problem to resolve, not proof that every board fails. Actual sensor inrush, capacitance and behavior during a slow supply ramp are not yet specified.
2. **Fault-current behavior.** The running-short experiment predicts an 8.61 A inductor pulse. That exceeds the range where the retained linear-inductor approximation is adequate. It does not prove destruction: the inductor's 8 A figure specifies a 20% inductance reduction. Actual peak current, switching-node voltage and component stress remain unqualified. [Bourns specification](https://www.bourns.com/docs/product-datasheets/srp5030ta.pdf)
3. **Controlled recovery.** U4 and U9 EN pins are physically connected to V5_INTERNAL. Firmware can observe a fault but cannot switch either branch off or clear its latch. The rapid-power-cycle simulation also fails in the isolated switch model, so its physical interpretation remains uncertain. The manufacturer supports reset through EN or input power cycling; the board exposes only the latter. [TI TPS2553, latch-off operation](https://www.ti.com/lit/ds/symlink/tps2553.pdf)
4. **The complete power chain is untested.** The SPICE source reaches 5 V using an idealized ramp. The real buck has a nominal 4 ms soft start, its own loop and current limits. Motor noise, brownouts, thermal behavior and both sensor rails loaded together need physical evidence. [TI LMR51420](https://www.ti.com/lit/ds/symlink/lmr51420.pdf)
5. **Sensor compatibility is not defined by NPN/PNP alone.** The hardware's LOW threshold, leakage margin and supply limits are fixed. Firmware cannot make an incompatible residual voltage work reliably. Qualify exact sensor models and cable lengths before accepting the design.
6. **Rail status is not a voltage measurement.** The calculated 12 V monitor rising threshold spans about 8.0-10.6 V. At the lower threshold, an 8.8-9.8 V supply can be reported as present while a sensor requiring at least 10.8 V is undervoltage. The 5 V status comes from U4's fault output; it does not measure the sensor voltage. Firmware cannot correct this blind spot with the existing nets. These are consequences of the circuit and threshold budgets, not measured fault occurrences.

Also review local bypassing in the next electrical change: TI recommends a 1 µF bypass at the TPS61085 IN pin, while C61 is 100 nF and C60 supplies the larger nearby input capacitance. Reducing the bulk input capacitor merely to reduce a simulated fault pulse is not an accepted fix. [TI TPS61085, section 9.2.2.6](https://www.ti.com/lit/ds/symlink/tps61085.pdf)

## Further component exploration

[Retained pre-order review](../reports/electrical/order_readiness.json) · [Completed original power waveforms](../reports/electrical/boost_spice.png) · [Review/reproduction script](../scripts/check_order_readiness.py)

Exploratory runs with 1 µF C66 and reduced bulk input capacitance were stopped before completion. Neither is counted as passed or failed, and neither supports a fitted change. **The PCB/BOM still specify 100 nF C66 and 22 µF C60.** Capacitor changes alone would not address the required recovery and voltage-monitoring capabilities.

The script's optional `--simulate` command can complete that exploration later. Partial traces stay in the ignored workspace. The original eight-case transient report and four completed diagnostic experiments remain the applicable simulation evidence, with the limitations stated in [validation](VALIDATION.md).

## Hardware work required before a final order

Close the startup and short-circuit findings together, retaining adequate input filtering and the shared buck current budget. Compare controlled sensor-load connection or protection directly in the 12 V output path against the present input-side limiter. Verify any revised topology and exact components before adopting it; no output-protection redesign is approved by this review.

Provide MCU control of the protection-switch enables with defined hardware defaults if future software must handle branch restart. Keep the hardware current limit independent of firmware, and require deliberate recovery after a sustained short. The removable 5 V/12 V selection jumpers can remain.

For software to verify sensor supply voltage, provide divided 5 V and 12 V signals to MCU ADC inputs or use suitably accurate hardware voltage monitors. The current MCU has spare digital pins; moving two bias controls can free ADC-capable pins. This is a proposed wiring change requiring electrical/layout review, not an implemented feature or a substitute for fault protection.

Match input thresholds and sensor-power requirements to the actual sensors. For example, Omron's listed E3Z family specifies at most 1 V residual below 10 mA output load, which fits the board's approximately 3.5 mA maximum NPN pull-up current and 1.2 V LOW target. This does not establish compatibility for every Omron or Banner product or its startup load. [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html)

## Evidence needed to release the order

A first article of the final electrical design needs measured startup and steady operation with both rails loaded; the actual sensors and cables; brownouts and restart; cold and running shorts; temperatures; and real CAN programming/recovery. The [validation procedure](VALIDATION.md) gives the full gates. Measurements must identify the PCB revision, fitted BOM and firmware image.

Factory first-article testing could precede lot completion or shipping, but none has been arranged or quoted. Continuity testing and optical inspection are insufficient. User-fitted terminals also require an agreed test fixture or first-article assembly scope.

If a first article and possible hardware correction are impossible, this custom design cannot honestly be represented as a guaranteed one-order solution. Use hardware already validated for the required sensors and robot installation instead of spending the only order on an unresolved prototype.
