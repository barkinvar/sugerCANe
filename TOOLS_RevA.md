**Installed tools for the sensor-to-CAN project**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Installed on 2026-09-07 for Ubuntu 24.04 x86-64. Tools are user-local because noninteractive sudo requires a password. No system package installation or Codex MCP configuration change was needed.

| Tool | Installed version | Purpose |
| --- | --- | --- |
| KiCad, CLI, schematic/PCB editors, Gerber viewer | 10.0.6 | Editable design, ERC/DRC, fabrication exports |
| KiCad standard symbols, footprints, 3D models and Python API | Bundled with 10.0.6 | Libraries, automation, mechanical review |
| InteractiveHtmlBom | 2.11.2 | Clickable BOM/board assembly view for hand soldering |
| ngspice | 42 | Circuit simulation |
| Unicorn / pyelftools | 2.1.4 / 0.32 | Compiled Cortex-M0 function execution against explicit synthetic register models |
| GNU Arm Embedded C/C++ compiler | 13.2.1 | STM32/Cortex-M firmware, with newlib and C++ libraries |
| OpenOCD | 0.12.0 | SWD programming/debugging when hardware is connected |
| CMake / Ninja | 4.4.3 / 1.13.2 | Firmware build orchestration |
| Python environment | Python 3.12.3; packages pinned in tools-requirements.lock | Numerical analysis, plots, BOM tables, PDF inspection, CAN utilities |
| PDF skill | openai/skills curated skill | Datasheet and schematic PDF review workflow |

Python packages include NumPy, SciPy, PyAMG 5.3.0, Shapely, Gerbonara, Matplotlib, pandas, pypdf, pdfplumber, ReportLab, Pillow, python-can, cantools, and pyserial. Existing Poppler commands provide PDF rendering.

**Use from this project**

```bash
cd /path/to/candi-clone
source tools/env.sh
kicad
kicad-cli version
ngspice --version
arm-none-eabi-gcc --version
openocd --version
python tools/verify_toolchain.py
```

The desktop application menu also has **KiCad 10 (CANDI tools)**. GUI windows require a desktop display; this tool session verified command-line operations and the Python API rather than an interactive GUI session.

`kicad-python` runs KiCad's bundled Python 3.11 interpreter with `pcbnew`. Use it for PCB automation; use project `python` for calculations and PDF/BOM processing. Their Python versions and compiled extensions differ, so do not mix the environments.

For an actual board, the assembly BOM command is:

```bash
source tools/env.sh
bash scripts/export_manufacturing.sh
```

The routed prototype is hardware/FRC_Sensor_CAN.kicad_pcb. The export script creates Gerbers, drills, PDFs, STEP and the interactive BOM. The plugin is also linked into the user KiCad 10 scripting-plugin directory. The headless `ibom` wrapper was verified; desktop plugin discovery remains to be checked in the GUI.

**Locations and provenance**

- Tool installation: `/home/neuro/.local/share/candi-tools/` (approximately 8.1 GB including full 3D libraries, firmware libraries, and downloaded archives).
- Project Python environment: `/home/neuro/candi-clone/.venv/`.
- Command wrappers: `/home/neuro/.local/share/candi-tools/bin/`, added to the current shell by `tools/env.sh`.
- PDF skill: `/home/neuro/.codex/skills/pdf/`; available to Codex on the next turn.
- Exact package versions, source URLs, archive hashes, and plugin commit: `reports/toolchain/installation.json`.
- Tool verification results: `reports/toolchain/verification.json`.
- Disposable check fixtures and detailed logs: `reports/toolchain/work/` (gitignored).

