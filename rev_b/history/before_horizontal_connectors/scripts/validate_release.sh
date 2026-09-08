#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
mkdir -p reports/erc reports/drc reports/manufacturing reports/electrical output/review
python scripts/build_bom.py
python calculations/electrical_checks.py
bash scripts/test_firmware.sh > reports/firmware-test-run.log 2>&1
python tools/fetch_driver_dependencies.py
bash scripts/test_drivers.sh > reports/driver-tests.log 2>&1
bash scripts/export_manufacturing.sh > reports/manufacturing_export.log 2>&1
kicad-python scripts/export_board_manifest.py
kicad-python scripts/check_programming_geometry.py
python scripts/verify_manufacturing.py
python scripts/verify_gerber_connectivity.py
python scripts/verify_gerber_geometry.py
kicad-python scripts/audit_power_routes.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python calculations/ground_return_model.py .10 .075
python calculations/loaded_input_thresholds.py
python scripts/build_validation_summary.py
