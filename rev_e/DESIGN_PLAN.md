# Rev E implementation scope

Add independent electronic NPN, PNP, push-pull, floating detection and keeper modes. Remove JP103/JP203/JP303 input-bias selectors. Preserve the separate 5 V/12 V power caps and optional CAN termination bridge. Six MOSFETs and seven added resistors use spare MCU GPIOs; the existing comparator and protected digital input divider remain.

The board extends from D2's 52 × 64 mm to 52 × 70 mm. All components remain on top. In1 remains dedicated to ground; In2 has a ground pour and three low-speed bias-control routes to escape the MCU. Critical converter/crystal routes are preserved. Factory scope is 111 SMT placements; the user fits six terminals, three power headers and three loose caps.

Firmware 0.6.0 uses hardware identity 5 and protocol 4. CAN service persists per-input modes and active conditions together with ID/inversion/debounce. Robot APIs offer volatile changes and input-state readback. The GUI and CLI expose the same choices. Earlier revisions remain preserved.

Regenerate native CAD, BOM, manufacturing exports, firmware, tests, documentation and release archives together. Physical sensor compatibility, gate startup, backfeed, float timing, thermal, EMC, surge and vibration qualification remain open. See [input modes](docs/INPUT_MODES.md), [cost basis](docs/COST_REDUCTION.md) and [validation](docs/VALIDATION.md).
