# Rev B tools and reproduction

**Scope: Rev B.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

The saved native schematic and routed PCB are authoritative. Reproduction starts with those files and regenerates reports and exports; it does not rerun the placement experiments or autorouter.

Tools used: KiCad 10.0.6 with matching Python bindings and standard libraries, Arm GNU GCC 13.2.1, GNU make, ngspice 42, Python 3.12, Java 17, native GCC/G++ with sanitizers, InteractiveHtmlBom 2.11.2 and Poppler. Python packages are pinned in `tools-requirements.lock`. Freerouting 2.4.1 and CadQuery 2.8.0 were design aids. Manufacturing verification uses Gerbonara 1.6.3 and Shapely 2.1.2; the DC ground estimate uses PyAMG 5.3.0.

`tools/env.sh` adds a local Python environment and `$CANDI_TOOLS_ROOT/bin` to PATH. In this workspace it can reuse the parent `.venv`. On another workstation, install native tools and provide wrappers named `kicad-python`, `host-gcc`, `host-g++` and `ibom` as needed. `kicad-python` must use the interpreter matching the installed KiCad bindings; do not mix its compiled extensions with Python 3.12. Native tool binaries and library caches are not bundled.

```bash
source tools/env.sh
python scripts/build_bom.py
python calculations/electrical_checks.py
make -C firmware
bash scripts/test_firmware.sh
bash scripts/test_drivers.sh
bash scripts/export_manufacturing.sh
kicad-python scripts/export_board_manifest.py
python scripts/verify_manufacturing.py
python scripts/verify_gerber_connectivity.py
python scripts/verify_gerber_geometry.py
kicad-python scripts/check_programming_geometry.py
kicad-python scripts/audit_power_routes.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python calculations/ground_return_model.py .10 .075
python calculations/loaded_input_thresholds.py
```

Driver dependency versions are pinned in `tools/driver_dependencies.json`; use `python tools/fetch_driver_dependencies.py` to restore missing dependencies. Firmware third-party sources and their provenance are included. Firmware source/build commands are detailed in its README; program only after inspection and with the documented custom Tag-Connect adapter.

The boost model runs from its directory so ngspice reads the supplied `.spiceinit`:

```bash
cd simulation
ngspice -b boost.cir
ngspice -b boost_corner.cir
```

Large transient raw files are omitted from the delivery ZIP. The model, circuit decks, sampled waveform, measurements and plots are included. Running the simulations recreates the raw files. Allow several GB of memory for simulations and the fine-grid ground calculation. Neither simulation includes physical PCB measurements.

To rebuild the PDFs after exports and review renders:

```bash
bash scripts/render_board.sh
python scripts/build_bom_pdf.py
python scripts/build_handbook.py
```

The documentation uses local DejaVu fonts from the standard Linux font directory. The PCB models resolve through `${KIPRJMOD}/library/3d`; they should not require this development machine's paths. Horizontal /90 connector models use manufacturer STEP geometry with a rigid translation and project colors; run `python scripts/import_connector_models.py` to recreate them. Other custom models, including inductors, remain nominal envelopes. CAD checks do not establish physical fit.

To check refreshed documentation and package the revision, run:

```bash
python scripts/review_documents.py
python scripts/build_release.py
```

The review checks local links in every maintained guide and PDF text bounds; visually inspect the affected pages too.
