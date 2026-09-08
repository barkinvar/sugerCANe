# Rev D SC12 wiring

Use Rev D hardware, firmware and host tools together. Board coordinates below are viewed from the component side, origin at the top-left PCB corner. Bottom silkscreen is read after turning the board over. Do not infer pin numbering from left/right after flipping.

| Connector | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| J1 power | Positive input, 6–22 V | GND | — |
| J2, J3 CAN | CAN H | CAN L | — |
| J4 input 1 | Selected sensor power | GND | Signal |
| J5 input 2 | Selected sensor power | GND | Signal |
| J6 input 3 | Selected sensor power | GND | Signal |

Each terminal pole has two solder legs; they are one electrical contact. J2/J3 are connected in parallel for bus continuation, with no onboard CAN ground terminal. Common ground comes through robot power. Use twisted H/L wiring; keep branches short. Strip 8 mm using the conductor range specified by Weidmüller for the exact terminal. Press the white release button for removal and for conductor types requiring it. Provide cable strain relief independently of the terminal.

Feed J1 from appropriately fused robot distribution. F1 is secondary board protection. Do not backfeed J4–J6 power pins, parallel the two sensor rails, or apply external power to the programming rail. The board is not galvanically isolated.

## Solder settings

All selectors ship **open**, with no stencil paste on their pads. Configure with power disconnected, then inspect and check continuity. A small iron bridge joins adjacent pads. Remove solder before changing settings.

| Channel | Power selector | Bias selector | Center X, mm |
|---|---|---|---|
| 1 / J4 | JP101 | JP103 | Power 7; bias 13 |
| 2 / J5 | JP201 | JP203 | Power 23; bias 29 |
| 3 / J6 | JP301 | JP303 | Power 39; bias 45 |

These six selectors are at Y=51.5 mm, just above the sensor connectors. **Pads 1, 2, 3 run left to right when viewed from the component side.** The square pad identifies pin 1. Use the detailed assembly drawing/interactive BOM to identify a selector before soldering.

| Selector | Bridge 1–2 | Bridge 2–3 | Open |
|---|---|---|---|
| Power | Regulated 5 V | Regulated 12 V | Port power disconnected |
| Bias | 10 kΩ pullup to selected port supply, through diode: NPN/open collector | 10 kΩ pulldown: PNP | Push-pull or external pullup |

**One bridge per selector. Bridging both sides of a power selector shorts 12 V to 5 V.** Bridge JP2 only at a CAN bus end that needs a 120 Ω termination. Leave it open at intermediate nodes; normally there are two terminations on the entire bus.

Examples:

- Industrial NPN: select the sensor's required supply; bias 1–2. Output current from the pullup is below about 1.3 mA at 12 V. Select inversion in firmware if asserted means pulled low.
- Industrial PNP: select supply; bias 2–3. Verify the sensor's OFF leakage cannot raise the input above the LOW target through 10 kΩ (1.2 V / 10 kΩ ≈120 µA before margin).
- 3.3/5 V push-pull: bias open; select power only if the board powers that sensor. Always connect signal ground.
- 3.3 V open drain that is not 5 V tolerant: bias open, external pullup to the sensor's own 3.3 V rail. There is no onboard 3.3 V sensor supply selector.

Design targets: 0–30 V positive input, LOW ≤1.2 V / HIGH ≥2.4 V, common-ground offset budget ±0.1 V. Do not use as an analog input, quadrature encoder, IO-Link port or continuous negative-voltage input. Sampling is 1 ms with 1–100 ms debounce; short pulses can be missed. Sensor power budgets are shared, 300 mA per rail. Rail-health indications are available; they are not calibrated voltage/current measurements. A fault on either rail makes the health-checked driver input unavailable. See [protocol](CAN_PROTOCOL.md).

## Representative industrial sensors

Regulated 12 V is a suitable nominal supply for the following families, subject to exact model and cable checks. Connect the selected output only; insulate unused complementary output wires separately. Brown/blue/black is common supply/ground/output coloring, but follow the specific datasheet rather than assuming colors.

| Family | Published limits | Rev D setup / limitation |
|---|---|---|
| Omron E3Z three-wire NPN/PNP | 12–24 V ±10%; typically 30 mA maximum, through-beam pair 35 mA; residual ≤1 V below 10 mA | Power 2–3 for 12 V. NPN bias 1–2; PNP bias 2–3. Residual voltage fits the LOW target at this board's small load |
| Banner QS18 standard opposed/diffuse/retroreflective variants | 10–30 V; <25 mA excluding output load; standard outputs <1 V at 10 mA | 12 V supply is in range. Select NPN or PNP bias to match model; use one output. Account for its 100 ms power-up delay |
| Banner QS18 DVS/DL/FF variants | NPN residual specified up to 1.5 V at 10 mA | This exceeds the board's design LOW target. Prefer a compatible PNP variant or qualify actual NPN residual at the ~1.2 mA pullup load; do not assume all QS18 NPN models work |

Sources: [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html), [Banner QS18 manual](https://info.bannerengineering.com/cs/groups/public/documents/literature/197052.pdf). PNP OFF leakage must also meet the input pulldown budget. Observe manufacturer cable/fusing requirements. Two-wire current-loop, AC, analog, IO-Link and safety/OSSD sensors are not supported as interchangeable three-wire inputs.

12 V is specified at the board, not guaranteed at the remote cable end under every transient. The analytical DC divider/reference budget is approximately 11.80–12.22 V before dynamic/distribution allowances; check ≥10.8 V at an E3Z during startup and worst battery/load conditions. Three 30 mA sensors are comfortably within the 300 mA shared design target, but include emitters, indicator loads, cable losses and inrush. The board's 100 ms rail qualification is not proof that every sensor has completed its own startup.

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