KiCad comes from the stable full Linux AppImage linked by the [official KiCad download page](https://www.kicad.org/download/linux/), extracted for use without FUSE. The download matched the official mirror's published archive checksum; SHA-256 is recorded locally for reproducibility. ngspice, GCC/newlib, OpenOCD and dependencies were downloaded through the configured Ubuntu package repositories and extracted into a local sysroot. The required newlib include/library links were recreated inside that sysroot. Local wrappers supply OpenOCD's runtime library and script paths.

The BOM plugin is pinned to the upstream [InteractiveHtmlBom release v2.11.2](https://github.com/openscopeproject/InteractiveHtmlBom/releases/tag/v2.11.2). The installed skill comes from [OpenAI's curated PDF skill](https://github.com/openai/skills/tree/main/skills/.curated/pdf).

No additional MCP server is installed. The terminal can directly operate KiCad CLI, its Python API, ngspice, and the BOM plugin. Browser access can research DigiKey and manufacturer data. This supplies the needed capabilities without adding a redundant server. DigiKey API integration can be added later if authenticated stock/BOM automation becomes necessary; no API credentials are required for this setup.

**Verification and limits**

The check script exercised a 12 V resistor divider and verified its 6 V result, compiled and linked C and C++ Cortex-M0+ fixtures, created/reopened a board through the KiCad Python API using a bundled 0805 footprint, executed the DRC engine, exported Gerbers/drills, generated an interactive HTML BOM, executed ERC on a bundled upstream schematic, exported/rendered its PDF, and sent/received a frame through python-can's virtual interface.

ERC and DRC here verify that the engines execute. Their fixture reports are not a product design review or a claim of zero violations. The standard `nosys` linker test may warn that operating-system file calls are stubbed; this is expected for this bare-metal fixture. No sensor circuitry, physical CAN traffic, probe access, or hardware programming has been tested. USB programmer permissions/udev rules may need system configuration once a probe is chosen. The final firmware uses STM32F042 CMSIS device headers v2.3.7 and Arm CMSIS 5.9.0. Their representative used files were compared byte-for-byte with the pinned official tags; see firmware/third_party/PROVENANCE.json. ESP-IDF is not required for the selected MCU.

To recreate the Python environment:

```bash
uv venv .venv
uv pip sync --python .venv/bin/python tools-requirements.lock
```

The native tools are a local, pinned installation, not an apt-managed system installation. Preserve the installation manifest when moving or updating them, and rerun the verification script after changes.

**Final design validation and additional tools**

`bash scripts/validate_release.sh` validates the saved native schematic and PCB without rerouting or overwriting either drawing. It exports the structured circuit model and BOM, checks electrical calculations, builds/tests firmware and Java/C++/Python integration, runs the documented SPICE cases, exports fabrication files, and independently reconstructs Gerber connectivity. Reports are written under `reports/validation`; a failure stops the run. Successful computational validation does not replace physical bring-up.

Additional installed tools used during design are native GCC/G++ 13.3 with address/undefined-behavior sanitizers, Java JDK 17.0.20.1, Freerouting 2.4.1 with its JRE 25, CadQuery 2.8.0 for six original package envelopes, Gerbonara 1.6.3 for independent manufacturing-file parsing, and Shapely 2.1.2 for copper geometry. Freerouting is a historical routing aid; it is not invoked by the release validator. The saved routed PCB is authoritative. The final Python lock also contains Markdown and BeautifulSoup for the printable handbook.

The driver dependencies can be restored with `python tools/fetch_driver_dependencies.py`. URLs and SHA-256 hashes are pinned in `tools/driver_dependencies.json`; matching local files are reused and mismatches fail. All seven remote Java/header downloads were compared with the files used for compilation. `CANDI_JDK` can select another Java 17 installation. The test scripts use `host-gcc`/`host-g++` wrappers for this workspace's extracted native compiler; on another machine, provide equivalent wrappers around its native GCC/G++ with sanitizer support. `kicad-python` must use the Python interpreter matching that machine's KiCad bindings.

For routine use on another workstation, install KiCad 10 with its standard libraries, Arm GNU Toolchain 13.2.Rel1, GNU make, Python and pyserial. Open the project directly in KiCad, build with `make -C firmware`, and use the supplied HEX/BIN only after hardware inspection. Reproducing every engineering check additionally needs ngspice 42, the pinned Python packages, Java 17, native GCC/G++, the KiCad Python bindings, InteractiveHtmlBom 2.11.2 and Poppler. Native tool binaries and their several-gigabyte library cache are not bundled in the prototype ZIP.

The ground-return estimate uses PyAMG to solve a square-grid resistor-sheet model reconstructed from exported Gerbers. The validation runner uses one BLAS/OpenMP thread to avoid oversubscription. Its 0.10 mm mesh uses about 1.26 million unknowns; allow several GB of memory. This is a DC numerical estimate with mesh/conservation checks, not an AC, thermal or EMC solver.

The final validator also renders the assembled board and copper review drawings, characterizes short pulses, and rebuilds the PDF documentation. `scripts/verify_documentation.py` checks text page bounds and the mounting template's nominal vector scale. Printer scaling and physical fit still require an actual print and board.

`python scripts/reproduce_release.py release/FRC_Sensor_CAN_RevA_Prototype.zip` extracts an archive to a new temporary directory, checks its manifest, creates a fresh Python environment from the lock, removes firmware build products and reruns validation. It retains the extracted workspace and writes `release/reproduction.json` beside the archive. Native tools are reused from this workstation; the report does not claim a different-OS or physical-hardware test.

Unicorn is used as a CPU instruction engine, following its [official project documentation](https://github.com/unicorn-engine/unicorn). It does not supply an STM32F042 peripheral model here; the project test harness defines the limited register behavior and records that limitation.
