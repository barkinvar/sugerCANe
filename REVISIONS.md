# Revision purposes and compatibility

[Overview](README.md) · [Current Rev F](current/README.md) · [Historical packages](archive/README.md)

| Revision | Purpose | Hardware and behavior |
|---|---|---|
| A | Four-channel baseline | 96 × 96 mm; 6–18 V target; Würth terminals and 2.54 mm service header |
| B | Compact configurable prototype | Three inputs, 60 × 68 mm, 5–22 V target; horizontal Weidmüller terminals; physical voltage/bias/threshold selectors |
| B2 | Factory-oriented B | Same circuit/geometry; 49 equivalent passive placements changed and eight unchanged MPNs resourced |
| C Lite | Simplification | 52 × 56 mm, 89 fitted parts, 6–22 V; 5 V plus protected battery rail, fixed input threshold, hardware-only power, protocol 2 |
| D SC12 | Regulated industrial-sensor supply | 52 × 64 mm, 104 fitted parts; regulated 5 V / 12 V, 300 mA shared per rail, hardware 4 / protocol 3 |
| D2 SC12 | Cost reduction and CAN maintenance | Same D electrical features; 98 SMT + nine hand-fitted parts; removable 2 mm power jumpers; app 0.5.0 with CAN ID/setup and recoverable updates |
| E SC12 | Software selection of sensor input type | 52 × 70 mm; 111 SMT + nine hand-fitted parts; app 0.6.0 / hardware 5 / protocol 4; NPN/PNP/push-pull/float/keeper |
| **F SC12** | **Lower cost with E's input features retained** | **52 × 64 mm; 110 SMT + nine hand-fitted parts; app 0.7.0 / hardware 6 / protocol 4; protected 5 V-fed boost and cheaper passives** |

All revisions are unbuilt prototypes. The early B package with angled terminals is preserved separately because its footprint is not interchangeable with the later horizontal-terminal version.

## E to F

- Replace the battery-fed TPS552872-Q1 buck-boost with TPS61085 fed by the existing internal 5 V regulator. Add a TPS2553DBVR-1 before the boost to interrupt its direct inductor/diode short path.
- Reuse the fourth comparator for coarse 12 V rail status. Both sensor branches now latch on an overload and require a board power cycle to reset. Neither rail status signal is a calibrated measurement.
- Retain removable 5 V/12 V jumpers, electronic input modes, connectors, MCU, CAN and the 300 mA-per-rail useful output targets.
- Resource three unchanged filter capacitors and substitute four equivalent capacitors outside the power stage. Ten-board parts purchasing falls from $35.14 to $27.17 per board, excluding PCB/assembly/freight/tax.
- Reduce PCB area by 8.6%. Four copper layers and top-side-only component placement remain. Factory savings from area/inspection require quotation.

[Electrical explanation](current/DESIGN_PLAN.md) · [exact regression/cost comparison](current/reports/variant_verification.json) · [prototype checks](current/docs/VALIDATION.md).

## Firmware and wiring compatibility

Use each revision's complete package. F has a separate hardware identity, update-image tag and configuration magic; older firmware is rejected. Shared telemetry protocol numbers do not authorize mixing hardware images. CAN servicing needs the initial matching bootloader installation through the documented custom SWD contact mapping.

Voltage selection stays physical; sensor bias selection is software in E/F. D/D2 hardware cannot acquire E/F's electronic bias circuit through an update. C's battery output is not a regulated 12 V output. Neither Phoenix nor GrappleHook is this project's protocol.

The source tree before consolidation is preserved at [commit 9ccb4b7](https://github.com/barkinvar/candi-clone/tree/9ccb4b7). The [archive manifest](archive/manifest.json) records original paths and SHA-256 hashes; original released ZIPs were copied byte-for-byte, without rewriting history.
