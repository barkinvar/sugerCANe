# Rev H cost and assembly basis

The selected build uses **JLCPCB for 129 SMT placements** and **DigiKey for the user-soldered STM32F042K6T6**. The ten-board parts estimate is **$27.08 per board before SMT attrition**, or about **$27.96** with conservative JLC allowances. Two optional spare MCUs add about **$6.55 per batch**. PCB, factory assembly, inspection, shipping and taxes are additional.

| Ten-board basis | Parts per board |
|---|---:|
| JLC factory parts before attrition | $15.10 |
| User-fitted MCU, ten through-hole parts and three caps | $11.98 |
| Combined before attrition | **$27.08** |
| JLC factory parts including conservative allowance | $15.98 |
| Combined including conservative allowance | **$27.96** |

The earlier all-factory plan used a provisional $2.4981 MCU price despite zero JLC stock. DigiKey's observed ten-piece price is $3.277. Moving U5 to user assembly raises the parts estimate about $0.78 per board, and removes one factory feeder ($1.53 per order at the posted Standard rate). It avoids the separate JLC MCU procurement step. Actual savings in procurement fees or lead time require a quote.

| Boards | Parts purchasing per board before attrition | Lot parts purchasing |
|---|---:|---:|
| 1 | $34.21 | $34.21 |
| 5 | $30.32 | $151.60 |
| 10 | $27.08 | $270.82 |
| 25 | $24.96 | $624.07 |

These figures exclude optional spares and factory charges, and do not establish supported assembly quantities or available stock for every lot. The JLC check covers ten boards. The five/ten-board DigiKey import files include two extra MCUs, so their cart totals differ from the bare BOM arithmetic. Other parts may have minimum packs; see [cost_detail.csv](../bom/cost_detail.csv).

Standard PCBA is required by the exact D10 LED. Posted setup, stencil, 54 loading types and two fixtures total **$132.81 per order**. Placement, X-ray, panel/rails, handling, PCB, freight and tax/duty are extra. The final quote may apply other minimums or fixtures. [JLC fee basis](https://jlcpcb.com/help/article/pcb-assembly-price) · [partial scenarios](../bom/assembly_scenarios.csv).

The board remains 52 × 74 mm, four copper layers, with all parts on top. No protection components or electrical functions were removed by the assembly-scope change. User soldering totals 32 MCU leads and 49 through-hole joints. Reuse one programmer and mapped harness across the batch; [programmer details](STATUS_AND_PROGRAMMING.md).

JLC factory stock was checked September 10, 2026, 03:43 UTC; all 54 types covered ten boards with the displayed allowances. Separate supplier links for the six hand-purchased types were also checked. Prices and availability are observations, not reserved stock or a complete quotation. Final simulations, factory stack/process/inspection confirmation and delivery review remain pending. [Ordering guide](FACTORY_ORDER.md) · [sourcing audit](JLC_SOURCING.md).
