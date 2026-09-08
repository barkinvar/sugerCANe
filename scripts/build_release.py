"""Create private prototype and bare-board fabrication archives with exact hashes.

The fabrication archive contains only the current fabrication directory. The
prototype archive includes editable sources, required local libraries, firmware,
documentation and final evidence, excluding installed tools and obsolete routing
snapshots. This script does not submit an order or publish anything.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'release';DEST.mkdir(exist_ok=True)
files=set()
def add(path):
    path=ROOT/path
    if path.is_file():files.add(path)
    elif path.is_dir():
        files.update(p for p in path.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and '.git' not in p.parts
                     and p.suffix not in ('.pyc','.lck','.kicad_prl'))
    else:raise FileNotFoundError(path)

for p in ['REV_A.md','DESIGN_PLAN.md','TOOLS_RevA.md','tools-requirements.lock','docs','bom',
          'licenses','tools','host','examples','firmware/src','firmware/include',
          'firmware/tests','firmware/third_party','firmware/README.md','firmware/Makefile',
          'firmware/stm32f042k6.ld','hardware/library','sources',
          'output/assembly','output/documentation','output/mechanical','output/fabrication']:
    add(p)
for extension in ['elf','hex','bin','map']:add('firmware/build/sensor_can.'+extension)
for p in (ROOT/'hardware').glob('*'):
    if (p.suffix == '.kicad_sch' or p.name in ('FRC_Sensor_CAN.kicad_pro',
                                             'FRC_Sensor_CAN.kicad_pcb',
                                             'sym-lib-table','fp-lib-table')):
        files.add(p)
for p in ['hardware/design/circuit.py','hardware/design/circuit.json','hardware/design/schematic.net.xml','hardware/design/README.md']:
    add(p)
for p in ['export_bom.py','export_assembly_drawing.py','export_manufacturing.sh','export_board_manifest.py','check_design_parity.py',
          'test_firmware.sh','audit_firmware_stack.py','test_drivers.sh','audit_power_routes.py','verify_manufacturing.py',
          'verify_gerber_connectivity.py','render_gerber_previews.py','render_power_layout.py','render_crystal_lands.py','validate_release.sh','generate_schematic.py',
          'sync_pcb_metadata.py','verify_gerber_geometry.py','refine_mount_keepouts.py',
          'generate_mechanical_models.py','build_architecture_diagram.py','build_wiring_card.py','build_documentation.sh','verify_documentation.py','build_handbook.py','build_bom_pdf.py','build_bench_plan.py','build_source_manifest.py',
          'check_document_links.py','build_release.py','reproduce_release.py','progress.py','watchdog.py']:
    add('scripts/'+p)
for p in ['calculations/electrical_checks.py','calculations/capacitor_derating.py',
          'calculations/simulate_inputs.py','calculations/simulate_pulse_response.py','calculations/simulate_inrush.py','calculations/ground_return_model.py']:
    add(p)
for p in ['reports/erc/final.json','reports/drc/final.json','reports/design_parity.json',
          'reports/electrical','reports/manufacturing','reports/validation',
          'reports/firmware-errata-review.json','reports/firmware-arm-registers.json','reports/firmware-arm-registers.log','reports/firmware-stack.json','reports/firmware-disassembly.txt','reports/firmware-build.log','reports/firmware-tests.log','reports/driver-tests.log',
          'reports/worksheet_review.json','reports/worksheet-browser-review.log','reports/assembly_browser_review.json','reports/assembly-browser-review.log','reports/assembly_browser_review.js','reports/document_links.json','reports/documentation.json',
          'reports/bench_measurements_template.csv','reports/bench_test_plan.csv','reports/toolchain/installation.json',
          'reports/toolchain/verification.json']:
    add(p)
for p in (ROOT/'reports/spice').glob('*'):
    if p.suffix in ('.json','.png','.pdf','.log'):files.add(p)
for p in ['board_3d_final.png','board_bottom_final.png','schematic_contact_sheet.png','gerber_top_copper.png','gerber_bottom_copper.png']:
    add('output/review/'+p)
for p in ['worksheet_desktop.png','worksheet_mobile.png','worksheet_example_print.pdf','assembly_u3_highlight.png','assembly_bom_overview.png']:
    add('output/playwright/'+p)

# Standalone Rev A entry points; repository-wide README/TOOLS are not bundled.
archive_sources = {str(p.relative_to(ROOT)): p for p in files}
archive_sources['README.md'] = ROOT / 'REV_A.md'
archive_sources['TOOLS.md'] = ROOT / 'TOOLS_RevA.md'

# Generated drawings and firmware must correspond to the verified design.
run=json.loads((ROOT/'reports/validation/run.json').read_text())
assert run['result']=='PASS'
for name,digest in run['sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, f'Validation stale: {name}'
manifest=dict(revision='A prototype',created_utc=datetime.now(timezone.utc).isoformat(),
              physical_validation='NOT PERFORMED',design_validation='reports/validation/run.json',
              scope='Rev A prototype review/build package; no manufacturing order or physical qualification performed.',
              files=[dict(path=name,bytes=p.stat().st_size,
                          sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for name,p in sorted(archive_sources.items())])
manifest_path=DEST/'manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')

fabrication=DEST/'FRC_Sensor_CAN_RevA_Fabrication.zip'
with zipfile.ZipFile(fabrication,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted((ROOT/'output/fabrication').iterdir()):
        if p.is_file():z.write(p,p.name)
prototype=DEST/'FRC_Sensor_CAN_RevA_Prototype.zip'
with zipfile.ZipFile(prototype,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,p in sorted(archive_sources.items()):z.write(p,'FRC_Sensor_CAN_RevA/'+name)
    z.write(manifest_path,'FRC_Sensor_CAN_RevA/release/manifest.json')
    z.write(fabrication,'FRC_Sensor_CAN_RevA/release/'+fabrication.name)

checks=[]
for archive in [fabrication,prototype]:
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
        if archive==prototype:
            for entry in manifest['files']:
                assert hashlib.sha256(z.read('FRC_Sensor_CAN_RevA/'+entry['path'])).hexdigest()==entry['sha256']
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    checks.append(f'{digest}  {archive.name}')
    print(f'{archive.name}: {archive.stat().st_size/1e6:.2f} MB, SHA-256 {digest}')
checks.append(f'{hashlib.sha256(manifest_path.read_bytes()).hexdigest()}  manifest.json')
(DEST/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n')
print(f'Verified {len(manifest["files"])} archived source/artifact files against the manifest.')
