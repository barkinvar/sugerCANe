# Compact board: JLC package and assembly review

Checked September 10, 2026 against the compact PCB and JLC's exact catalog codes. **No package/land-pattern mismatch requiring a PCB change was found. Factory process approval is still pending.** This review covers all **54 factory MPN types, 129 SMT placements and 22 footprint families**. The eleven user-fitted parts are excluded from the factory scope.

[Machine-readable part-by-part review](../bom/jlc_package_review.json) · [Manufacturer drawing extracts](../sources/datasheets/jlc_package_drawings.pdf) · [Native geometry/CPL checks](../reports/manufacturing/jlc_packages.json) · [Ordering instructions](FACTORY_ORDER.md)

## What was checked

- Live exact JLC MPN identity and package names; all 54 catalog entries match the factory BOM. Availability covered ten boards with the displayed quantity allowances at this observation, without reserving stock.
- Manufacturer package dimensions, lead pitch and land patterns against the actual native pads. Generic KiCad lands can differ from vendor examples while providing correct terminal overlap; those differences are recorded rather than described as exact matches.
- Every factory pad's dimensions and normalized position, pin-to-net mapping to the circuit model, plus all 129 CPL coordinates, sides and rotations against native KiCad.
- Fresh native DRC: **zero violations and zero unconnected items**, including enabled courtyard-overlap and solder-mask-bridge rules. Native board constraints also pass.
- Same-side component/lead envelopes: no overlap; the smallest screened gap is **0.40 mm**, between Q202/Q2 and Q301/Q3. This is an envelope calculation, not a placement-machine/nozzle clearance certification. The fuse envelope is nominal because that drawing does not specify body tolerances.
- The tightest adjacent pad gap is **0.15 mm at U8**, whose lead pitch is **0.65 mm**. Factory stencil/mask review is still required. No factory part has a finer lead pitch.
- The existing factory stencil checker confirms **32 U5 openings omitted**, **127 top + 198 bottom openings retained**, including U9's four center-pad windows.

The circuit, pads, tracks, Gerbers and component positions were not changed by this audit. Existing electrical simulation evidence therefore remains tied to the same hardware. The new check is `kicad-python scripts/check_jlc_packages.py` after sourcing `tools/env.sh`.

## Package details that matter at ordering

| Part | Reviewed fit / ordering detail |
|---|---|
| D10 RGB LED | Exact OPSCO C2890035: 1.5 × 1.5 mm body; four 0.55 × 0.55 mm lands with 0.40 mm gaps. 1=DIN, 2=VDD, 3=DOUT, 4=GND. Current linked drawing is SK6805-EC15-001 A/1; confirm the supplied revision, MSL 4 handling and orientation. |
| U9 eFuse | C2155773's short catalog label “SO-8” means **DDA8 with an exposed pad** here. Native center copper is 2.4 × 3.1 mm; retain four paste windows and ground connection. Require explicit X-ray coverage/report. |
| U8 boost IC | DGK/VSSOP8: 3 × 3 mm body, 0.65 mm pitch. PW/TSSOP is a different package. Native 1.625 × 0.50 mm lands are larger than TI's example; lead overlap is correct. |
| U1 buck IC | DDC thin SOT23, six leads at 0.95 mm pitch. The native TSOT footprint accommodates it. |
| U2 regulator | AP2112K uses SOT25, equivalent to this five-lead SOT23 footprint. Other AP2112 packages do not fit. |
| U4 5 V switch | SOT23-6/DBV; keep **TPS2553DBVR-1**, including the latch-off suffix. |
| U6 / U7 | SOIC8 / SOIC14, 1.27 mm pitch. Do not select the smaller SOT, VSON, WQFN or TSSOP variants. |
| L1 | SRP7028A: pads 2.95 × 3.5 mm, 2.5 mm gap, 8.4 mm overall span match Bourns. |
| L2 | Ordered SRP5030TA; footprint name ends SRP5030T. Pads **2.0 × 1.8 mm, 2.5 mm gap, 6.5 mm span** match the TA drawing. |
| C1 | Standard Panasonic FT size D, 6.3 × 5.8 mm can. Pads **3.2 × 1.6 mm, 1.8 mm gap** match. Pin 1 positive; the can's stripe marks negative. The vibration-proof variant uses a different land pattern. |
| Y1 crystal | ABM3B, 5.0 × 3.2 mm; 1.8 × 1.2 mm lands at 4.0 × 2.4 mm centers. Pins 1/3 are crystal, 2/4 grounded case. Abracon allows the chamfer at pin 1 **or pin 4**; do not use chamfer alone to decide rotation. |
| F1 fuse | 2410 Nano2; 1.96 × 3.15 mm lands and 2.95 mm gap match the drawing within its rounding. |
| Resistors / MLCCs | 0805, 1206 and 1210 dimensions were checked by manufacturer family; all use the correct case size. C2 is a relatively tall 1210, **2.50 ±0.20 mm** before solder stand-off. |
| Diodes / MOSFETs | SMA, SMB, SOD123, SOT23 and SOIC8 variants fit. Diode pad 1 is cathode. AOS SOT23 has a different lead span from some other makers; the current lands still cover it. |

