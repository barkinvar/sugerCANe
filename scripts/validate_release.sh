#!/usr/bin/env bash
# Validate the current native CAD files. Never reroute or overwrite a schematic.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
mkdir -p reports/validation reports/drc reports/erc
run_check() {
  local name="$1"
  shift
  python scripts/progress.py "Release validation: $name"
  "$@" > "reports/validation/$name.log" 2>&1 || {
    cat "reports/validation/$name.log"
    return 1
  }
  echo "PASS $name"
}
# circuit.py exports the structured source model; parity detects disagreement
# with the editable schematic/PCB rather than silently changing either drawing.
run_check circuit_model python hardware/design/circuit.py
run_check bom python scripts/export_bom.py
run_check electrical python calculations/electrical_checks.py
run_check capacitor_derating python calculations/capacitor_derating.py
run_check routed_power kicad-python scripts/audit_power_routes.py
run_check dependencies python tools/fetch_driver_dependencies.py
run_check firmware bash scripts/test_firmware.sh
run_check firmware_stack python scripts/audit_firmware_stack.py
run_check firmware_arm_registers python firmware/tests/test_arm_registers.py
cp reports/validation/firmware_arm_registers.log reports/firmware-arm-registers.log
run_check drivers bash scripts/test_drivers.sh
cp reports/validation/drivers.log reports/driver-tests.log
run_check input_spice python calculations/simulate_inputs.py
run_check pulse_response python calculations/simulate_pulse_response.py
run_check inrush_spice python calculations/simulate_inrush.py
run_check manufacturing_export bash scripts/export_manufacturing.sh
run_check board_manifest kicad-python scripts/export_board_manifest.py
run_check board_render kicad-cli pcb render --width 1800 --height 1300 --quality high --background transparent --rotate 335,0,20 --zoom 0.65 --use-board-stackup-colors -o output/review/board_3d_final.png hardware/FRC_Sensor_CAN.kicad_pcb
run_check manufacturing_parser python scripts/verify_manufacturing.py
run_check gerber_connectivity python scripts/verify_gerber_connectivity.py
run_check gerber_geometry python scripts/verify_gerber_geometry.py
run_check gerber_previews python scripts/render_gerber_previews.py
run_check power_layout_review python scripts/render_power_layout.py
run_check ground_return env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python calculations/ground_return_model.py
run_check documentation bash scripts/build_documentation.sh
python scripts/progress.py 'All release validation stages passed; physical qualification remains pending.'
python - <<'PY'
from pathlib import Path
import datetime, hashlib, json
paths = {'hardware/FRC_Sensor_CAN.kicad_pcb', 'hardware/FRC_Sensor_CAN.kicad_pro',
         'hardware/design/circuit.json', 'firmware/build/sensor_can.bin',
         'bom/BOM_grouped.csv', 'scripts/validate_release.sh', 'firmware/Makefile',
         'firmware/stm32f042k6.ld'}
paths.update(str(p) for p in Path('hardware').glob('*.kicad_sch'))
for directory in ('hardware/library', 'firmware/src', 'firmware/include',
                  'firmware/tests', 'host', 'examples'):
    paths.update(str(p) for p in Path(directory).rglob('*') if p.is_file()
                 and '__pycache__' not in p.parts and p.suffix != '.pyc')
files = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(paths)}
Path('reports/validation/run.json').write_text(json.dumps({
    'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'result': 'PASS', 'physical_validation': 'NOT PERFORMED', 'sha256': files
}, indent=2) + '\n')
PY
