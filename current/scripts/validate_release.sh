#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
mkdir -p reports/electrical reports/manufacturing reports/driver
python scripts/test_routing.py > reports/routing-tests.log 2>&1
python scripts/check_routing.py
python scripts/build_bom.py
python scripts/estimate_cost.py
python scripts/compare_assembly_cost.py
python scripts/check_electrical.py > reports/electrical/check.log
python scripts/check_component_margins.py > reports/electrical/component-margins.log
python scripts/check_converter_loop.py > reports/electrical/loop.log
python scripts/check_input_spice.py > reports/electrical/input-spice.log
python scripts/check_boost_spice.py --verify-report --require-pass
kicad-python scripts/check_board_constraints.py > reports/board-constraints.log
kicad-python scripts/test_compact_layout.py > reports/compact/layout-tests.log
kicad-python scripts/check_compact_layout.py > reports/compact/layout-verification.log
bash scripts/test_firmware.sh
bash scripts/test_drivers.sh > reports/driver/tests.log 2>&1
bash scripts/test_bridge2027.sh > reports/bridge2027-tests.log 2>&1
kicad-python scripts/check_variant.py > reports/variant.log
bash scripts/export_manufacturing.sh > reports/manufacturing-export.log 2>&1
kicad-python scripts/export_board_manifest.py
python scripts/build_factory_files.py
python scripts/build_factory_stencil.py
kicad-python scripts/check_jlc_packages.py
python scripts/verify_manufacturing.py > reports/manufacturing/export-parity.log
python scripts/verify_gerber_geometry.py > reports/manufacturing/geometry.log
python scripts/verify_gerber_connectivity.py > reports/manufacturing/connectivity.log
python scripts/check_order_readiness.py
python scripts/check_power_replay.py > reports/electrical/power-replay.log
python scripts/write_validation_summary.py
echo 'PASS: Rev H saved design, BOM, electrical budgets, firmware/drivers and exported fabrication checks'
