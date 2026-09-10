# Rev H source and release status

The maintained source is in [current/](../README.md), with native CAD, firmware, manufacturing exports, the [handbook](../output/documentation/SC12_RevH_Handbook.pdf) and [check summary](../reports/release_checks.json).

The [JLC sourcing candidate](../docs/JLC_SOURCING.md) has matched BOM/CPL and a [review-only package](../order/README.md). The 44 × 48 mm compact board has updated native CAD, renders and manufacturing exports. All nine power transient cases and required timestep/solver repeats completed without interrupting the original checkout. The saved evidence is hash-verified; routed-copper, input and firmware checks are refreshed for this layout. U5 is assigned to user purchase and hand soldering from DigiKey, and C25/C26 now use 20 pF.

No full-validation release ZIP is published for H. Full-release packaging remains blocked by the factory process and sourcing holds recorded in the current check summary; no approved manufacturing release is claimed. Prior released ZIPs remain unchanged in the [archive](../../archive/README.md).
