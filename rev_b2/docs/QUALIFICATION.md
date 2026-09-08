# Prototype qualification worksheet

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Status: **not physically built or tested**. Record board serial number, PCB lot, firmware hash, instruments, ambient temperature and operator for every run. Start with current-limited laboratory supplies and controlled loads. Exported design checks establish file consistency; they do not establish a production rating.

| Test | Method and acceptance target | Measured result |
|---|---|---|
| Assembly | Inspect polarity, MCU bridges, exposed-pad wetting, fuse, terminal double legs, solder-mask coverage and all seven NPTH holes. Confirm no shorts before applying power. | Pending |
| No-load supplies | Sweep J1 through 5, 6.3, 12, 14.4, 20 and 22 V. Record input current, intermediate rail, internal 5 V and 3.3 V; no oscillation or abnormal heating. | Pending |
| Full shared-rail loads | Apply 300 mA to 5 V and 300 mA to VBAT simultaneously. Repeat each sensor port carrying the full allowed shared-rail load. Measure voltage at the external terminal, including wire and shunt loss. | Pending |
| Low-input startup | Cold-start at 5 V at all load combinations and repeat with realistic source/wire resistance. Inspect both switching nodes and ripple. | Pending |
| Voltage transients | Sweep and interrupt the input; capture MOSFET, TVS and converter voltages with appropriate probes. Confirm absolute maxima and recovery. The TVS rating does not establish load-dump immunity. | Pending |
| Short/inrush | Test each shared output with controlled shorts and representative sensor capacitance. Verify hardware limit/latch, firmware fault report and explicit clear. Evaluate the 40 µF external VBAT capacitance target at 22 V. | Pending |
| Thermal | Repeat full-load tests over the intended enclosure/ambient range. Record regulator, rectifier, inductor, switch, fuse and connector temperatures against datasheet limits with margin. | Pending |
| Input thresholds | For every channel and setting, ramp 0–30 V in both directions and record switching/hysteresis. Verify logic LOW at 0.8 V/HIGH at 2.4 V and industrial LOW at 4 V/HIGH at 7 V over supply/temperature. | Pending |
| Sensor bias | Exercise NPN, PNP, push-pull and open-contact examples with every valid bias setting. Measure leakage/disconnection behavior. Confirm external outputs tolerate the chosen pull-up voltage. | Pending |
| Backfeed | With board off and rails disabled, apply representative externally powered sensor signals within the specified range. Measure logic and rail backfeed; no unintended powering. Never connect two power sources to a selected sensor rail. | Pending |
| Firmware failures | Force foreground stall, watchdog reset, PVD/brownout, crystal/CSS failure and a latched output fault. Check documented safe-off behavior and recovery. | Pending |
| CAN | Test on a correctly terminated 1 Mbit/s robot bus with realistic traffic. Exercise counters, filtering, loss/recovery, duplicate-ID handling and Broadcast Disable. Verify custom Team Use identifiers on a real roboRIO. | Pending |
| Programming | Repeatedly mate the TC2050 cable, verify orientation, target sense and custom adapter continuity, flash/read back, and inspect pogo-pad wear. | Pending |
| Mechanical | Confirm terminal wire retention, actuator access, mounting/enclosure clearance, shunt retention and vibration behavior. Review fabrication-house CAM before volume ordering. | Pending |

Record corrections and rerun affected checks after any failure. The fixed 5 V converter's tolerance and board drops mean the external output is nominal 5 V; applications requiring a strict minimum need measured limits. VBAT follows the input and is never regulated 12 V. Current limits are shared across ports selecting the same rail.
