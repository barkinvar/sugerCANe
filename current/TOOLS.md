# Tools and reproduction

The [pre-order review](docs/ORDER_READINESS.md) remains HOLD. Run its pin and routed-copper checks with `python scripts/check_order_readiness.py`; `--verify-report` verifies retained evidence. Optional `--simulate --jobs 2` runs hypothetical component cases into ignored `tmp/order-review/` and can take over an hour; `--reuse` accepts only matching completed decks/models. These experiments were stopped during this review and are not counted as pass/fail evidence. None of these commands approves fabrication or changes fitted hardware.

The saved native KiCad schematic/PCB are authoritative. Circuit data, schematic, BOM and PCB must agree. Historical placement/router experiments have been removed; validation never reroutes the board.

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

The validation script refreshes electrical budgets, loop sensitivity, board constraints, firmware/driver/bridge tests, native ERC/DRC/parity, manufacturing exports and independent Gerber geometry/connectivity checks. It compares against the small frozen Rev E contract in `hardware/design/rev_e_baseline.json`, without depending on an expanded historical checkout.

After validated changes, refresh documents and inspect the results:

```sh
bash scripts/render_board.sh
python scripts/compare_assembly_cost.py
python scripts/build_documents.py
python scripts/build_handbook.py
python scripts/review_documents.py
python scripts/build_release.py
python scripts/verify_archive.py
```

`build_documents.py` creates the factory packet and Gerber ZIP. `build_release.py` writes a curated source/review archive and manifest. `verify_archive.py` extracts it, verifies all hashes and reruns native checks. The manifest excludes itself and its enclosing ZIP from its own hashes. Review PDF page bounds and rendered pages; automated text bounds cannot detect every overlap.

Optional desktop setup preview: `python scripts/check_gui.py` with a working display, Tkinter and Pillow. It uses simulated data and performs no CAN I/O. `scripts/generate_schematic.py` rebuilds native sheets from `hardware/design/circuit.py`; PCB edits remain a separate CAD operation. `import_connector_models.py` is only for restoring/reviewing exact vendor CAD and transforms, followed by fresh STEP/render exports.

Compiler objects, downloaded Java dependencies, test runners, caches and scratch renderings are ignored. The retained firmware third-party subset supports STM32F042 and GCC; see its [provenance](firmware/third_party/README.md). All checks are engineering evidence; [physical qualification](docs/VALIDATION.md) remains required.

## Power transient simulation

The optional native simulator is **ngspice 42 with XSPICE and PSpice compatibility**. Original manufacturer model files and hashes are retained in `sources/spice/`. The harness reads the maintained circuit's pin connections and component values; it generates simulator-specific copies, decks and raw traces under ignored `tmp/spice/`.

```sh
# From current/, after source tools/env.sh; takes several minutes.
python scripts/check_boost_spice.py --jobs 2
# Reuse only completed traces whose deck, model and simulator hashes match.
python scripts/check_boost_spice.py --jobs 2 --reuse
# Fast evidence consistency check (preserves and reports failed findings).
python scripts/check_boost_spice.py --verify-report
# Also require every screening criterion to pass; used by validate_release.sh.
python scripts/check_boost_spice.py --verify-report --require-pass
```

The published [summary](reports/electrical/boost_spice.json) and [waveforms](reports/electrical/boost_spice.png) cover the protected boost stage, not the upstream buck or the whole board. A circuit, budget, source-model or harness change invalidates saved evidence. `--case NAME` produces separate partial reports and cannot replace the full release result. `--case softstart_220n` and `--case softstart_330n` are hypothetical C66 value experiments, not the fitted board. A failed screening criterion returns a nonzero exit status and remains visible in the report; archive integrity checks can still verify a package containing negative evidence. See the [simulation scope](docs/VALIDATION.md#manufacturer-model-transient-screen) before interpreting a pass.

`--case typical_bias_curve` uses the retained Samsung C(V) data; `--case switch_rapid_reset` isolates U9 and saves its internal deglitch state. Individual-case outputs stay under ignored `tmp/spice/`. The published [diagnostic record](reports/electrical/boost_spice_experiments.json) includes the exact tested netlists, trace hashes and reproduction commands.
