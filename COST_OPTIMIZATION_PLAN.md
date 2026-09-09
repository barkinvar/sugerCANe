# Cost reduction and software voltage-selection review

## Implemented: Rev G

The maintained design is **[Rev G](current/README.md)**. Each port's voltage is selected with a removable jumper. All components mount on top. The proposed software voltage selector below is not implemented in the schematic, PCB, firmware or factory package.

| Change | Implemented result |
|---|---|
| Generate 12 V from internal 5 V | F replaced the former buck-boost stage with a TPS61085 boost; approximately $6.66/board saved at ten boards, including shared-part purchasing effects |
| Other passive sourcing | Three unchanged filter capacitors resourced and four equivalent capacitors substituted; approximately $1.30/board saved |
| Repair F's startup and short-circuit behavior | G places a TPS259620 eFuse after the boost reservoir and adds default-off control, CAN fault reset and rail measurement; approximately $1.64/board added |
| PCB size | G is 52 × 74 mm, four copper layers, top-side assembly. F's 52 × 64 mm area reduction was reversed to accommodate the additional circuitry |
| Repository organization | One `current/` project and immutable historical packages in `archive/` |

At ten boards, parts purchasing is **$35.14 for E, $27.17 for F and $28.81 for G** per board. G retains approximately $6.32 of savings versus E, using unrounded arithmetic. PCB fabrication, assembly, freight, taxes, attrition and programming/testing are extra.

[Cost arithmetic](current/docs/COST_REDUCTION.md) · [factory package](current/docs/FACTORY_ORDER.md) · [engineering evidence and physical qualification](current/docs/VALIDATION.md).

## Proposed: independent software selection of OFF / 5 V / 12 V

The user's requirement includes avoiding 12 V on a 5 V sensor during boot, reset, brownout and software errors. Two different fault classes must be addressed:

1. **Unintended switching during startup, reset or supply failure.** External inhibition, reset supervision and controlled sequencing can be designed to hold both source paths off. Their physical timing must be verified.
2. **A valid but incorrect 12 V command.** Ordinary three-wire sensors do not tell this board their supply-voltage rating. A software-selectable limit controlled by the same faulty software cannot independently prevent such a command. A hardware voltage ceiling, physically disconnected 12 V path or separately established sensor identity is required for that stronger requirement.

Checksums, duplicate commands, configuration readback and a watchdog reduce specific failure risks. They do not make a legitimate-looking but incorrect 12 V selection harmless. A current limiter also does not prevent an overvoltage injury at a current below its limit.

### TPS2121 feasibility findings

The TPS2121 is a candidate selector, not a finalized part selection. Its integrated switches and reverse-current blocking can select between 5 V and 12 V, but its default priority behavior needs additional controls:

- The first valid supply can power the output during startup.
- If only one input is valid, the device uses that input. Merely preferring 5 V does not prevent selection of 12 V when 5 V disappears.
- Both inputs can be inhibited through OV1/OV2. Inhibition must remain valid while the MCU and its 3.3 V supply are absent or resetting; a pull-up to a disappearing logic rail is insufficient evidence.
- The specified current-limit adjustment starts at 1 A. It does not replace G's lower-current shared-rail protection, and three per-port limits would not enforce a shared converter budget.
- ST identifies the selected source; it is not a port voltmeter or an equivalent replacement for the existing protection fault outputs.
- Switching from 12 V to 5 V does not instantly remove stored output charge. Port discharge and voltage verification must be addressed before treating the port as ready for a 5 V sensor.

Sources: [TI TPS2121 datasheet, sections 9.3 and 9.5](https://www.ti.com/lit/ds/symlink/tps2121.pdf), [TI discussion of startup inhibition](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/995043/tps2121-output-selection-during-in1-and-in2-power-up-at-same-timing), [TI discussion of disabling both paths](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1237729/tps2121-power-switch).

### Recommended independent limit

Retain a physical **12 V permission link** for each port, in series with that port's 12 V source path. Its absence physically disconnects that source. This link would authorize 12 V; the actual OFF / 5 V / 12 V selection would be electronic.

| Hardware permission | Software request | Intended permitted result |
|---|---|---|
| Absent: 5 V only | OFF | Off |
| Absent: 5 V only | 5 V | 5 V, provided the 5 V source is healthy |
| Absent: 5 V only | 12 V, including an erroneous command | Reject and remain off; the board's 12 V path is physically disconnected regardless of software |
| Present: 12 V allowed | OFF / 5 V / 12 V | Requested state after source and transition checks |
| Either | Reset, unpowered controller or invalid/conflicting commands | Disable both paths; residual charge must discharge before the output can be considered at zero volts |

This ceiling protects a correctly configured 5 V-only port against a wrong software voltage command. It does not identify a sensor, protect a misconfigured 12 V-authorized port, or cover external backfeeding, a PCB short across the link, or every possible component failure. Move links and replace sensors only with power disconnected and the output discharged.

The remaining architecture choice is whether to retain this hardware permission link or accept the wrong-command risk of fully software-controlled selection. The stronger requirement cannot be satisfied by software-controlled limits alone.

### Work required after the voltage-limit choice

- Design independent default-off source inhibition and mutually exclusive source enables. Prevent automatic fallback to an unrequested supply.
- Allocate control I/O; the present MCU pins are assigned. Evaluate a resettable expander or pin reassignment without sacrificing CAN or SWD recovery.
- Provide output discharge and a means to confirm each port's voltage. Existing ADC channels measure the shared rails, not the three connector power pins.
- Define OFF → discharge/verify → select → ramp → verify operation. Reset/update/corrupt configuration must not automatically restore 12 V.
- Preserve hardware shared-rail current limiting and explicit fault recovery. A voltage selector is not an increase in available sensor power.
- Exercise rail ramp order, reset during every transition, brownouts, unpowered control circuitry, stuck control lines, conflicting requests, corrupt settings, an unavailable selected rail, retained capacitor charge and sensor inrush. Evaluate a wrong but valid 12 V command separately from malformed commands.
- Update native CAD, firmware, pricing and documentation together, and rerun affected electrical, simulation, layout and manufacturing checks before producing a new revision's factory files.

These are design requirements, not verified properties of a new circuit. An abstract 64-state Boolean check was used to examine source availability, mutually exclusive requests, reset inhibition and the permission link; it is not a transistor model, transient simulation, firmware test or hardware qualification.

### Cost status

The earlier **+$3–5 per-board parts estimate at ten boards** covered three selector ICs, a supporting-circuit allowance and removal of the original voltage jumpers. It was not a validated BOM or factory quote. Keeping permission links reduces that assumed saving, and the supervisor, control expansion, discharge and per-port verification circuit need actual pricing. Do not treat +$3–5 as a committed price for the stronger fault requirements.

Rev G's order files remain the existing jumper-selected design. No supplier has been contacted or order placed. Hardware assembly, electrical/mechanical qualification and a destination-specific delivery quotation remain outstanding.
