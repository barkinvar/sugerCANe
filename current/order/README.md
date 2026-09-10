# Rev H JLC review package

**Review/quotation only. Do not authorize manufacture from this candidate.** Six passive types have been replaced with equal-rated JLC-listed parts. All 55 SMT types have codes; U5 still needs sourcing. D10 requires Standard PCBA. C1 now uses the reviewed high-reflow capacitor and footprint, resolving the earlier peak conflict. New simulations wait for user approval. [Substitutions and plan](../docs/JLC_SOURCING.md) · [current check summary](../reports/release_checks.json).

| Download | Use |
|---|---|
| [sugarCANe_RevH_JLC_REVIEW_ONLY.zip](sugarCANe_RevH_JLC_REVIEW_ONLY.zip) | Matched BOM/CPL, fabrication ZIP, assembly drawing and review instructions |
| [sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip](sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip) | Four-layer fabrication upload for quotation |

JLC fits 130 top SMT parts. The ten through-hole parts and three loose caps remain user-fitted. The package includes file hashes; it does not reserve parts, confirm a quotation or constitute an engineering release.

C1 is updated; use the [ordering sequence](../docs/FACTORY_ORDER.md#ordering-sequence) to arrange factory-installed U5 through Global Sourcing. After approval, rerun the simulations, resolve the incomplete combined startup and confirm MCU allocation, factory dwell/profile limits and the stack. Issue the final order package only after reviewing those results. The user then orders. Full-release packaging also rejects unresolved sourcing or factory-process holds.

[Factory instructions](../docs/FACTORY_ORDER.md) · [Historical packages](../../archive/README.md). Archived G packages do not contain H's LED/header and must not be mixed with H firmware.