D10's `xrayFlag=false` catalog field means it is **not currently flagged for automatic X-ray**, not that its underside joints become visible. The order notes request inspection coverage separately. Changing D10 would not remove U9's exposed-pad inspection request. A reviewed alternative, [WS2812B-MINI-V3/W C527089](https://jlcpcb.com/partdetail/C527089), has exposed side terminals, a roughly 3.5 mm body and a different footprint/pin numbering (1=VDD, 2=DOUT, 3=GND, 4=DIN). It is **not fitted or an approved substitution**. At the September 10 catalog check it was $0.1134 versus $0.0993 for the fitted LED at quantity 1–49; both had `xrayFlag=false`. The SK6812MINI-E alternative was rejected because it is a reverse-mount package requiring a board opening. A different LED must also have its timing, current and moisture/reflow requirements checked before substitution; the factory determines final inspection and pricing.

## Required factory confirmations

1. **Both sides**, 50 top and 79 bottom. The outdated “top side only” assembly-plan field and old finished-board count were corrected; the finished board is 61 top + 79 bottom.
2. The 44 × 48 mm board needs a factory panel of at least **70 × 70 mm**, with rails and fiducials, then depanelization. These are Standard PCBA requirements; five-millimetre rails alone do not make this small board large enough. [JLC capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).
3. Review actual BOM/CPL previews against the assembly PDFs. Native rotations are internally consistent; JLC's library zero-angle and bottom-view conventions still need confirmation. Pay particular attention to D10, Y1, C1, IC pin 1 and diode cathode bars.
4. Confirm two-pass reflow and retention of underside L1/L2/F1. C1 permits at most two cycles with strict dwell limits. F1 and Bourns publish example profiles different from JLC's nominal Standard peak; the factory must qualify a compatible process rather than treating a peak-temperature comparison as a complete recipe. Keep the exact LED's moisture/reflow instructions with the order.
5. Confirm U9's thermal-pad soldering, paste volume and X-ray, plus D10/Y1 hidden-joint inspection. The public catalog currently has `xrayFlag=false` for U9, D10 and Y1; do not assume hidden-joint inspection is automatically included. Confirm the four-layer copper/stack requirements already in the order guide.

The order packet stays **REVIEW_ONLY** until those factory questions are closed. This is a dimensional and assembly-file review, not a promise of defect-free manufacture or a substitute for testing assembled prototypes.

<details>
<summary>All 54 exact factory parts and drawing evidence</summary>

| References | Exact MPN | JLC | Native footprint | Drawing bundle pages |
|---|---|---|---|---|
| F1 | 0451003.MRL | [C13982](https://jlcpcb.com/partdetail/C13982) | Fuse_Littelfuse-NANO2-451_453 | 1, 2 |
| R4, R110, R210, R310 | 0805W8F1001T5E | [C17513](https://jlcpcb.com/partdetail/C17513) | R_0805_2012Metric | 3, 4 |
| R3, R21, R22, R40, R41, R105, R205, R305, R52, R71, R75, R31 | 0805W8F1002T5E | [C17414](https://jlcpcb.com/partdetail/C17414) | R_0805_2012Metric | 3, 4 |
| R50, R111, R112, R211, R212, R311, R312, R70 | 0805W8F1003T5E | [C149504](https://jlcpcb.com/partdetail/C149504) | R_0805_2012Metric | 3, 4 |
| R30 | 0805W8F3300T5E | [C17630](https://jlcpcb.com/partdetail/C17630) | R_0805_2012Metric | 3, 4 |
| Y1 | ABM3B-8.000MHZ-B2-T | [C83312](https://jlcpcb.com/partdetail/C83312) | Abracon_ABM3B_5.0x3.2mm | 13 |
| Q101, Q201, Q301 | AO3401A | [C15127](https://jlcpcb.com/partdetail/C15127) | SOT-23 | 14 |
| Q1 | AO4485 | [C51499](https://jlcpcb.com/partdetail/C51499) | SOIC-8_3.9x4.9mm_P1.27mm | 15 |
| U2 | AP2112K-3.3TRG1 | [C51118](https://jlcpcb.com/partdetail/C51118) | SOT-23-5 | 16 |
| D4, D5 | B240A-13-F | [C92506](https://jlcpcb.com/partdetail/C92506) | D_SMA | 17 |
| D102, D202, D302 | BAT46W-E3-18 | [C5557780](https://jlcpcb.com/partdetail/C5557780) | D_SOD-123 | 18 |
| Q102, Q202, Q302, Q2, Q3 | BSS138BK,215 | [C282529](https://jlcpcb.com/partdetail/C282529) | SOT-23 | 19 |
| C25, C26 | CC0805JRNPO9BN200 | [C105173](https://jlcpcb.com/partdetail/C105173) | C_0805_2012Metric | 7 |
| C101, C201, C301 | CC0805JRNPO9BN102 | [C62774](https://jlcpcb.com/partdetail/C62774) | C_0805_2012Metric | 7 |
| C69 | CC0805KRX7R9BB333 | [C107150](https://jlcpcb.com/partdetail/C107150) | C_0805_2012Metric | 8 |
| C72, C73 | CL21B103KBANNNC | [C1710](https://jlcpcb.com/partdetail/C1710) | C_0805_2012Metric | 9 |
| C3, C6, C11, C20, C21, C22, C27, C40, C41, C50, C51, C66, C74, C75 | CL21B104KCFNNNE | [C28233](https://jlcpcb.com/partdetail/C28233) | C_0805_2012Metric | 9 |
| C7, C23, C61, C65, C71 | CL21B105KBFNNNE | [C28323](https://jlcpcb.com/partdetail/C28323) | C_0805_2012Metric | 9 |
| C70 | CL21B473KBCNNNC | [C53134](https://jlcpcb.com/partdetail/C53134) | C_0805_2012Metric | 9 |
| C8, C24 | CL21B475KAFNNNE | [C98195](https://jlcpcb.com/partdetail/C98195) | C_0805_2012Metric | 9 |
| C4, C5, C13, C12, C60, C62, C63, C64 | CL31A226KAHNNNE | [C12891](https://jlcpcb.com/partdetail/C12891) | C_1206_3216Metric | 9 |
| C2 | CL32B106KBJNNWE | [C3844168](https://jlcpcb.com/partdetail/C3844168) | C_1210_3225Metric | 10 |
| C1 | EEEFT1H470AP | [C92059](https://jlcpcb.com/partdetail/C92059) | CP_Panasonic_FT_6.3x5.8 | 11, 12 |
| D20 | ESD2CAN24DBZRQ1 | [C5736151](https://jlcpcb.com/partdetail/C5736151) | SOT-23 | 20, 21 |
| U7 | LM339LVDR | [C22427665](https://jlcpcb.com/partdetail/C22427665) | SOIC-14_3.9x8.7mm_P1.27mm | 22, 23 |
| U1 | LMR51430XDDCR | [C5185863](https://jlcpcb.com/partdetail/C5185863) | TSOT-23-6 | 24, 25, 26 |
| D3 | MMSZ12T1G | [C72599](https://jlcpcb.com/partdetail/C72599) | D_SOD-123 | 27 |
| R61 | 0805W8F1152T5E | [C17418](https://jlcpcb.com/partdetail/C17418) | R_0805_2012Metric | 3, 4 |
| R63 | RC0805FR-0713KL | [C137592](https://jlcpcb.com/partdetail/C137592) | R_0805_2012Metric | 5 |
| R103, R203, R303 | RC0805FR-0720KL | [C114566](https://jlcpcb.com/partdetail/C114566) | R_0805_2012Metric | 5 |
| R101, R201, R301 | 0805W8F2203T5E | [C17556](https://jlcpcb.com/partdetail/C17556) | R_0805_2012Metric | 3, 4 |
| R62 | RC0805FR-072K61L | [C273965](https://jlcpcb.com/partdetail/C273965) | R_0805_2012Metric | 5 |
| R104, R204, R304 | RC0805FR-072M2L | [C137552](https://jlcpcb.com/partdetail/C137552) | R_0805_2012Metric | 5 |
| R10 | 0805W8F5902T5E | [C17763](https://jlcpcb.com/partdetail/C17763) | R_0805_2012Metric | 3, 4 |
| R51 | 0805W8F5231T5E | [C17739](https://jlcpcb.com/partdetail/C17739) | R_0805_2012Metric | 3, 4 |
| R20 | RC0805JR-070RL | [C96345](https://jlcpcb.com/partdetail/C96345) | R_0805_2012Metric | 5 |
| R109, R209, R309 | RC1206FR-0710KL | [C132649](https://jlcpcb.com/partdetail/C132649) | R_1206_3216Metric | 5 |
| R42 | 1206W4F1200T5E | [C17909](https://jlcpcb.com/partdetail/C17909) | R_1206_3216Metric | 3, 4 |
| R60, R65, R66, R68, R72, R73 | RT0805BRD07100KL | [C122537](https://jlcpcb.com/partdetail/C122537) | R_0805_2012Metric | 6 |
| R1 | RT0805BRD07102KL | [C865126](https://jlcpcb.com/partdetail/C865126) | R_0805_2012Metric | 6 |
| R69 | RT0805BRD0712K1L | [C865169](https://jlcpcb.com/partdetail/C865169) | R_0805_2012Metric | 6 |
| R2 | RT0805BRD0713K7L | [C865183](https://jlcpcb.com/partdetail/C865183) | R_0805_2012Metric | 6 |
| R67, R74 | RT0805BRD0720KL | [C469660](https://jlcpcb.com/partdetail/C469660) | R_0805_2012Metric | 6 |
| D10 | SK6805-EC15 | [C2890035](https://jlcpcb.com/partdetail/C2890035) | LED_SK6805_EC15 | 28, 29 |
| D6 | SMAJ13A-13-F | [C110519](https://jlcpcb.com/partdetail/C110519) | D_SMA | 30 |
| D101, D201, D301 | SMAJ30A | [C148230](https://jlcpcb.com/partdetail/C148230) | D_SMA | 31 |
| D2 | SMBJ22A-E3/52 | [C3698580](https://jlcpcb.com/partdetail/C3698580) | D_SMB | 32 |
| U10 | SN74AHCT1G125DBVR | [C7484](https://jlcpcb.com/partdetail/C7484) | SOT-23-5 | 33 |
| L2 | SRP5030TA-3R3M | [C2042118](https://jlcpcb.com/partdetail/C2042118) | L_Bourns_SRP5030T | 34 |
| L1 | SRP7028A-8R2M | [C2041815](https://jlcpcb.com/partdetail/C2041815) | L_Bourns_SRP7028A_7.3x6.6mm | 35 |
| U6 | TCAN3413DR | [C22433320](https://jlcpcb.com/partdetail/C22433320) | SOIC-8_3.9x4.9mm_P1.27mm | 36, 37 |
| U4 | TPS2553DBVR-1 | [C111738](https://jlcpcb.com/partdetail/C111738) | SOT-23-6 | 38, 39 |
| U9 | TPS259620DDAR | [C2155773](https://jlcpcb.com/partdetail/C2155773) | TPS2596_DDA8 | 40, 41, 42, 43 |
| U8 | TPS61085DGKR | [C113659](https://jlcpcb.com/partdetail/C113659) | VSSOP-8_3x3mm_P0.65mm | 44, 45, 46 |

</details>
