# Revision D — regulated industrial-sensor power

Status: Rev D CAD, firmware, manufacturing exports and engineering review package implemented. Automated checks and final source/archive verification are recorded in the release. Physical prototype qualification remains open.

## Product targets

- Three 0–30 V digital inputs, including suitable 12/24 V PNP/NPN sensors and 3.3/5 V push-pull logic.
- 6–22 V input; selectable regulated 5 V or regulated 12 V sensor power, 300 mA combined sensor load per rail.
- Target PCB 52 × 64 mm; retain horizontal Weidmüller LSF-SMT 3.50 /90 push-in terminals and compact TC2050 programming contacts.
- No removable jumper headers. Top-side assembly; 0805 passives where practical, with small converter bypass capacitors only where layout requires them.
- A synchronous buck-boost converter maintains 12 V on both sides of the battery voltage. Its current-sense resistor replaces the former standalone battery high-side switch.
- Supply the converter's gate-driver bias from the existing efficient 5 V buck. Use automatic light-load power saving rather than forced switching at idle.
- Report converter power-good and 5 V output-switch fault over CAN. Keep the sensor interface independent of firmware power enables.
- Keep prior revisions intact. Case design follows the user's later confirmation; provide dimensions, mounting and access information now.

## Engineering sequence

1. Read primary converter, magnetic, capacitor and connector data. Record exact DigiKey MPNs, dated availability and substitutions that require review.
2. Calculate steady-state limits, ripple, capacitance derating, compensation, startup, input current and plausible thermal losses. Distinguish guaranteed limits, typical curves and engineering assumptions.
3. Generate native KiCad schematic from an explicit pin model. Independently check package pin numbering against manufacturer drawings.
4. Place the converter's input/output hot loops, bootstrap capacitors, inductor and feedback first. Keep its switch copper away from the crystal, CAN and input reference. Reserve mounting and programming access.
5. Route critical connections before general signals; refill ground, inspect copper and run KiCad ERC/DRC and model-to-board parity.
6. Update firmware identity, rail status and host decoders; run existing meaningful protocol, watchdog and driver tests with new rail-fault cases.
7. Export Gerbers, drills, pick-and-place, exact-MPN BOM, schematic, STEP, assembly drawings and CAD-derived renders. Check exported geometry and connectivity independently of KiCad.
8. Review the documents and factory archive from a clean extraction; update the root revision index, commit and push.

## Release boundary

CAD checks can establish consistency and fabricability, not measured converter stability, EMC, thermal performance, sensor compatibility or FRC acceptance. The release must identify outstanding bench tests and applicable FIRST/WPILib integration requirements. Manufacturing orders and a production-qualified designation require those results; no fabricated measurements or certification claims.
