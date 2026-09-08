**Representative sensor checks — examples, not a tested compatibility list**

No sensor was physically connected during this design session. These examples show how to apply the board's electrical limits to real products. They are separate from the PCB BOM and are not included in its cost. Confirm the exact purchased sensor's datasheet, cable and output behavior before use.

| Example | Published electrical information | Board setup / remaining check |
| --- | --- | --- |
| Omron E3Z-D61, NPN diffuse photoelectric | E3Z family: 12–24 V ±10%; 30 mA maximum consumption; open-collector output; residual voltage ≤1 V below 10 mA load; 1 ms response. | Battery power, industrial threshold, port-power pull-up. Confirm OFF leakage ≤0.5 mA for the actual revision. Sensor supply must remain ≥10.8 V at its cable end. |
| Omron E3Z-D81, PNP diffuse photoelectric | Same family supply/current envelope; PNP open-collector output. | Battery power, industrial threshold, 4.7 kΩ pulldown. Confirm OFF leakage ≤0.5 mA. At the stated supply minimum, the published residual-voltage allowance leaves enough HIGH-level margin. |
| Adafruit 2167, 3 mm IR break-beam pair | Published supply 3.3–5.5 V; receiver open collector; emitter draws 20 mA at 5 V; response <2 ms. | Regulated 5 V power, logic threshold, 3.3 V pull-up. Include both emitter and receiver in the rail-current budget. The product page does not establish a maximum total current or worst-case OFF leakage; verify them. |

Sources: [Omron E3Z specifications](https://www.ia.omron.com/products/family/407/specification.html), [Adafruit 2167 product details](https://www.adafruit.com/product/2167). The board adds its own 1 kHz sampling and debounce latency to the sensor response.

For a sensor on channel 1, the corresponding selector positions are:

| Example mode | JP101 power | JP102 threshold | JP103 bias |
| --- | --- | --- | --- |
| E3Z-D61 NPN | 2–3 battery | Open, industrial | 1–2, pull to port power |
| E3Z-D81 PNP | 2–3 battery | Open, industrial | 5–6, pulldown |
| Adafruit 2167 | 1–2 regulated 5 V | Fitted, logic | 3–4, pull to 3.3 V |

Only one shunt belongs on each power selector and one horizontal pair on each bias selector. Select software inversion after observing the actual beam/object state; Light-ON/Dark-ON switches can change what an asserted transistor means. Do not infer logical game-piece presence from NPN/PNP alone.

The E3Z examples illustrate a battery-sag limitation: 12 V nominal does not mean the sensor remains within its rated supply during a match. The supplied intake-code example assumes a different generic sensor with a 10 V minimum and uses an 11 V diagnostic threshold. For a 10.8 V-minimum E3Z, use a more conservative starting policy such as **12,000 mV measured switched battery output**, then qualify actual cable drop, measurement error, hysteresis and sensor behavior. This is a robot-code policy example, not a calibrated undervoltage guarantee. A compatible 5 V sensor avoids this particular battery-following supply limitation.

For the break-beam pair, distribute the selected 5 V and ground to both halves using a suitable insulated splice or distribution connection; only the receiver's output goes to SIGNAL. Do not force multiple wire ends into a terminal unless that exact termination is qualified. Keep the cable mechanically secured and confirm operation under the venue lighting and intended target geometry.

DigiKey reference listings observed on 2026-09-07: [E3Z-D61 / Z1108-ND](https://www.digikey.com/en/products/detail/omron-automation-and-safety/E3Z-D61/408008), [E3Z-D81 / Z5588-ND](https://www.digikey.com/en/products/detail/omron-automation-and-safety/E3Z-D81/1778493), [Adafruit 2167 / 2167-ND](https://www.digikey.com/en/products/detail/adafruit-industries-llc/2167/6226609). The D61 product page showed no immediate stock, the D81 showed 30, and the 2167 showed 934; older search listings disagreed. These are examples for engineering comparison, not an assertion that all are available to order now.
