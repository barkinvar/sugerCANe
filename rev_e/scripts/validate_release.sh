#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
mkdir -p reports/electrical reports/manufacturing reports/driver
python scripts/build_bom.py
python scripts/estimate_cost.py
python scripts/check_electrical.py > reports/electrical/check.log
python scripts/check_converter_loop.py > reports/electrical/loop.log
kicad-python scripts/check_board_constraints.py > reports/board-constraints.log
bash scripts/test_firmware.sh
bash scripts/test_drivers.sh > reports/driver/tests.log 2>&1
bash scripts/export_manufacturing.sh > reports/manufacturing-export.log 2>&1
kicad-python scripts/export_board_manifest.py
python scripts/build_factory_files.py
python scripts/verify_manufacturing.py > reports/manufacturing/export-parity.log
python scripts/verify_gerber_geometry.py > reports/manufacturing/geometry.log
python scripts/write_validation_summary.py
echo 'PASS: Rev E saved design, BOM, electrical budgets, firmware/drivers and exported fabrication checks'
