# Status LED, enclosure access and inexpensive programming

Rev H has one RGB LED, D10, in the open area on the right, above the right-hand mounting hole. A silkscreen circle and RGB label identify it. It runs from the internal 5 V supply, so it can indicate a sensor-power fault while the protected outputs are off. Sensor-voltage selection remains on the removable 2 mm jumpers.

## Reading the indicator

| Pattern | Meaning |
|---|---|
| Green, one short pulse per second | Configured, rails qualified, telemetry enabled, and a CAN transmission acknowledged within 500 ms |
| Amber, one short pulse per second | Waiting: unconfigured, startup, maintenance, or telemetry disabled; also the initial CAN connection grace period |
| Red, two short pulses per second | Latched sensor-power fault or clock-start failure; inspect CAN diagnostics and rail measurements |
| Red, equal on/off every 250 ms | CAN initialization/error-passive/bus-off fault, or no successful transmission after the initial one-second grace period |
| Blue, one 200 ms pulse per second | Bootloader, including CAN update/recovery |
| Magenta, rapid 50 ms on/off | Three-second identify request; application power/CAN faults take priority |
| Dark or frozen color | Check board power, reset and firmware; this alone does not prove the outputs are off |

A CAN acknowledgment proves that another node accepted the frame at the bus level; it does not prove the robot application consumed it. Green does not certify sensor type, jumper voltage, robot enable state or healthy external wiring. There are no per-input LEDs. This is SC12's own status scheme and CAN protocol.

## Enclosure location

Coordinates use the component-side view, top-left PCB corner as (0,0). D10 is centered at **X=48 mm, Y=39.5 mm**: 4 mm from the right edge and 7 mm above mounting hole H2. Its nominal body is 1.5 × 1.5 × 0.65 mm. A **6 mm diameter area** centered on D10 is reserved against other component courtyards for a future circular light duct. C75 sits just above this area and remains connected by a short local supply trace.

For a first printed enclosure, use a duct with **6 mm maximum outside diameter and 4 mm inside diameter**. These are nominal starting dimensions, not a tolerance-qualified enclosure. The duct must hang from the case, without loading the PCB or LED. Start its lower face **0.2–0.5 mm above the LED**, or nominally **0.85–1.15 mm above the top PCB surface**. Maintain the separate mounting-hardware clearance at H2; do not combine the duct with a screw boss.

The LED should be visible from above, but brightness and viewing angle have not been measured on hardware. Keep a hollow duct short and its opening unobstructed; a translucent window or light-pipe insert can make the case indicator easier to see from an angle. Check all RGB patterns through the actual print under workshop and competition lighting before finalizing the case. The CAD render shows the package without illumination.

J8 is centered at (24,6.30) mm, with a 12.70 × 5.00 mm insulator and approximately 8.5 mm total height above the PCB. Its tails extend about 1.4 mm beyond a 1.6 mm PCB. Allow access through a removable lid and space for plugged leads during servicing. The completed [STEP model](../output/mechanical/FRC_Sensor_CAN.step) and [mechanical drawing](../output/mechanical/mechanical_drawing.pdf) include both parts. All assembly remains on top.

## One programmer for the ten-board batch

Hand solder the ordinary **2×5, 2.54 mm J8 header** included in the hand-solder BOM. Its estimated purchase price is $0.0718 each at ten. No special pogo cable is required. Keep one short five-wire harness and reuse it across all boards. Disconnect it for robot use.

Use an existing ST-Link with external-target SWD, reset and voltage sensing, or a Nucleo's detachable/external ST-Link according to that specific board's manual. If buying a programmer, the genuine [STLINK-V3MINIE](https://estore.st.com/en/stlink-v3minie-cpn.html) was listed at about **$26 on 2026-09-09**, before shipping/tax and USB cable. That is a one-time bench tool, about $2.60 per board spread over ten, plus a small wire/adapter allowance.

The V3MINIE's CN2 edge pads are **2 mm**, and its supplied ribbon is **1.27 mm STDC14**: neither directly plugs into this 2.54 mm header. Make one mapped adapter, or solder strain-relieved flywires to CN2 following the probe manual. Verify every connection unpowered. Ordinary female 2.54 mm leads fit the SC12 end.

| Signal | SC12 J8 | STLINK-V3MINIE CN2 edge pad | Alternative CN4 STDC14 pin |
|---|---:|---:|---:|
| NRST | 1 | 9 | 12 |
| SWCLK | 4 | 4 | 6 |
| SWDIO | 5 | 3 | 4 |
| 3.3 V target reference, sense only | 6 | 10 | 3 |
| GND | 7 | 6 | 5 |

Use only one probe connector path. CN2 uses pads on both faces; identify positions from [ST UM2910, connector tables and board views](https://www.st.com/resource/en/user_manual/um2910-stlinkv3minie-debuggerprogrammer-tiny-probe-for-stm32-microcontrollers-stmicroelectronics.pdf). J8's full UART/BOOT0 mapping and odd/even orientation are in [WIRING.md](WIRING.md). J8 is a custom signal assignment, not an ARM ribbon-compatible socket.

Power SC12 through J1, with sensor jumper caps removed for first bring-up. Connect J8.6 only to target-voltage sensing; never feed 3.3 V or 5 V from the programmer into it. Leave J8.9 BOOT0 open. With short leads, start SWD at 1 MHz or lower:

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c 'adapter speed 1000' -f tools/program_factory.tcl
```

Run from `current/`. The script programs the matching combined factory image, verifies it, and sets/verifies bootloader write protection. Power cycle and follow [the fixture checks](FIXTURE.md). The first installation needs SWD; later application updates, CAN ID and sensor modes use [CAN service](CAN_SERVICE.md). Bootloader or option-byte recovery still requires SWD. USB-C is needed on the external programmer, not on each SC12 board.

## Circuit and verification basis

PB3 drives an SN74AHCT1G125 buffer, which converts 3.3 V data to the LED's 5 V logic domain. A 10 kΩ pulldown holds its input low on reset; a 330 Ω series resistor and local 100 nF capacitors support the short board-level link. OPSCO SK6805-EC15 uses GRB data at 800 kbit/s. The buffer is necessary because this LED's minimum HIGH level is 0.78 of its supply; directly driving it with 3.3 V would lack guaranteed margin.

The timer/DMA implementation preserves foreground input sampling and CAN service. Compiled firmware tests exercise the emitted data, timing registers, transfer errors, CAN acknowledgment tracking and application status states. They do not measure real LED waveforms, optical brightness, or reset behavior on silicon. Bench-check colors, timing, CAN unplug/recovery, rail faults and boot-to-application transitions before robot use. The LED may hold its last color until the next valid word if the MCU resets or stops.

Sources: [OPSCO SK6805-EC15 A/1 datasheet](https://datasheet.lcsc.com/datasheet/pdf/0f4b58ac8908ccf8037b2d7ca0ec1e91.pdf?productCode=C2890035), [TI SN74AHCT1G125](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf), [STM32F042 datasheet](https://www.st.com/resource/en/datasheet/stm32f042k6.pdf), [ST RM0091](https://www.st.com/resource/en/reference_manual/dm00031936.pdf).
