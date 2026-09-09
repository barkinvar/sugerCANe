# Cost decisions and current design

The maintained design is **[Rev H](current/README.md)**. The user chose to keep removable physical 5 V/12 V jumpers and top-side assembly. Software voltage selection is canceled; it is not implemented or awaiting a decision.

| Change | Result |
|---|---|
| Generate 12 V from internal 5 V | F replaced the former buck-boost with TPS61085; approximately $6.66/board saved at ten, including shared-part purchasing effects |
| Passive sourcing | Equivalent substitutions/resourcing saved approximately $1.30/board |
| Repair startup and short behavior | G added output eFuse, default-off control, CAN reset and rail measurement; approximately $1.64/board added |
| Status and initial programming | H adds one buffered RGB LED and an ordinary hand-fitted service header; approximately $0.13/board in parts added versus G |
| Assembly | Keep all parts on top; hand solder ten large through-hole parts, including J8 |
| Repository | One maintained `current/` project; immutable earlier ZIPs in `archive/` |

At ten boards, parts purchasing is **$35.14 for E, $27.17 for F, $28.81 for G and $28.94 for H** per board. H retains approximately $6.19 of savings versus E. PCB, assembly, attrition, programming/test, freight and tax are extra. The RGB implementation adds two SMT part types, so the parts difference alone understates the assembled-price increment.

The canceled software selector would require three source switches plus reset inhibition, control I/O, discharge/verification and an independent voltage permission mechanism to prevent a valid but incorrect 12 V command from damaging a 5 V sensor. Existing shared-rail current limiters do not provide that voltage ceiling. Keeping the jumpers avoids that complexity and cost.

A double-sided layout is only a rough alternative estimate: **15–25% smaller area**, with a target near **52 × 60 mm** instead of 52 × 74 mm. Budget **$3–6 extra per board at ten** assuming Standard assembly for both options; extra setup and stencil alone are about $3.38/board. No double-sided layout or quotation has been produced. [Detailed cost assumptions](current/docs/COST_REDUCTION.md).

One reusable ST-Link and a five-wire header harness program the entire batch; future application updates use CAN. [Programming options](current/docs/STATUS_AND_PROGRAMMING.md). [Factory scope](current/docs/FACTORY_ORDER.md) · [engineering and physical qualification](current/docs/VALIDATION.md). No supplier has been contacted or order placed; a one-month arrival date needs an actual destination-specific quotation.
