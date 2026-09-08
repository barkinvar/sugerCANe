**Revision A prototype fabrication package**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Use the supplied Gerber X2 files and separate Excellon PTH/NPTH drills. The native KiCad board is the design authority. This package is for prototype fabrication; physical electrical/thermal qualification remains pending.

| Parameter | Request |
| --- | --- |
| Outline | 96 × 96 mm square, dimension defined by Edge.Cuts centerline |
| Layers | Two copper layers, top/bottom solder mask and silkscreen |
| Material/thickness | FR-4, 1.6 mm nominal |
| Copper | 1 oz / 35 µm finished-design assumption; confirm fabrication process |
| Finish | Lead-free HASL or ENIG; ENIG preferred for flat fine-pitch pads |
| Minimum designed track/clearance | 0.18 mm track, 0.20 mm clearance rules; see native DRC settings |
| Smallest finished plated hole | 0.30 mm |
| Drill count | 268 plated holes, four 3.20 mm nonplated mounting holes |
| Mounting centers | (4,4), (92,4), (4,92), (92,92) mm from board top-left |
| Solder mask | Follow supplied apertures; tent vias where no mask opening exists |
| Stencil | Top only, 0.10 mm starting thickness; retain U3 split exposed-pad windows |

Nine Gerber layers are supplied: F/B copper, F/B mask, F/B silk, F/B paste and Edge.Cuts. Bottom paste is intentionally empty because all fitted parts are on top. Drill coordinates are in millimeters with decimal notation; KiCad exports to 0.001 mm coordinate resolution. The independent manifest comparison allows only the resulting half-micron rounding difference.

The drill report and drill-map PDFs help inspection; they do not replace the drill files. Do not merge nonplated mounting holes into the plated drill set. Do not scale any fabrication layer. Copper keepouts around the mounting holes are intentional. Do not add automatic copper fill or remove the U3 thermal-via/paste arrangement without engineering review.

Assembly placement CSVs, the interactive BOM, top assembly PDF and full schematic PDF are in `../assembly`. They use the same board origin; Y values in placement exports are negative below the top-left origin, following KiCad export convention. The BOM includes exact manufacturer and DigiKey order codes. Test pads and mounting holes are fabricated features, not separate purchased components.

KiCad ERC/DRC and model parity pass. A separate Gerbonara parser checked Gerber X2 pad identities, nets and coordinates against the PCB manifest, plus all drill positions, outline, component values and placement references. See `../../reports/manufacturing/verification.json`. Fabricator CAM review is still appropriate before manufacture.
