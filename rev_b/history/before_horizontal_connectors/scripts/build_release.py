"""Package authoritative Rev B files; exclude routing experiments and large raw data."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'release'
DEST.mkdir(exist_ok=True)
selected = set()

def add(pattern):
    matches = [p for p in ROOT.glob(pattern) if p.is_file()]
    assert matches, f'No release files: {pattern}'
    selected.update(matches)

for pattern in [
    'README.md', 'TOOLS.md', 'DESIGN_PLAN.md', 'tools-requirements.lock',
    'bom/*', 'docs/*.md', 'tools/*', 'licenses/*', 'examples/**/*',
    'host/*.py', 'calculations/*.py',
    'firmware/Makefile', 'firmware/README.md', 'firmware/.clang-format',
    'firmware/*.ld', 'firmware/src/*', 'firmware/include/*',
    'firmware/tests/**/*', 'firmware/third_party/**/*',
    'firmware/build/sensor_can.*',
    'hardware/FRC_Sensor_CAN.kicad_pro', 'hardware/FRC_Sensor_CAN.kicad_dru',
    'hardware/FRC_Sensor_CAN.kicad_pcb', 'hardware/*.kicad_sch',
    'hardware/fp-lib-table', 'hardware/sym-lib-table', 'hardware/library/**/*',
    'hardware/design/circuit.py', 'hardware/design/circuit_rev_a.py',
    'hardware/design/circuit.json', 'hardware/design/symbol_pinmap.json',
    'hardware/design/final_placement.json', 'hardware/design/final_ground_stitches.json',
    'hardware/design/schematic.net.xml',
    'sources/*.pdf', 'sources/*.txt', 'sources/boost_model/**/*',
    'simulation/*.cir', 'simulation/*.lib', 'simulation/.spiceinit',
    'simulation/*_sampled.csv',
    'reports/erc/final.json', 'reports/drc/final.json',
    'reports/design_parity.json', 'reports/programming_geometry.json',
    'reports/boost_simulation.json', 'reports/boost_spice_run.log', 'reports/boost_corner.log',
    'reports/firmware-build.log', 'reports/firmware-tests.log', 'reports/driver-tests.log',
    'reports/document_links.json', 'reports/pdf_review.json',
    'reports/manufacturing/*.json', 'reports/manufacturing_export.log',
    'reports/electrical/*.json', 'reports/electrical/ground_fields.npz',
    'reports/electrical/ground_return_0.1mm.png', 'reports/electrical/ground_return_0.075mm.png',
    'reports/driver/deps/*', 'reports/driver/cpp-deps/**/*',
    'output/fabrication/*', 'output/assembly/*', 'output/mechanical/*',
    'output/documentation/*', 'output/boost_simulation.*',
    'output/review/board_3d_final.png', 'output/review/board_top.png',
    'output/review/board_bottom.png', 'output/review/size_comparison.png',
    'output/review/gerber_*',
]:
    add(pattern)

scripts = '''build_release.py validate_release.sh build_bom.py build_bom_pdf.py
build_handbook.py build_mechanical_template.py build_validation_summary.py
export_manufacturing.sh export_assembly_drawing.py export_board_manifest.py
check_design_parity.py check_programming_geometry.py verify_manufacturing.py
verify_gerber_connectivity.py verify_gerber_geometry.py audit_power_routes.py
test_firmware.sh test_drivers.sh plot_boost_simulation.py render_gerber_previews.py render_board.sh'''.split()
for name in scripts:
    add('scripts/' + name)
if (ROOT / 'reports/release_reproduction.json').exists():
    add('reports/release_reproduction.json')
    add('reports/release_reproduction.log')
selected = {p for p in selected if '__pycache__' not in p.parts
            and p.suffix not in {'.pyc', '.o', '.d', '.su'}
            and not p.name.startswith('weidmuller_3p_90')}

# Validate local links in the project documentation inside this exact archive.
broken = []
for path in selected:
    if path.suffix != '.md' or any(d in path.parts for d in ['third_party', 'licenses']):
        continue
    for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
        if re.match(r'^[a-z]+:|^#', link):
            continue
        target = (path.parent / link.split('#')[0]).resolve()
        if not (target in selected or target.is_dir() and any(target in p.parents for p in selected)):
            broken.append((str(path.relative_to(ROOT)), link))
assert not broken, broken

entries = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
           for p in sorted(selected)]
manifest = {'project': 'FRC Sensor CAN Rev B', 'status': 'Unbuilt prototype',
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'files': entries, 'file_count': len(entries),
            'scope': 'Hashes identify delivered files; manifest and ZIP checksum are outside this file list.'}
manifest_bytes = (json.dumps(manifest, indent=2) + '\n').encode()
(DEST / 'manifest.json').write_bytes(manifest_bytes)
archive = DEST / 'FRC_Sensor_CAN_RevB_Prototype.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for entry in entries:
        z.write(ROOT / entry['path'], 'FRC_Sensor_CAN_RevB/' + entry['path'])
    z.writestr('FRC_Sensor_CAN_RevB/manifest.json', manifest_bytes)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(DEST / (archive.name + '.sha256')).write_text(f'{digest}  {archive.name}\n')
print(json.dumps({'archive': str(archive), 'files': len(entries),
                  'size_bytes': archive.stat().st_size, 'sha256': digest}, indent=2))
