# Rev F SC12 wiring

Use the included hardware-6/protocol-v4 firmware and tools; older-revision firmware must not be used on Rev F. Board coordinates below are viewed from the component side, origin at the top-left PCB corner. Bottom silkscreen is read after turning the board over. Do not infer pin numbering from left/right after flipping.

| Connector | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| J1 power | Positive input, 6–22 V | GND | — |
| J2, J3 CAN | CAN H | CAN L | — |
| J4 input 1 | Selected sensor power | GND | Signal |
| J5 input 2 | Selected sensor power | GND | Signal |
| J6 input 3 | Selected sensor power | GND | Signal |

Each terminal pole has two solder legs; they are one electrical contact. J2/J3 are connected in parallel for bus continuation, with no onboard CAN ground terminal. Common ground comes through robot power. Use twisted H/L wiring; keep branches short. Strip 8 mm using the conductor range specified by Weidmüller for the exact terminal. Press the white release button for removal and for conductor types requiring it. Provide cable strain relief independently of the terminal.

Feed J1 from appropriately fused robot distribution. F1 is secondary board protection. Do not backfeed J4–J6 power pins, parallel the two sensor rails, or apply external power to the programming rail. The board is not galvanically isolated.

## Sensor power and software bias

The factory leaves JP101/JP201/JP301 unpopulated for hand soldering. Fit the specified 2 mm headers, then leave caps off for initial bring-up. With power disconnected, fit ONE cap across 1–2 for 5 V or 2–3 for 12 V. No cap disconnects port power. Connecting all three power pins shorts the rails.

The headers are centered at X=7, 23 and 39 mm, Y=51.5 mm. Pins 1–2–3 run left to right from the component side; pin 1 is square. There are no physical input-bias selectors. Set each channel to NPN, PNP, push-pull, float detection or keeper in software; see [input modes](INPUT_MODES.md).

Use Harwin M22-2010305 headers and Sullins SPN02SVEN-RC closed-top caps (2 mm pitch; not 2.54 mm). Caps are friction-retained, not mechanically latched. After voltage/functional verification, support retention with a small removable bead of electronics-grade neutral-cure silicone between the cap exterior and header body, clear of the contacts. This is a proposed retention method; qualify it for your robot vibration/impact environment and enclosure. Allow full cure before use and inspect seating during service. Do not claim these are vibration-qualified merely because there is no slider. Bridge JP2 only at a CAN bus end that needs a 120 Ω termination. Leave it open at intermediate nodes; normally there are two terminations on the entire bus.

Examples: select `npn` for a sinking output (default active LOW), `pnp` for a sourcing output (active HIGH), or `push-pull` for an actively driven logic signal. NPN pull-up current is at most approximately 3.5 mA. Both NPN and PNP compatibility budgets allow 100 µA OFF leakage. No onboard 3.3 V sensor-power output is provided; the signal pull-up is not a sensor supply.

Design targets: 0–30 V positive input, LOW ≤1.2 V / HIGH ≥2.4 V, common-ground offset budget ±0.1 V. Do not use as an analog input, quadrature encoder, IO-Link port or continuous negative-voltage input. Sampling is 1 ms with 1–100 ms debounce; short pulses can be missed. Sensor power budgets are shared, 300 mA per rail. Both sensor branches latch off after a qualified overload; remove the fault and cycle board power to reset. The 12 V limiter is on the boost input, not an independent 300 mA output cutoff. Its rail monitor trips around 9.3 V nominal (wide tolerance), so a healthy flag does not prove a particular sensor has enough voltage. Rail-health indications are not calibrated voltage/current measurements. A fault on either rail makes the health-checked driver input unavailable. See [protocol](CAN_PROTOCOL.md).

## Representative industrial sensors

Regulated 12 V is a suitable nominal supply for the following families, subject to exact model and cable checks. Connect the selected output only; insulate unused complementary output wires separately. Brown/blue/black is common supply/ground/output coloring, but follow the specific datasheet rather than assuming colors.

| Family | Published limits | Rev F setup / limitation |
|---|---|---|
| Omron E3Z three-wire NPN/PNP | 12–24 V ±10%; typically 30 mA maximum, through-beam pair 35 mA; residual ≤1 V below 10 mA | Power 2–3 for 12 V. NPN or PNP software mode. Residual voltage fits the LOW target at this board's small load |
| Banner QS18 standard opposed/diffuse/retroreflective variants | 10–30 V; <25 mA excluding output load; standard outputs <1 V at 10 mA | 12 V supply is in range. Select NPN or PNP bias to match model; use one output. Account for its 100 ms power-up delay |
| Banner QS18 DVS/DL/FF variants | NPN residual specified up to 1.5 V at 10 mA | This exceeds the board's design LOW target. Prefer a compatible PNP variant or qualify actual NPN residual at the ~3.5 mA pullup load; do not assume all QS18 NPN models work |

Sources: [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html), [Banner QS18 manual](https://info.bannerengineering.com/cs/groups/public/documents/literature/197052.pdf). PNP OFF leakage must also meet the input pulldown budget. Observe manufacturer cable/fusing requirements. Two-wire current-loop, AC, analog, IO-Link and safety/OSSD sensors are not supported as interchangeable three-wire inputs.

12 V is specified at the board, not guaranteed at the remote cable end under every transient. The analytical DC divider/reference budget is approximately 11.64–12.38 V before dynamic/distribution allowances; check ≥10.8 V at an E3Z during startup and worst battery/load conditions. Three 30 mA sensors are comfortably within the 300 mA shared design target, but include emitters, indicator loads, cable losses and inrush. The board's 100 ms rail qualification is not proof that every sensor has completed its own startup.

## Programming contacts

J8 uses the **TC2050-IDC-NL mechanical pattern and a custom electrical mapping**, centered at (24, 5.75) mm. Use a mapped adapter, not an assumed ARM/STDC ribbon pinout. Ten 0.7874 mm contact pads are on 1.27 mm pitch, with three mechanical guide holes. In the component-side view, the upper row runs **10, 9, 8, 7, 6** left to right at Y=5.115 mm; the lower row runs **1, 2, 3, 4, 5** at Y=6.385 mm. Pin 1 is at X=21.46 mm, Y=6.385 mm. Use this U-shaped numbering, not an odd/even ribbon numbering assumption.

| J8 pin | Signal | Connection |
|---|---|---|
| 1 | NRST | Probe reset, optional |
| 2 | MCU UART RX | 3.3 V UART adapter TX |
| 3 | MCU UART TX | UART adapter RX |
| 4 | SWCLK | SWD clock |
| 5 | SWDIO | SWD data |
| 6 | +3V3 | Probe VTref sense **only**, board output |
| 7 | GND | Probe ground |
| 8 | GND | UART ground |
| 9 | BOOT0 | Normally leave open; onboard pulldown |
| 10 | GND | Ground |

Power the board through J1 during programming. Leave adapter/probe power disconnected. BOOT0 is normally low. SWD programming and custom pogo-adapter fit require bench verification. The intended clip-free probe is held perpendicular by a fixture; the no-legs pattern does not retain itself.
