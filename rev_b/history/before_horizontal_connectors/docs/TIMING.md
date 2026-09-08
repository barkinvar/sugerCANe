# Sampling and event timing — Rev B

Inputs are sampled every 1 ms. Firmware applies configurable 1–100 ms debounce, sends status every 10 ms and sends each pair of rising-edge counters every 100 ms. The service example selects 2 ms debounce. There are three active inputs; the fourth protocol slot remains zero.

A short pulse can fall between samples. A pulse detected by one sample can also disappear before the debounce interval completes. Allow at least the configured debounce interval plus a sampling interval, analog/sensor delay and margin; establish the actual minimum pulse width on hardware. A 5 ms pulse is a useful initial bench test with 2 ms debounce, followed by shorter and longer pulses at varied phase. Rev B has no measured pulse-capture guarantee.

A debounced pulse can occur entirely between two status packets. Rising-edge counters retain a captured logical rising event until reset, but their slower reporting adds delay and they carry no timestamp. Select inversion so the event of interest is a rising edge. Establish a counter baseline on startup and after data loss, handle unsigned rollover, and reject implausible jumps after a board reboot. The two counter-pair messages are separate samples.

With 2 ms debounce, local firmware response is roughly 2–3 ms after the sampled electrical transition, excluding analog delay. The next status transmission can add approximately 10 ms and a 20 ms robot loop can add almost another 20 ms. CAN arbitration and transport delay add to this scheduling budget; it is not a measured or guaranteed end-to-end bound.

Check the shortest beam interruption at the highest expected game-piece speed. Test the complete sensor, wiring, board, CAN and robot loop. These filtered digital inputs and telemetry rates are not qualified for PWM, quadrature or high-speed encoder acquisition. The Rev A comparator pulse study is not claimed as Rev B validation.
