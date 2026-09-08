# Why Rev C has fewer parts

The board is now a three-channel digital input interface. The reduction comes from deleting functions, not removing arbitrary bypass components.

| Change from B/B-2 | Result / tradeoff |
|---|---|
| Delete the 4.2 V buck + boost arrangement; use one 5.067 V nominal buck | Removes a converter, inductor, diode and associated capacitors; supply minimum becomes 6 V |
| Delete rail ADC dividers, software enables and fault-report networks | Power is standalone; CAN cannot report sensor supply failure or cycle a sensor |
| Replace plug-in selectors with solder pads | No ten purchased headers or loose shunts; settings change with an iron |
| Delete selectable industrial threshold | One reference supports 3.3/5 V and typical NPN/PNP sensors; less noise margin than B's industrial mode |
| Delete onboard 3.3 V input bias choice | External 3.3 V pullup needed for non-5-V-tolerant open-drain devices |
| Use one 220 kΩ input series resistor instead of two 110 kΩ | Three fewer resistors; loses the previous single-series-resistor-short fault tolerance |
| Keep one status LED, remove the other indicator networks | Fewer parts; inspect input state over CAN |
| Two mounting holes, smaller board and fewer test pads | 52 × 56 mm; use the documented mounting and service contacts |

Totals: **144 →89 fitted components**, **63 →33 resistors**, **34 →29 capacitors**, **60 ×68 →52 ×56 mm**. All 89 are placed from the top; 83 are SMT and six are through-hole/THR terminals. Solder selectors, pogo contacts, one test point and mounting holes add PCB features, not purchased components.

## Why 29 capacitors remain

Capacitors at different locations perform different jobs. Sharing a distant capacitor does not provide the same local current path. MCU supply pins, the comparator and both CAN supply pins retain local bypass. The clock needs its load capacitors, each input needs its own filter, the buck needs its bootstrap capacitor and input/output reservoirs, and the protected rails need local stability/transient capacitance. The battery limiter's 33 nF capacitor sets its latch delay.

Three 22 µF capacitors remain at the 5 V buck output. Their nominal 66 µF becomes approximately **25.9 µF** under the recorded Samsung typical DC-bias curve and additional design budgets; two would leave about **17.3 µF**, below the 25 µF design target. They are not interchangeable with one arbitrary capacitor labelled 47 or 68 µF. A future single-capacitor substitution needs a specific part's bias curve, loop/transient review and physical tests.

The 5 V feedback divider uses 0.1%, 25 ppm/°C resistors to preserve voltage margin. The PNP pulldowns stay 1206 / 0.25 W because a 30 V input dissipates about 90 mW continuously. Other signal resistors remain hand-friendly 0805. The NPN pullup diodes prevent an externally driven signal from feeding its selected sensor rail through the pullup resistor.

Both current-limit ICs, reverse-polarity MOSFET, TVS parts and CAN default-state resistors remain. Removing those would save little area compared with the terminals while weakening behavior under miswiring, faults or reset. The MCU includes a CAN controller, but still needs the physical CAN transceiver. An ESP32-C3 would not eliminate that transceiver and would add module/firmware considerations without a clear assembly advantage here.
