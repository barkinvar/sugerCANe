# Rev H source and release status

The maintained source is in [current/](../README.md), with native CAD, firmware, manufacturing exports, the [handbook](../output/documentation/SC12_RevH_Handbook.pdf) and [check summary](../reports/release_checks.json).

The [JLC sourcing candidate](../docs/JLC_SOURCING.md) has matched BOM/CPL and a [review-only package](../order/README.md). Final power, input, firmware and PCB checks pass, including both complete 40 ms startup traces. U5 is assigned to user purchase and hand soldering from DigiKey. C25/C26 use 20 pF; U1/L1 use LMR51430XDDCR and SRP7028A-8R2M for current headroom.

No full-validation release ZIP is published for H. Power evidence is complete; full-release packaging remains blocked by unconfirmed factory solder-process qualification. Stack and inspection confirmation and quotation also remain order prerequisites. Prior released ZIPs remain unchanged in the [archive](../../archive/README.md).
