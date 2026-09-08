# Rev B-2 sourcing

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Use [BOM_turnkey.csv](../bom/BOM_turnkey.csv) for a complete factory quotation. It includes exact manufacturer/MPN, per-board quantities, source IDs and observation dates. There are 50 fitted MPN groups plus one loose-shunt group.

The [JLCPCB BOM](../bom/BOM_JLCPCB.csv) is a matching/import aid. Empty catalog IDs require global procurement; they are not omissions. STM32F042K6T6 was out of stock at LCSC; its DigiKey code is supplied. The six exact horizontal Weidmüller connectors also need factory sourcing. Confirm all 144 fitted references and ten shunts before ordering.

LCSC and JLCPCB stock are separate. No factory allocation, feeder classification, lead time or price is guaranteed by these files. No supplier has been contacted and no order has been submitted.

See [part changes](PART_CHANGES.md), [full factory instructions](FACTORY_ORDER.md) and [cost assumptions](COST.md). Rev B's DigiKey-only purchasing files are not the ordering BOM for B-2.
