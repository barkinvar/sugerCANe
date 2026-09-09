# Cost-reduction implementation status

The approved work is implemented in **[Rev F](current/README.md)**. Voltage selection remains removable jumpers; all components remain on top. Existing terminals and software input modes are retained.

| Requested item | Implemented result |
|---|---|
| 2. Protected 12 V from internal 5 V | TPS61085 boost with TPS2553DBVR-1 input fault disconnect; about $6.66/board saving at ten boards, including shared-part price breaks |
| 3. Other passive sourcing | Three unchanged filter caps resourced and four equivalent capacitors substituted; about $1.30/board saving |
| 4. Smaller PCB | 52 × 70 → 52 × 64 mm, 8.6% area reduction; four copper layers, top-side assembly |
| Clearer GitHub | One `current/` project; historical packages in `archive/`; obsolete expanded revisions, experiments and unused library/vendor files removed |

Parts purchasing is approximately **$47.80 / $30.93 / $27.17 / $24.98 per board** for quantities 1 / 5 / 10 / 25. The ten-board saving is about $8 per board against E. PCB, assembly, freight, taxes, attrition and programming/testing are extra. Area reduction does not guarantee a lower minimum PCB price.

[Detailed arithmetic and substitutions](current/docs/COST_REDUCTION.md) · [factory quote package](current/docs/FACTORY_ORDER.md) · [engineering evidence and physical qualification](current/docs/VALIDATION.md).

Remaining external work: prototype assembly and electrical/mechanical qualification, then a confirmed factory quote, stock allocation and destination-specific delivery estimate. No order, factory contact or one-month delivery commitment has been made.
