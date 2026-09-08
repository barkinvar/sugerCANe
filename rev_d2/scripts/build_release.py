"""Curated prototype source/manufacturing package; no router trials or tool caches."""
from pathlib import Path
import hashlib,json,zipfile
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];D=R/'release';D.mkdir(exist_ok=True)
patterns=['*.md','tools-requirements.lock','bom/*','docs/*.md','tools/*','licenses/*','scripts/*','host/*.py','examples/**/*',
 'firmware/Makefile','firmware/README.md','firmware/.clang-format','firmware/*.ld','firmware/src/*','firmware/include/*','firmware/tests/**/*','firmware/third_party/**/*','firmware/build/sensor_can.*','firmware/build/bootloader.*','firmware/build/factory.hex','firmware/build/application.sc12',
 'hardware/FRC_Sensor_CAN.kicad_pcb','hardware/FRC_Sensor_CAN.kicad_pro','hardware/FRC_Sensor_CAN.kicad_dru','hardware/*.kicad_sch','hardware/*-lib-table','hardware/library/**/*',
 'hardware/design/circuit.py','hardware/design/circuit.json','hardware/design/symbol_pinmap.json','hardware/design/schematic.net.xml','hardware/design/compact_placement.json',
 'sources/**/*','output/fabrication/*','output/assembly/*','output/mechanical/*','output/documentation/*','output/review/board*.png','output/review/service_gui.png','output/review/gerber_*',
 'order/*','reports/erc/final.json','reports/drc/final.json','reports/design_parity.json','reports/board_constraints.json','reports/document_review.json','reports/release_checks.json','reports/visual_review.json','reports/variant_verification.json','reports/electrical/*.json','reports/electrical/*.png','reports/manufacturing/*.json',
 'reports/firmware-images.json','reports/firmware-arm-registers.json','reports/bridge2027-tests.log','reports/firmware-build.log','reports/firmware-tests.log','reports/driver/tests.log','reports/manufacturing-export.log']
selected=sorted({p for pat in patterns for p in R.glob(pat) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.o','.d')})
assert any(p.name=='board_3d_final.png' for p in selected)
entries=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in selected]
manifest=dict(project='SC12 Rev D-2',status='Unbuilt prototype',created_utc=datetime.now(timezone.utc).isoformat(),file_count=len(entries),files=entries,scope='Manifest and enclosing archive excluded from their own hashes; no physical qualification.')
raw=(json.dumps(manifest,indent=2)+'\n').encode();(D/'manifest.json').write_bytes(raw)
dest=D/'FRC_Sensor_CAN_RevD2_SC12_Prototype.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in selected:z.write(p,'SC12_RevD2/'+p.relative_to(R).as_posix())
 z.writestr('SC12_RevD2/manifest.json',raw)
(D/(dest.name+'.sha256')).write_text(hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name+'\n')
print(f'Packaged {len(entries)} files, {dest.stat().st_size:,} bytes: {dest}')
