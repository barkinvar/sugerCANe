# Rev B-2 local libraries

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

The native PCB is authoritative. Project-local copies of KiCad assets retain the KiCad library license and recorded provenance. Horizontal /90 Weidmüller 1824420000 and 1824430000 footprints use 3.5 mm pitch, two legs per pole, 7 mm row spacing and 1.1 mm drills. The larger tabulated 14.75 mm depth is reserved.

The horizontal connector STEP models now use official manufacturer geometry, translated to the existing PCB origins and assigned project display colors. Original vendor files are retained in `3d/vendor/`; [vendor_connectors.json](3d/vendor_connectors.json) records hashes, URLs and alignment checks. These assets remain Weidmüller material; no project license is applied to them. Other custom models remain nominal envelopes with their original provenance. Older /135 assets are unused by the current PCB.

See [connector verification](../../docs/CONNECTORS.md). Check physical sample fit before committing to volume assembly.
