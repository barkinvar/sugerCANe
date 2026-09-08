# Tools and rebuilding

[Repository overview](README.md) · [Revision history](REVISIONS.md)

The project uses KiCad 10.0.6, Arm GNU GCC 13.2.1, Python 3.12, GNU make, ngspice 42, Java 17, native GCC/G++, InteractiveHtmlBom 2.11.2 and Poppler. Python packages are pinned in each revision's `tools-requirements.lock`. CadQuery imports the manufacturer connector STEP geometry. Native tool installations and caches are not included in Git.

| Revision | Working directory | Detailed setup and commands |
|---|---|---|
| A | Repository root | [Rev A tools](TOOLS_RevA.md) |
| B | `rev_b/` | [Rev B tools](rev_b/TOOLS.md) |
| B-2 | `rev_b2/` | [Rev B-2 tools](rev_b2/TOOLS.md) |

First select a revision directory, then activate its environment:

```bash
# Run from the repository root; omit this cd for Rev A.
cd rev_b2
source tools/env.sh
```

On a new workstation, install the native tools, then create a Python environment with `uv venv --python python3.12 .venv` and `uv pip sync --python .venv/bin/python tools-requirements.lock`. Supply the `kicad-python`, `host-gcc`, `host-g++` and `ibom` wrappers described in the revision guide. `kicad-python` must use the interpreter matching KiCad's binary bindings.

The saved native PCB and schematics are authoritative. `bash scripts/validate_release.sh` checks that saved design and regenerates evidence; it does not reroute it. Simulations and the fine-mesh ground calculation can require several GB of memory. Computational checks do not replace hardware qualification.

For a B/B-2 visual refresh, run `python scripts/import_connector_models.py`, then `bash scripts/render_board.sh` and export the mechanical STEP. For documentation, run `python scripts/build_handbook.py`; B-2's `python scripts/build_factory_packet.py` also refreshes the factory PDF/upload ZIP. Finally run `python scripts/build_release.py` for the selected revision and verify its manifest/checksum.

Driver downloads are restored using `python tools/fetch_driver_dependencies.py`. Raw SPICE traces and build intermediates are ignored; final delivered images, firmware and engineering reports remain tracked. See the [generated-file policy](CONTRIBUTING.md).
