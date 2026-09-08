# Rev B-2 China assembly budget

These are USD engineering estimates dated 2026-09-08, not a submitted quotation. The PCB has not been physically qualified. Pricing assumes full SMT and through-hole assembly, ENIG, bagged shunts and ordinary international shipping; destination taxes and tariffs are excluded.

JLCPCB publishes a minimum of **two assembled boards**. If you only need one, the first realistic JLCPCB order still pays for two. The one-board row in the CSV is hypothetical and must not be treated as an available service. PCBWay's current capability page publishes a five-piece minimum.

| Assembled boards | Estimated order total | Approx. per board |
|---:|---:|---:|
| 2 | $300–390 | $151–194 |
| 5 | $435–535 | $87–107 |
| 10 | $665–800 | $67–80 |
| 25 | $1380–1630 | $55–65 |

The component-only consumed comparison is **$46.35 per board versus Rev B's $59.30**, about 22% lower on the stated first-tier basis. This comparison does not include MOQ leftovers or assembly. It combines cheaper equivalents with cheaper procurement of identical parts; it is not a $46 finished-board price.

The order model uses dated per-line prices and MOQ rounding, then adds the published JLCPCB Standard setup/stencil/feeder and solder-joint rates. It conservatively budgets feeder fees for all 50 fitted part types. Other costs are explicit allowances: ENIG boards/panel rails, attrition, procurement handling/inbound freight, inspection and international shipping. The factory's actual sourcing quote may differ considerably. LCSC inventory is not JLCPCB assembly inventory.

Factory programming and simple no-load checks are optional and additional: budget **$50–100 setup plus $3–5 per board**, including an allowance for the custom SWD adapter. The archive supplies the firmware and wiring. Full sensor/CAN/load testing, a repeatable production fixture and qualification are separate work.

At prototype quantities, this is not yet a cost-competitive retail product. The 50 fitted part types, premium connectors and supplier setup costs dominate; reducing capacitors alone does little. A further cost revision should consolidate functional circuits and selectors after this prototype is measured.

See `bom/cost_estimate.csv` for every allowance and `bom/procurement_quantities.csv` for exact modeled purchase quantities, leftover parts and price breaks.

Sources: [JLCPCB assembly fees](https://jlcpcb.com/help/article/pcb-assembly-price), [JLCPCB prototype minimum](https://jlcpcb.com/solutions/pcb-prototype-assembly), [PCBWay minimum](https://www.pcbway.com/assembly-capabilities.html). Component source URLs and observation dates are in the BOM.
