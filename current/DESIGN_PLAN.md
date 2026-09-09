# Rev F power and input design

The maintained native PCB and schematic implement the cost reductions below. [The revision regression check](reports/variant_verification.json) compares the result with a frozen Rev E electrical/procurement contract. Historical full sources and packages remain available from the repository archive.

## Supply path

```text
J1: 6–22 V → fuse / reverse-polarity MOSFET / TVS → U1: internal 5 V, 2 A
                                                      ├─ U2: 3.3 V logic
                                                      ├─ U4: latch limiter → 5 V sensor rail
                                                      └─ U9: latch limiter → U8 boost → 12 V sensor rail
5 V / 12 V sensor rails → separate removable jumper on each port → sensor power
```

U1 remains LMR51420XDDCR. U8 is now TPS61085DGKR at 1.2 MHz, with the retained 3.3 µH shielded inductor and a B240A-13-F Schottky diode. Its nominal output is 12.003 V; the conservative static divider/reference budget is 11.64–12.38 V before transient and cable allowances. Three 22 µF output capacitors provide only about 10.8 µF after the modeled DC-bias/tolerance allowances. They must not be replaced by one nominally equivalent small capacitor.

A boost has a direct input-to-output path through its inductor and diode. U9 therefore sits **before the boost** and disconnects that path after an overload deglitch interval. It is the exact TPS2553DBVR-1 latch-off version, with a 21.5 kΩ limit resistor. Its roughly 1.2 A setting is an **input current limit**, not permission to draw 1.2 A at 12 V. The useful output target stays 300 mA. The 5 V sensor branch retains its own U4 limiter. Either latch requires a board power cycle to reset. Output capacitors still release stored energy into a short before it is interrupted; no reverse-powered output or independent output-overvoltage cutoff is supported.

At the modeled worst normal load, the boost needs about 1.02 A from the internal supply. The two maximum branch-limit budgets plus 100 mA logic total about 1.91 A, below U1's 2 A rating. Those calculations assume 80% boost efficiency and specified cable/regulator allowances. They do not establish thermal headroom or safe simultaneous fault transients on a physical PCB.

The unused fourth LM339LV comparator now monitors a divided 12 V rail. Its open-drain output and U9 fault share PG_12V. Nominal rising threshold is about 9.3 V, with a wide 8.0–10.6 V modeled range. It detects a missing/collapsed rail, **not** compliance with a sensor's minimum voltage. Firmware keeps the existing 100 ms health qualification. V12 startup, sensor readiness and thresholds need measurement.

U8 compensation is 13 kΩ / 33 nF. A 512-corner averaged CCM sensitivity screen passes its chosen margins, but its modulator-gain and amplifier bounds are engineering assumptions. It is not a vendor-validated switching model; DCM, cascaded-regulator interaction, startup, shorts and load steps remain bench tests.

## Inputs, jumpers and layout

Each protected divider/comparator input and its software-controlled pull-up/down are retained. NPN, PNP, push-pull, floating and keeper modes remain independent across all three channels. Signal pull-ups use 3.3 V; selecting 12 V sensor power never changes them to 12 V. See [input modes](docs/INPUT_MODES.md).

JP101/JP201/JP301 remain removable 2 mm power headers: 1–2 selects 5 V, 2–3 selects 12 V, and no cap turns off that port's supply. CAN end termination remains a separate solder bridge. There are no input-bias solder selectors or DIP switches.

The board is 52 × 64 mm, down from 52 × 70 mm. Four copper layers are retained: In1 is ground; In2 is ground with a short 12 V monitor branch and a 3.3 V service-contact connection. Converter switching/feedback/compensation and crystal nets stay on top without vias. All 119 fitted components are on top; the assembler places 110 SMT parts and the user fits six terminals and three headers. The user also supplies three removable caps.

Firmware identity is hardware 6 / application 0.7.0 / protocol 4, with separate image/configuration tags. Use this revision's complete package. [Qualification](docs/VALIDATION.md) and [cost basis](docs/COST_REDUCTION.md) describe the remaining boundaries.
