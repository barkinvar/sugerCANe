**Sensor timing and short pulses — revision A**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Voltage compatibility does not establish how short a beam interruption the complete robot program can observe. This revision samples inputs every 1 ms, applies a configurable 1–100 ms debounce, sends status every 10 ms, and sends each pair of rising-edge counters every 100 ms. The service example selects 2 ms debounce.

The additional pulse study uses the same seven typical comparator circuits as the input-transient analysis, both pulse polarities, 84 widths from 0.25 to 15 ms, four debounce settings, and 100 sample phases. The sampled comparator output is passed through the actual compiled production debounce code. There are 470,400 pulse/setting/phase decisions. Every recognized pulse is counted once; the study also checks that increasing pulse width beyond the first fully captured test point does not lose capture.

| Debounce setting | Smallest tested pulse width captured at all 100 phases, across the 14 waveforms |
| --- | --- |
| 1 ms | 2.00–2.05 ms |
| 2 ms | 3.00–3.05 ms |
| 5 ms | 6.00–6.25 ms |
| 10 ms | 11.00–11.25 ms |

These are **simulation observations, not guaranteed minimum pulse widths**. Width spacing is 0.05 ms near the 2 ms debounce transition and mostly 0.25 ms elsewhere; a listed 6.25 ms does not establish the precise boundary between 6.00 and 6.25 ms. The model uses typical comparator behavior, fixed component values, 1 µs input edges and a maximum 5 µs SPICE step. It does not represent sensor response variability, temperature/process corners, cable pickup or a physical MCU's input threshold. Use actual sensor/cable measurements to establish margin. A 5 ms pulse is a useful initial bench test for the default 2 ms setting, alongside longer and shorter cases.

The [pulse-capture plot](../reports/spice/pulse_response.pdf) and machine-readable `reports/spice/pulse_response.json` record the results. Regenerate them after `calculations/simulate_inputs.py` with `python calculations/simulate_pulse_response.py`; the full release validator runs both in order.

**A captured pulse can still fall between status packets**

The local debounced state can rise and fall between two 10 ms status transmissions. In that case robot code that only reads the latest state can miss the event. Rising-edge counters retain the event until reset, but their 100 ms reporting period adds delay and they contain no event timestamp. Select software inversion so that the event of interest is a logical rising edge.

For counting, establish a baseline on startup and after unavailable data, then compare successive fresh counter samples. Counts are unsigned 32-bit and reset at board boot; reject implausible jumps rather than treating a reboot as billions of events. The two counter pairs are separate samples. The example intake code is a state-based permission check, not a pulse-event latch.

**End-to-end response includes robot scheduling**

The approximately 2–3 ms local debounce latency in the earlier SPICE plots excludes communication and robot scheduling. After a stable transition, the next periodic status can take up to approximately 10 ms; a robot program running every 20 ms can then add almost another 20 ms. The sum is about 33 ms plus CAN arbitration/transport delay in this scheduling example. This is a timing budget, not a bound on a congested bus or a measured roboRIO result.

For a fast moving game piece, check the minimum time the sensor remains asserted at the highest intended speed. Bench-test the complete chain—sensor, wiring, board, CAN and robot loop—against the required response. This revision implements ordinary digital sensing; its filtered inputs and telemetry rates have not been qualified for PWM, quadrature or high-speed encoder capture.
