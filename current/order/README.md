# Rev H manual-MCU order package

**Read [where to buy and how to order](../docs/FACTORY_ORDER.md) first.** The assembly plan is fixed: JLC fits 129 top SMT parts / 54 types; you buy STM32F042K6T6 from DigiKey and hand solder U5, ten through-hole parts and three caps. U5 is omitted from BOM, CPL and factory stencil.

**Engineering screens pass; review/quotation only until factory confirmation.** Nine power cases, both complete startup traces, ten input cases, firmware checks and all-four-layer CAD/connectivity checks pass. Factory stack/process/inspection and quote remain unconfirmed; no physical board has been tested.

| Download | Use |
|---|---|
| [sugarCANe_RevH_JLC_REVIEW_ONLY.zip](sugarCANe_RevH_JLC_REVIEW_ONLY.zip) | Extract this: matched BOM/CPL, Gerber ZIP, guide, manual shopping lists and drawings |
| [sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip](sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip) | JLC Gerber upload for quotation; factory top paste omits U5 |
| [Printable ordering guide](../output/documentation/ORDER_GUIDE.pdf) | Settings, buying links, order notes and first-board procedure |

Do not upload the whole documentation package into the Gerber field. Complete-board CAD, drawings and renders include U5 because the finished product needs it; factory scope comes from the supplied BOM/CPL. Other paste geometry and all copper/drills/mask are unchanged. [Stencil verification](../reports/manufacturing/factory_stencil.json).

All 54 factory types had stock for ten boards at the latest check; nothing is reserved. No manufacture order has been placed. The user reviews the final electrical results and factory quote before paying. [Evidence](../reports/release_checks.json) · [Historical packages](../../archive/README.md).
