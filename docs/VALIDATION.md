**Validation status — revision A prototype, 2026-09-07**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

The editable design, exports and software have been checked computationally. **No physical PCB, sensor, CAN adapter or roboRIO was available for bench validation.** Passing software/design checks does not establish electrical ratings, EMC compliance, assembly yield or competition approval.

| Check | Result | Evidence and scope |
| --- | --- | --- |
| KiCad schematic ERC | 0 violations | `reports/erc/final.json`; electrical-rule checking of the modeled schematic |
| KiCad PCB DRC | 0 violations, 0 unconnected items | `reports/drc/final.json`; copper clearance, connectivity and configured manufacturing rules |
| Circuit/schematic/PCB parity | PASS | `reports/design_parity.json`; 171 modeled parts, 99 nets, 439 schematic pin nodes; 443 board pads including four additional U3 thermal pads |
| Final device pin review | No assignment mismatch found | `reports/electrical/pin_review.json`; manual manufacturer-source comparison of 97 pins across 11 components; crystal lands changed to Abracon's recommendation |
| Independent Gerber parsing | PASS | `reports/manufacturing/verification.json`; Gerbonara verifies 443 top and 80 bottom X2 pad/net/position records, 268 plated drills, 4 nonplated drills, 96 mm outline, 161 placements and purchased references |
| Independent Gerber copper connectivity | PASS | `reports/manufacturing/gerber_connectivity.json`; separate polygon reconstruction and plated-barrel joins find no shorts, opens or orphan copper islands across 99 named nets |
| Independent Gerber geometry | PASS | `reports/manufacturing/gerber_geometry.json`; clearance, board edge, mounting clearance, annular copper and drill web checks; mask/paste metrics |
| DC ground-return estimate | Numerical checks pass | `reports/electrical/ground_return_model.json`; analytic sheet calibration, reciprocity, solver residuals and two mesh sizes; DC approximation only |
| Local mechanical models | PASS | 161 fitted-component model paths resolve inside the project; simplified original envelopes are identified separately |
| DigiKey purchasing completeness | PASS | 51 purchase lines, 161 fitted components plus 13 shunts, no zero-stock selected line in dated observations; not a live quote |
| DC electrical corners | PASS | `reports/electrical/calculations.json`; 8192 input corners per threshold mode, rail/current/stress/clock calculations |
| Capacitor and routed-power allowances | PASS under stated assumptions | `reports/electrical/capacitor_derating.json`, `power_routes.json`; typical DC-bias curve and geometric resistance estimates |
| Input transient simulation | 7 cases × 100 sample phases pass | `reports/spice/input_results.json`; TI macro-model plus actual production debounce code |
| Pulse capture characterization | 14 waveforms × 84 widths × 4 settings × 100 phases | `reports/spice/pulse_response.json`; expected short-pulse misses are characterized, not a hardware minimum-width guarantee |
| Passive hot-plug sensitivity | 54 cases completed | `reports/spice/inrush_results.json`; useful stress estimates, not MOSFET/TVS/fuse qualification |
| ARM firmware build | PASS, warnings treated as errors | `reports/firmware-build.log`; 7132 bytes flash, 1832 bytes reserved RAM in checked build |
| Static linked-firmware stack screen | PASS | `reports/firmware-stack.json`; 432-byte conservative direct-call/exception estimate within 1024-byte minimum reservation; no runtime watermark measurement |
| Compiled ARM register-model execution | 13 groups pass | `reports/firmware-arm-registers.json`; actual Cortex-M0 binary functions, GPIO/CAN/ADC/UART/watchdog/flash models and 34 halfword interruption cases; no peripheral timing or silicon emulation claim |
| Portable firmware logic | 2,190,989 assertions pass | `reports/firmware-tests.log`; address/undefined-behavior sanitizers enabled |
| Actual application boundary tests | 18 scenarios pass | Same log; normal/unconfigured/clock/CAN/ADC/watchdog/rail-fault/bad-command/UART/stall/busy plus light-load, output-loss and startup cases with simulated board boundary |
| Java integration | 232,928 assertions pass | `reports/driver-tests.log`; Java 17, real WPILib 2026.2.1 jars, simulated CAN transport |
| C++ integration | 75,828 assertions pass | Same log; C++17, actual WPILib 2026.2.1 headers, simulated CAN transport, sanitizers |
| Python service/protocol | 5 tests pass | Same log; protocol vectors, all IDs, random counters, actual UART CLI over a simulated PTY board |
| Offline setup worksheet | PASS in browser | `reports/worksheet_review.json`; mixed-mode jumper/command checks, budget/range rejection, desktop/mobile and print review; no hardware connection |
| Interactive assembly BOM | PASS in browser | `reports/assembly_browser_review.json`; all 161 reference/MPN pairs match the purchasing CSV, component/net lookup, pin-1 highlighting and checkbox persistence |
| Physical electrical, thermal and robot tests | PENDING | Follow `docs/BRING_UP.md`; no measured hardware claims |

The interactive-BOM exporter warns that H1–H4 are absent from the schematic. These are intentional mechanical mounting holes, excluded from electrical netlist/BOM. The separate parity and manufacturing checks account for them explicitly. Gerbonara reports benign KiCad-format/parser warnings concerning header command placement and unused aperture-macro parameters; these are retained in its report rather than silently discarded. No missing copper pads or drill mismatches remain.

The 3D render and Gerber previews are visual review aids. Standard package models and six original simplified package envelopes are included locally. Nominal models do not replace supplier tolerances, wire-bend clearance, tool access or an enclosure fit test. Native KiCad files remain the physical design authority.

**Reproduce the checks**

With the documented toolchain installed, run `bash scripts/validate_release.sh`. This regenerates electrical/BOM data, checks the native design, builds/tests firmware and drivers, exports manufacturing files, and independently compares those exports. SPICE runs are included in that script and save their assumptions/results. Read `TOOLS.md` for installation/provenance and `hardware/design/README.md` before running historical layout scripts.

Do not interpret a check that was not run as passed. The release manifest records actual output hashes so later changes can be distinguished from this reviewed revision. A later footprint, value, firmware or package substitution invalidates the affected result until its relevant checks are rerun.
