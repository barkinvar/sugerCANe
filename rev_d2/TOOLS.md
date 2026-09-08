# Rev D-2 SC12 tools and checks

The saved native KiCad schematic/PCB are authoritative. Generation/placement/router scripts record design construction; they are not a one-command reroute of the reviewed board. Editing the circuit requires matching schematic, BOM, PCB and new checks. Earlier revisions remain separate.

Tested toolchain: KiCad 10.0.6, its matching Python/pcbnew interpreter, Python 3.12, Arm GNU GCC 13.2.1, GNU make, host GCC/G++, Java 17, Poppler, InteractiveHtmlBom 2.11.2 and the packages pinned in `tools-requirements.lock`. Tool binaries/caches are external to the repository. Install those native tools for the host operating system. The `kicad-python` wrapper must use the interpreter matching the KiCad binary bindings, not an arbitrary venv Python.

```sh
# In rev_d2/, after installing native tools:
uv venv --python python3.12 .venv
uv pip sync --python .venv/bin/python tools-requirements.lock
source tools/env.sh
python tools/fetch_driver_dependencies.py
bash scripts/validate_release.sh
```

`tools/env.sh` uses a revision-local venv, or the repository venv when working in the full checkout. It prepends `$CANDI_TOOLS_ROOT/bin` (default `$HOME/.local/share/candi-tools/bin`). Wrappers expected there are `kicad-cli`, `kicad-python`, `host-gcc`, `host-g++`, `ibom`, and Arm compiler commands. Java is under the configured tools root or selected with `CANDI_JDK`. Fonts for the PDFs are DejaVu Sans/Mono.

The validation script checks the saved design and refreshes manufacturing evidence, firmware and host tests; it does not move or reroute components. A visual/documentation refresh is separate:

```sh
bash scripts/render_board.sh
python scripts/build_documents.py
python scripts/build_handbook.py
python scripts/review_documents.py
python scripts/build_release.py
```

The factory packet is built by `build_documents.py`. Rebuild it after any BOM/placement/fabrication change. `build_release.py` selects authoritative files and writes a manifest plus ZIP checksum. Check an extracted archive with `verify_archive.py`; the release manifest deliberately excludes itself and the enclosing ZIP from its file hashes.

Use `python scripts/import_connector_models.py` only when restoring/reviewing vendor models. It checks the original STEP hashes and all six native connector pad patterns, then writes translated local models. It can change STEP headers, requiring a fresh STEP export, renders and release. Keep the originals and provenance JSON together.

`hardware/design/circuit.py` is the explicit component/net model; `generate_schematic.py` rebuilds the schematic. Construction helpers such as `pack_compact.py`, `route_critical.py` and `apply_routes.py` operate on intermediate files and can overwrite placement/routing. They are not part of release validation. The boost CCM analytical loop screen is in `check_converter_loop.py`. It is not a switching simulation or thermal qualification. Do not reuse older revision reports as evidence for this changed supply.

In the full repository, `kicad-python scripts/check_variant.py` compares D-2 component pin nets, passive values/footprints, critical routes and firmware sources with the preserved neighboring `rev_d/`. The dated result is included in [variant_verification.json](reports/variant_verification.json); a standalone D-2 archive does not contain the older D baseline.
