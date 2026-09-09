# Revision purposes and compatibility

[Overview](README.md) · [Current Rev H](current/README.md) · [Historical packages](archive/README.md)

| Revision | Purpose | Hardware and behavior |
|---|---|---|
| A | Four-channel baseline | 96 × 96 mm; 6–18 V target; Würth terminals and 2.54 mm service header |
| B | Compact configurable prototype | Three inputs, 60 × 68 mm, 5–22 V target; horizontal Weidmüller terminals; physical voltage/bias/threshold selectors |
| B2 | Factory-oriented B | Same circuit/geometry; 49 equivalent passive placements changed and eight unchanged MPNs resourced |
| C Lite | Simplification | 52 × 56 mm, 89 fitted parts, 6–22 V; 5 V plus protected battery rail, fixed input threshold, hardware-only power, protocol 2 |
| D SC12 | Regulated industrial-sensor supply | 52 × 64 mm, 104 fitted parts; regulated 5 V / 12 V, 300 mA shared per rail, hardware 4 / protocol 3 |
| D2 SC12 | Cost reduction and CAN maintenance | Same D electrical features; 98 SMT + nine hand-fitted parts; removable 2 mm power jumpers; app 0.5.0 with CAN ID/setup and recoverable updates |
| E SC12 | Software selection of sensor input type | 52 × 70 mm; 111 SMT + nine hand-fitted parts; app 0.6.0 / hardware 5 / protocol 4; NPN/PNP/push-pull/float/keeper |
| F SC12 | Lower cost with E's input features retained | 52 × 64 mm; 110 SMT + nine hand-fitted parts; app 0.7.0 / hardware 6 / protocol 4; input-protected boost; unresolved startup/short findings |
| **G SC12** | **Resolve the power-path findings and add CAN recovery** | **52 × 74 mm; 126 SMT + nine hand-fitted parts; app 0.8.0 / hardware 7 / protocol 4; output eFuse, rail ADCs and default-off power enables** |
| **H SC12** | **RGB status and low-cost initial programming** | **52 × 74 mm; 130 SMT + ten hand-fitted parts; app 0.9.0 / hardware 8 / boot 1.1.0 / protocol 4; one buffered RGB LED, 2.54 mm service header** |

All revisions are unbuilt prototypes. The early B package with angled terminals is preserved separately because its footprint is not interchangeable with the later horizontal-terminal version.

## F to G

- Move protection to the 12 V output: TPS259620DDAR limits sensor inrush and fault current while leaving the boost reservoir upstream.
- Keep 300 mA shared per rail and the removable 5 V/12 V jumpers. U4 protects 5 V; U9 protects 12 V.
- Add default-off enables and a CAN command that deliberately cycles a faulted branch. A raw-rail-powered inhibit keeps 12 V off even without MCU power.
- Free PB0/PB1 for divided rail measurements by moving two input-bias controls to PB5/PB6. External sensor inputs remain digital.
- Increase C61 to the converter's recommended 1 µF local bypass. Keep the bulk capacitors, inductor and compensation network.
- Allow space for the eFuse, thermal vias and measurement circuit: 52 × 74 mm, top-side assembly only. Parts purchasing rises from $27.17 to $28.81 per board at ten boards; E was $35.14.

Rev F's original packages and failed simulation evidence are preserved in [the archive](archive/README.md). [Current circuit](current/DESIGN_PLAN.md) · [exact regression](current/reports/variant_verification.json) · [verification](current/docs/VALIDATION.md).

## G to H

- Replace the green indicator with one SK6805-EC15 RGB LED at (26,2) mm for a future case window/light pipe. Use a 5 V AHCT buffer and a reset pulldown.
- Use timer/DMA serialization and distinct ready, wait, fault, bootloader and identify patterns. Green requires a recent CAN acknowledgment.
- Replace the pogo pattern with a hand-soldered 2×5 2.54 mm header. Electrical pin numbers stay the same, but the physical layout is now odd/even rows; old cables do not plug in directly.
- Retain G's power circuit, digital inputs, physical voltage jumpers, board outline and top-side assembly. Parts purchasing increases about $0.13 per board at ten; additional assembly fees and a reusable programmer are separate.

## Firmware and wiring compatibility

Use each revision's complete package. H is hardware 8, app 0.9.0, bootloader 1.1.0, with its own update-image tag. Drivers recognize hardware 8; older images are rejected. CAN telemetry remains protocol 4. Initial installation uses the matching factory image and the custom five-wire SWD mapping on J8. [Programming and LED guide](current/docs/STATUS_AND_PROGRAMMING.md).

Voltage selection stays physical. E/F/G/H select input bias in software; D/D2 cannot gain that circuit through firmware. C's battery output is not regulated 12 V. Neither Phoenix nor GrappleHook is this project's protocol.

All revisions are unbuilt designs. The [archive manifest](archive/manifest.json) records immutable packages; prior sources remain in Git history.
