# Rev B fabrication files

**Scope: Rev B.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Revision B compact redesign, started 2026-09-08 UTC.

User priorities: substantially smaller than 96 x 96 mm, three inputs acceptable,
5-22 V board input, push-in terminals, close-spaced programming contacts, explicit
5 V / battery sensor supply selection. Retain industrial and 3.3/5 V detection,
repairable hand assembly, DigiKey sourcing, and original CAN firmware.

Implemented design decisions (physical qualification pending):

- Three sensor channels; retain a reserved zero fourth slot in the wire protocol.
- Selected 60 x 68 mm; 55.7% less board area than the 96 x 96 mm revision A.
- Weidmuller 3.5 mm push-in terminal family, through-hole for mechanical retention.
- Standard Tag-Connect TC2050-IDC-NL mechanical footprint, 1.27 mm contact pitch and three guide holes. Custom electrical adapter pinout; no purchased onboard debug header.
- Physical per-port 5 V / protected VBAT selector. Software enables/disables and
  monitors the two shared rails. Software voltage multiplexing would require
  additional high-voltage reverse-blocking switches and interlock circuitry.
- Retain a 36 V rated LMR51420 buck, set to about 4.0 V, followed by TPS613222A
  fixed 5 V boost. This avoids the 5.3 V startup restriction of TPS55165-Q1 and
  the cost/assembly burden of a 21-pin high-voltage buck-boost QFN.
- No regulated 12 V rail: it needs another converter to coexist with regulated
  5 V. VBAT follows the battery; voltage selection does not make it regulated.
- Review changed protection, capacitor ratings, power losses, startup and
  converter interaction; do not inherit Rev A validation for changed circuits.

Iteration gates: manufacturer pin/land drawing review -> schematic parity/ERC ->
placement/connector and pogo access -> short power/clock routing -> full routing
and DRC -> BOM and firmware variant -> independent fabrication review -> concise
assembly/bring-up documentation. Record actual outcomes and unresolved physical
tests. Keep Rev A release intact and place this revision in rev_b/.

Review improvement: replace battery-powered LM2901B with 3V3-powered LM339LVDR. Its rail-to-rail, failsafe inputs retain the divided 0-30V input range and avoid relying on offset specifications below the old comparator's 5V test condition. This changes U7 pin3 and C50 pin1 to 3V3.

Tools and search method: use manufacturer datasheets for pinout, supply limits, derating, timing and land dimensions; DigiKey exact MPN/SKU listings for sourcing; prefer SOIC/SOT23/LQFP and 0805 or larger packages. Use KiCad 10 native hierarchical schematics, explicit model-to-netlist-to-PCB parity checks, short locked converter/clock routes, and reviewed routing for the remaining nets. Check native ERC/DRC, then independently parse exported Gerber copper/drills. Build the actual STM32 firmware and run fault-path host tests. Use vendor SPICE models only within their modeled scope, and publish outstanding physical tests. Preserve Rev A and archive failed experiments without claiming them as validation.
