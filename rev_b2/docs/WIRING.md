# Rev B-2 wiring and setup

This revision has three independent digital sensor inputs, two shared switched power rails, and a custom 1 Mbit/s CAN interface. It is a prototype design; physical bring-up and qualification remain outstanding. It does not implement CTRE Phoenix or Tuner.

| Connector | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| J1 input | +5–22 V DC | Ground | — |
| J2, J3 CAN | CAN H | CAN L | — |
| J4 sensor 1 | Selected power | Ground | Signal |
| J5 sensor 2 | Selected power | Ground | Signal |
| J6 sensor 3 | Selected power | Ground | Signal |

Use the numbered pads and board markings. J1–J3 face the opposite board edge from J4–J6, so pin numbers are more reliable than assuming the same left-to-right order. The two solder legs for each terminal pole are the same electrical pin. CAN terminals do not provide a ground pin: power grounds establish the shared reference.

Supply 5–22 V **at J1 under load**. The maximum is 22 V including supply tolerance. A nominal 24 V industrial supply is outside this input rating, although a separately powered sensor may present a positive signal up to 30 V. Use an appropriate fused FRC distribution output and common ground; the onboard 1.5 A fuse does not replace robot distribution protection.

Weidmuller /90 terminals take wires horizontally, parallel to the PCB, with push-in actuators. Sensor terminals are 1824430000; power/CAN terminals are 1824420000. Strip 8 mm. Follow the manufacturer's conductor/ferrule limits; 20–22 AWG flexible robot wiring is a practical starting point. Press the actuator to insert or remove fine-stranded wire when required. Secure cables against robot vibration and pulling. Assemble the through-hole terminals after the surface-mount parts.

## Select sensor power

Each port gets its own three-pin selector. **Turn board power off before changing shunts. Fit exactly one power shunt per powered port.**

| Port | Selector | Bridge pins 1–2 | Bridge pins 2–3 | No shunt |
|---|---|---|---|---|
| 1 | JP101 | Regulated 5 V | Protected switched VBAT | Power pin disconnected |
| 2 | JP201 | Regulated 5 V | Protected switched VBAT | Power pin disconnected |
| 3 | JP301 | Regulated 5 V | Protected switched VBAT | Power pin disconnected |

VBAT follows the input voltage, less protection and wiring losses. It is not regulated 12 V. A sensor requiring 10 V minimum can stop operating when the FRC battery sags, even though the board itself continues running. The 5 V rail has a 300 mA design target shared across all ports selecting it; the VBAT rail has a separate 300 mA shared target. These are total rail budgets, not 300 mA per port. Account for sensor inrush and bias currents.

Software switches the two shared rails on/off and reports their voltage and fault state. It does **not** change a port's voltage selection and cannot read the shunt position. Rail mask: 0=off, 1=5 V, 2=VBAT, 3=both. An erased/unconfigured board starts with both rails off. A stored nonzero rail setting can restore power automatically after ordinary startup.

Do not connect an external power source to a port power pin. For externally powered sensors, remove that port's power shunt, connect common ground and signal, and choose an appropriate bias. The battery switch and reverse-polarity MOSFET do not provide general reverse-current isolation.

## Select input threshold and bias

| Port | Threshold jumper | Bias header |
|---|---|---|
| 1 | JP102 | JP103 |
| 2 | JP202 | JP203 |
| 3 | JP302 | JP303 |

Threshold jumper fitted selects logic mode: target LOW ≤0.8 V and HIGH ≥2.4 V. Jumper removed selects industrial mode: target LOW ≤4 V and HIGH ≥7 V. Voltages between the LOW and HIGH limits have hysteretic/unspecified state. Positive signal range is 0–30 V. This is digital detection, not an analog measurement input; 1.8 V logic is not guaranteed.

Fit at most one bias shunt, horizontally across one row of the 2×3 header:

| Bias row | Bridge | Use |
|---|---|---|
| Top | 1–2 | Pull up through 4.7 kΩ to the port's selected supply; usually industrial NPN/open collector |
| Middle | 3–4 | Pull up through 4.7 kΩ to 3.3 V; suitable for low-leakage logic open drain |
| Bottom | 5–6 | Pull down through 4.7 kΩ; usually PNP sourcing outputs |
| None | Open | Push-pull output or external bias |

For a 10–30 V NPN photoelectric sensor powered by VBAT: select VBAT power, industrial threshold, and top-row bias. For PNP: select VBAT, industrial threshold, and bottom-row bias. For a 5 V push-pull sensor: select 5 V power, logic threshold, and no bias. Check the actual sensor's output type, minimum supply and off-state leakage. Use the software inversion mask if the desired logical meaning is opposite to the electrical level.

Input state is sampled at 1 ms intervals. Pulses shorter than a sampling interval can be missed, and debounce adds delay. The counters follow the firmware sampling/filtering path; they are not hardware edge-capture counters. Choose sensor timing and filtering accordingly.

## CAN and service connection

J2/J3 are electrically parallel for daisy chaining. Use twisted CAN H/L wiring and a short local stub. JP2 adds 120 Ω termination; fit it only at a bus endpoint. With power off, a correctly terminated whole bus usually measures about 60 Ω between H and L.

J8 uses the **standard Tag-Connect TC2050-IDC-NL mechanical footprint with a custom electrical pinout**. A generic 1:1 TC2050 cable needs an adapter wired to this table. It is not the standard ARM Cortex 10-pin mapping.

| J8/cable pin | Board signal | Connect to |
|---|---|---|
| 1 | NRST | Probe reset, optional |
| 2 | UART_RX | 3.3 V UART adapter TX |
| 3 | UART_TX | 3.3 V UART adapter RX |
| 4 | SWCLK | SWD probe clock |
| 5 | SWDIO | SWD probe data |
| 6 | +3V3 | Probe VTref **sense input only** |
| 7 | Ground | Probe ground |
| 8 | Ground | Service ground |
| 9 | BOOT0 | Leave open normally; use only for deliberate bootloader service |
| 10 | Ground | Service ground |

Power the board at J1 during programming. Leave programmer/UART power outputs disconnected. Align the cable using its three guide pins; the contacts have 1.27 mm pitch. UART is 115200 baud, 8N1, 3.3 V logic. Secure the cable with a suitable TC2050 retaining clip or fixture; a bare pogo pattern is not a permanent connector.
