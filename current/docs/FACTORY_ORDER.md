# Order and build sugarCANe Rev H

**Selected build: JLCPCB assembles 129 top-side SMT parts. You buy the original STM32F042K6T6 from DigiKey and solder U5, then fit the ten through-hole parts and three jumper caps.** The MCU footprint, four-layer layout and firmware stay the same. The final component review changed C25/C26 to **20 pF / C105173** for crystal startup margin, and U1/L1 to **LMR51430XDDCR / C5185863** plus **SRP7028A-8R2M / C2041815** for buck current headroom. All four use the existing footprints.

**Before paying for PCBA:** finish our final simulation review. The saved full startup simulation is incomplete; the available ZIPs remain marked REVIEW_ONLY. The assembly choice is finalized, but this is not an electrical release. Use the files now to obtain and review a quotation. [Current evidence](ORDER_READINESS.md).

## 1. Buy the parts you will fit

Order the MCU, terminals, voltage headers and caps from **DigiKey**. Order the recessed programming socket from **LCSC**. Ship both orders to yourself in the USA. Do not send the MCU to JLC or start a JLC Global Sourcing order.

| Part / supplier link | Where it goes | For 5 boards | For 10 boards |
|---|---|---:|---:|
| [STM32F042K6T6, DigiKey 497-14647-ND](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F042K6T6/4815294) | U5 MCU | **7 recommended** | **12 recommended** |
| [Weidmüller 1824420000, 281-2020-ND](https://www.digikey.com/en/products/detail/weidm%C3%BCller/1824420000/1094358) | J1–J3, two-pole terminals | 15 | 30 |
| [Weidmüller 1824430000, 281-2021-ND](https://www.digikey.com/en/products/detail/weidm%C3%BCller/1824430000/1094359) | J4–J6, three-pole terminals | 15 | 30 |
| [Harwin M22-2010305, 952-2274-ND](https://www.digikey.com/en/products/detail/harwin-inc/M22-2010305/3728238) | Three 2 mm voltage headers | 15 | 30 |
| [Sullins SPN02SVEN-RC, S9340-ND](https://www.digikey.com/en/products/detail/sullins-connector-solutions/SPN02SVEN-RC/2618265) | Three 2 mm jumper caps | 15 | 30 |
| [XFCN PM254V-12-10P-H85, LCSC C492399](https://www.lcsc.com/product-detail/C492399.html) | J8 recessed 2×5 / 2.54 mm socket | 5 | 10 |

MCU quantities include **two spare chips**; each board needs one. Other quantities are exact requirements before spares. Use the [five-board DigiKey import](../bom/DigiKey_5_boards.csv) or [ten-board import](../bom/DigiKey_10_boards.csv); both include two spare MCUs. J8 is a separate LCSC purchase. Check each cart's quantity, manufacturer and delivery date.

Buy **K6T6 / LQFP32**, 7 × 7 mm body with visible 0.8 mm-pitch legs. **K6U6TR / QFN does not fit this PCB.** DigiKey displayed 3,071 K6T6 in stock and $3.277 each at 10+ on September 10, 2026 UTC; twelve cost about $39.32 before shipping, tax and cart charges. Its 40-week manufacturer replenishment field is separate from stocked inventory. Stock is not reserved.

Reuse one compatible ST-Link and a mapped five-wire harness. If you need a probe, see the [STLINK-V3MINIE and adapter instructions](STATUS_AND_PROGRAMMING.md#one-programmer-for-the-ten-board-batch). J8 has a custom pinout; an ordinary ARM ribbon cannot plug in directly. Have a temperature-controlled iron, fine solder, flux, tweezers, wick, magnification, multimeter and current-limited bench supply.

## 2. Download the matching JLC files

Extract [sugarCANe_RevH_JLC_REVIEW_ONLY.zip](../order/sugarCANe_RevH_JLC_REVIEW_ONLY.zip). Do not upload the whole documentation packet as the Gerber file. Use these three files from that same packet:

| JLC upload field | File |
|---|---|
| PCB Gerber upload | `order/sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip` |
| BOM | `bom/BOM_JLCPCB.csv` |
| CPL / pick-and-place | `output/assembly/CPL_JLCPCB.csv` |

The BOM contains **54 types / 129 placements**; the CPL contains **129 rows**. **U5 is absent from both.** The Gerber ZIP has a factory-specific top paste layer with all **32 U5 apertures removed**. The other 325 apertures, including U9's exposed-pad windows, are preserved. Copper, solder mask and drills remain the checked native design. Ask CAM to use the supplied stencil geometry without recreating U5 openings.

The complete BOM, assembly drawing and 3D renders show the **finished board, including your MCU and connectors**. They are reference material, not instructions to add factory placements. Do not upload `BOM_grouped.csv`, `positions_all_top.csv` or `positions_smd_top.csv` as the JLC assembly selection.

## 3. Configure JLCPCB

Start at [JLCPCB PCB quotation](https://jlcpcb.com/quote), upload the Gerber ZIP, and choose PCB assembly. Interface labels can change; use these requirements:

| Setting | Select / require |
|---|---|
| Finished quantity | Your chosen **5 or 10 assembled boards**; match PCB and assembly quantities |
| PCB | **52 × 74 mm**, **four layers**, FR-4, **1.6 mm** |
| Copper | **1 oz / 35 µm nominal on all four layers**, including both inner layers |
| Finish | **ENIG** |
| Mask / silk | Green mask, white silkscreen on both sides; retain bottom artwork |
| Assembly | **Standard PCBA, top side only**, 129 placements |
| Panel / rails | Factory adds rails/fiducials and returns separated 52 × 74 mm boards |
| Electrical test | Confirm bare-PCB open/short electrical test |
| Stencil | Top only, nominal **0.10 mm**, supplied apertures; **no paste at U5** |
| Programming / functional test | You perform these after installing U5 |

D10's exact RGB LED requires Standard PCBA. Do not select Economic. The board is narrower than the published Standard minimum; have JLC confirm its panel/rail arrangement. Default rails alone must not be assumed to satisfy it. Request a symmetric four-layer stack with outer-to-inner dielectric ≤0.25 mm and 35 µm copper on every layer; do not accept 0.5 oz inner copper without another electrical review.

Upload and process BOM/CPL. **All 54 listed MPNs must be selected**, with no unexpected shortfall or unmatched parts. U5 and the ten through-hole parts are intentionally omitted; every other SMT part must be present, including C1, D10 and U9. Advancing past an unmatched part can omit it from assembly. [Official matching guidance](https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders).

Inspect the placement preview against [top_assembly.pdf](../output/assembly/top_assembly.pdf), particularly IC pin 1 and diode/capacitor polarity. CPL coordinates are millimetres from PCB lower-left, X right and Y up, with native KiCad counterclockwise rotation. The factory must reconcile its part-library orientations; do not guess a blanket 90° correction.

## 4. Copy these notes into the PCBA order

> sugarCANe SC12 Rev H. TOP assembly only: 129 placements / 54 exact MPN types from the supplied BOM/CPL. Leave U5 (STM32F042K6T6) unpopulated and unpasted; customer hand solders it. Use the supplied F_Paste Gerber with U5 apertures removed. Leave J1–J6, J8 and JP101/JP201/JP301 unpopulated; leave JP2 termination bridge open. No part substitutions or added placements. Fit C1, D10 and every other BOM/CPL reference. U1 is LMR51430XDDCR; L1 is SRP7028A-8R2M (8.2 uH). X-ray U9 TPS259620DDAR's exposed ground/thermal pad on every board and provide the report; confirm D10 underside-joint inspection coverage. Confirm 35 µm copper on ALL FOUR layers, symmetric 1.6 mm stack, outer-to-inner dielectric ≤0.25 mm, Standard-PCBA panel/rails and depanelization to 52 × 74 mm. Confirm component-compatible reflow/moisture handling, including D10 MSL 4 and C1 limits below. No firmware programming or powered functional test requested; U5 is absent. Confirm production and tracked express delivery timing to the USA before payment.

**C1 reflow limits:** Panasonic EEEFT1H470AP, profile (5): case-top peak ≤260°C; at/above 250°C ≤5 s, 230°C ≤30 s, 217°C ≤40 s and 200°C ≤70 s; at most two cycles. D10 is exact OPSCO SK6805-EC15; U8 is TPS61085DGKR; U4 is **TPS2553DBVR-1**; U9 is TPS259620DDAR. The `-1` latch-off suffix is required. Confirm the factory process and any X-ray charges in the quotation. [Process evidence](JLC_SOURCING.md#solder-process-audit) · [JLC targeted X-ray requests](https://jlcpcb.com/help/article/x-ray-inspection-report-interpretation-guide).

## 5. Review the quote and delivery before paying

1. Finish the final electrical simulation review and issue the approved manufacturing package; do not pay against the current REVIEW_ONLY release.
2. Verify quantities, all 54 selected types, U5/stencil omission, stack and component orientations. Files do not reserve inventory.
3. Obtain confirmation of reflow handling, panelization and U9/D10 inspection. Review any CAM changes before acceptance.
4. Check the **complete** price: PCB, parts, assembly/setup/stencil, panel/rails, X-ray, packing, express freight and tax/duty. Ten-board parts are about **$27.96 per board** with conservative JLC attrition and your MCU, before two optional spare MCUs and those additional charges. This is not a final assembled-board price.
5. Your last arrival date is **October 10, 2026, USA**. Use October 9 as the practical delivery target. Request a dispatch estimate and destination-specific tracked express quote; allow time for soldering/testing. Chinese holiday closures and customs can affect timing. Displayed production duration is not the arrival date. Order the separate DigiKey/LCSC parts in time too.

JLC public stock covers all **54 factory types for ten boards**, including displayed allowances, in the September 10, 2026, 03:43–05:13 UTC checks. U9 has 25 available and L2 has 39, so recheck at checkout. Allocation and delivery are unconfirmed. [Full audit](../reports/manufacturing/jlc_sourcing.json).

## 6. Finish the delivered boards

Start with one board. Inspect it unpowered, then solder **U5 before the tall connectors** so you can access its legs. Use the [MCU orientation map](../output/documentation/MCU_hand_solder_map.pdf) and [assembly procedure](ASSEMBLY.md).

Use **flux and a soldering iron**: align pin 1, tack opposite corner leads, recheck alignment, solder the remaining leads, and wick any bridges. This LQFP has no hidden central joint. Avoid prolonged repeated heating; clean and inspect all 32 leads under magnification. A full-board stencil cannot sit over fitted components. Your hot plate is optional rework equipment; this plan does not require reheating the factory-fitted LED and capacitor.

Fit terminals, service socket and voltage headers. Keep all caps removed and JP2 open. Check for bridges and supply shorts, then follow the [current-limited fixture procedure](FIXTURE.md). A blank MCU will not provide normal status or sensor-power operation yet.

Program the matching combined `firmware/build/factory.hex` over SWD; it includes bootloader and application. From `current/`, with OpenOCD installed and the [verified J8 wiring](STATUS_AND_PROGRAMMING.md#one-programmer-for-the-ten-board-batch):

```sh
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c 'adapter speed 1000' -f tools/program_factory.tcl
```

Power through J1. J8.6 is **target-voltage sense only**; never feed power from the probe into it. Verify programming/protection, power-cycle and set a unique CAN ID. With power disconnected, select each port's voltage: **pins 1–2 = 5 V; pins 2–3 = 12 V; no cap = disconnected sensor supply**. The middle pin is sensor-power output, not ground. Bridge JP2 only at a CAN bus end to connect the existing 120 Ω resistor; do not add a second resistor there.

Complete [first-board acceptance](VALIDATION.md) with a known load before connecting sensors or a robot harness, then repeat recorded checks for the batch. Initial programming needs SWD; later application updates and settings can use CAN.

[Printable guide](../output/documentation/ORDER_GUIDE.pdf) · [Factory package](../order/README.md) · [Hand-solder BOM](../bom/Hand_solder_BOM.csv)
