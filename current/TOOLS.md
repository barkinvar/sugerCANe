# Tools and reproduction

Run the [pre-fabrication review](docs/ORDER_READINESS.md) after refreshing the native board and electrical evidence: `python scripts/check_order_readiness.py`. Its `--verify-report` mode checks retained hashes and recalculates routed-copper voltage drop. It does not reroute the PCB or perform physical testing.

The saved native KiCad schematic/PCB are authoritative. Circuit data, schematic, BOM and PCB must agree. Historical placement/router experiments have been removed; validation never reroutes the board.

The sugarCANe bottom artwork is an outlined SVG under `hardware/artwork/`. `python scripts/build_brand_artwork.py` rebuilds it using the retained Pixelify Sans font; `kicad-python scripts/apply_bottom_artwork.py` applies it only to B.Silkscreen. `finish_markings.py` preserves the artwork-only underside when regenerating labels. See the [artwork source and provenance](hardware/artwork/README.md).

Tested toolchain: KiCad 10.0.6 and its matching pcbnew interpreter, Python 3.12, Arm GNU GCC 13.2.1, GNU make, host GCC/G++, Java 17, Java 25 for the WPILib 2027 adapter, Poppler, InteractiveHtmlBom 2.11.2 and [pinned Python packages](tools-requirements.lock). Native tool binaries and dependency caches are outside Git. PDF generation uses DejaVu Sans/Mono.

```sh
# Run from current/, after installing native tools.
uv venv --python python3.12 .venv
uv pip sync --python .venv/bin/python tools-requirements.lock
source tools/env.sh
python tools/fetch_driver_dependencies.py
CANDI_JDK25=/path/to/jdk25 bash scripts/validate_release.sh
```

`tools/env.sh` uses this directory's venv, or the repository venv. It prepends `$CANDI_TOOLS_ROOT/bin` (default `$HOME/.local/share/candi-tools/bin`). Expected wrappers include `kicad-cli`, `kicad-python`, `host-gcc`, `host-g++`, `ibom` and Arm compiler commands. `kicad-python` must match the installed KiCad binary bindings. Java 17 can be selected with `CANDI_JDK`; the 2027 test downloads its pinned dependencies.

The validation script refreshes electrical budgets, loop sensitivity, board constraints, firmware/driver/bridge tests, native ERC/DRC/parity, manufacturing exports and independent Gerber geometry/connectivity checks. It compares against the small frozen Rev G contract in `hardware/design/rev_g_baseline.json`, without depending on an expanded historical checkout.

After validated changes, refresh documents and inspect the results:

```sh
bash scripts/render_board.sh
python scripts/compare_assembly_cost.py
python scripts/build_documents.py
python scripts/build_handbook.py
python scripts/review_documents.py
# Inspect final renders/PDFs and update reports/visual_review.json with their hashes.
python scripts/build_release.py
python scripts/verify_archive.py
```

`build_documents.py` creates the factory packet and Gerber ZIP after checking current release and power-review hashes. `build_release.py` also requires a completed visual-review record matching the final artifacts, then writes the source/review archive and manifest. `verify_archive.py` extracts it, verifies all hashes and reruns native checks. The manifest excludes itself and its enclosing ZIP from its own hashes. Review PDF page bounds and rendered pages; automated text bounds cannot detect every overlap.

Optional desktop setup preview: `python scripts/check_gui.py` with a working display, Tkinter and Pillow. It uses simulated data and performs no CAN I/O. `scripts/generate_schematic.py` rebuilds native sheets from `hardware/design/circuit.py`; PCB edits remain a separate CAD operation. `import_connector_models.py` is only for restoring/reviewing exact vendor CAD and transforms, followed by fresh STEP/render exports.

Compiler objects, downloaded Java dependencies, test runners, caches and scratch renderings are ignored. The retained firmware third-party subset supports STM32F042 and GCC; see its [provenance](firmware/third_party/README.md). All checks are engineering evidence; [physical qualification](docs/VALIDATION.md) remains required.

## Sensor-input transient simulation

The separate sensor-input screen is fast and runs as part of release validation:

```sh
python scripts/check_input_spice.py --jobs 4
python scripts/check_input_spice.py --verify-report
```

It uses the original TI comparator model linked for LM339LV, the three native input/reference networks and explicitly simplified bias/sensor circuits. Ten cases include nominal signals, voltage/leakage limits, floating probes, supply cycling and two half-timestep repeats. [Model scope and limitations](docs/VALIDATION.md#sensor-input-transient-screen) remain part of the result.

## Power transient simulation

The latest H rerun has eight freshly completed standalone/load-step cases. The two full coupled-startup traces remain incomplete, so the factory/release gate remains on HOLD. The [standalone results](reports/electrical/boost_spice_partial.json) and [waveforms](reports/electrical/boost_spice_partial.png) are separate from the full-suite report.

The optional native simulator is **ngspice 42 with KLU, XSPICE and PSpice compatibility**. Original manufacturer model files and hashes are retained in `sources/spice/`. The harness reads the maintained circuit's pin connections and component values; it generates simulator-specific copies, decks and raw traces under ignored `tmp/spice/`. The full run includes nine cases plus a complete combined-startup solver repeat; the coupled switching models can take several hours.

```sh
# From current/, after source tools/env.sh; switching-model runs can take several hours.
python scripts/check_boost_spice.py --jobs 2
# Reuse only completed traces whose deck, model and simulator hashes match.
python scripts/check_boost_spice.py --jobs 2 --reuse
# Fast evidence consistency check (preserves and reports failed findings).
python scripts/check_boost_spice.py --verify-report
# Also require every screening criterion to pass; used by validate_release.sh.
python scripts/check_boost_spice.py --verify-report --require-pass
```

The published [summary](reports/electrical/boost_spice.json) covers the protected boost stage, not the upstream buck or the whole board. A circuit, budget, source-model or harness change invalidates saved evidence. Each case has an eight-hour wall-time limit; a timeout or incomplete trace cannot pass. `--case NAME` produces separate partial reports and cannot replace the full release result. A failed screening criterion returns a nonzero exit status and remains visible in the report. See the [simulation scope](docs/VALIDATION.md#manufacturer-model-transient-screen). Individual-case outputs remain under ignored `tmp/spice/`; the full run is required for the release report.

## Firmware waveform replay and partial checkpoints

`python scripts/check_power_replay.py` replays four completed SPICE traces through the actual `power.c`, compiled with ASan/UBSan, at four ADC-error corners. It reads full-suite traces from `tmp/spice/` by default. `--traces PATH` selects another completed run directory, and `--verify-report` checks retained evidence hashes. The fresh standalone run used `tmp/spice/final-crosscheck-fresh/`. This is one-way replay: firmware shutdown commands do not change the recorded circuit.

While a full power run is incomplete, `python scripts/check_order_readiness.py --allow-incomplete` refreshes native pin and copper-drop evidence with a **HOLD** decision. After replay, `python scripts/write_validation_summary.py --allow-incomplete` publishes the completed checks with the same HOLD. The default commands and factory/release scripts still require full passing power evidence.
