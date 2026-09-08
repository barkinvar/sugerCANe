"""Create the separate China-assembly variant from the reviewed Rev B release.

Run once. Saved routing is authoritative. Same-value, same-footprint purchasing
changes are specified here; this script never substitutes functional ICs.
"""
from pathlib import Path
import json
import shutil
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
BASE, OUT = ROOT / 'rev_b', ROOT / 'rev_b2'
assert not OUT.exists(), 'Refuse to overwrite an existing variant'
manifest = json.loads((BASE/'release/manifest.json').read_text())
for item in manifest['files']:
    path = item['path']
    dest = OUT/path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE/path, dest)
for name in ['generate_schematic.py', 'sync_pcb_metadata.py']:
    shutil.copy2(BASE/'scripts'/name, OUT/'scripts'/name)

subs = {
    'RC0805FR-071KL': ('0805W8F1001T5E', 'UNI-ROYAL', 'C17513'),
    'RC0805FR-0710KL': ('0805W8F1002T5E', 'UNI-ROYAL', 'C17414'),
    'RC0805FR-074K7L': ('0805W8F4701T5E', 'UNI-ROYAL', 'C17673'),
    'RC0805FR-07100KL': ('0805W8F1003T5E', 'UNI-ROYAL', 'C149504'),
    'CC0805KRX7R9BB104': ('CL21B104KCFNNNE', 'Samsung Electro-Mechanics', 'C28233'),
}
(OUT/'bom/substitutions.json').write_text(json.dumps(subs, indent=2)+'\n')
path=OUT/'hardware/design/circuit.py'
s=path.read_text()
idx=s.index('def export():')
s=s[:idx]+'''# Factory variant: values, pin maps and land patterns remain unchanged.
SUBSTITUTIONS = json.loads((ROOT/'bom/substitutions.json').read_text())
for ref, component in PARTS.items():
    original = component.get('mpn')
    if original in SUBSTITUTIONS:
        mpn, manufacturer, lcsc = SUBSTITUTIONS[original]
        component.update(mpn=mpn, manufacturer=manufacturer, lcsc=lcsc,
                         original_rev_b_mpn=original)
        component['note'] += ' Rev B-2: same-value factory sourcing equivalent.'
        if component['kind'] == 'C':
            component['voltage'] = '100V'
''' + s[idx:]
s=s.replace("'revision':'B'", "'revision':'B-2'")
path.write_text(s)

# Only the printed revision changes on the PCB. Purchasing metadata is synced
# from the model subsequently through KiCad's field API.
path=OUT/'hardware/FRC_Sensor_CAN.kicad_pcb'
s=path.read_text().replace('SENSOR CAN / REV B"', 'SENSOR CAN / B-2"')
path.write_text(s)

# Relabel maintained prose and documentation generators, preserving the original
# electrical evidence and provenance in the base release.
for folder in ['docs', 'output/fabrication']:
    for path in (OUT/folder).glob('*.md'):
        s=path.read_text().replace('Rev B', 'Rev B-2').replace('Revision B', 'Revision B-2')
        path.write_text(s)
for name in ['build_handbook.py','build_mechanical_template.py','build_validation_summary.py']:
    path=OUT/'scripts'/name
    s=path.read_text().replace('REVISION B ', 'REVISION B-2 ').replace('Revision B', 'Revision B-2').replace('Rev B', 'Rev B-2').replace('RevB', 'RevB2')
    path.write_text(s)
for name in ['build_bom.py','build_bom_pdf.py','build_release.py']:
    (OUT/'scripts'/name).unlink()  # replaced with variant-aware generators
for name in ['DigiKey_import.csv','BOM_grouped.csv','BOM_per_reference.csv','summary.json']:
    (OUT/'bom'/name).unlink()
for path in (OUT/'output/documentation').glob('*.pdf'):
    path.unlink()
for name in ['release_reproduction.json','release_reproduction.log','pdf_review.json','document_links.json']:
    (OUT/'reports'/name).unlink(missing_ok=True)
(OUT/'reports/base_release.json').write_text(json.dumps({
    'base': 'Rev B horizontal connector revision',
    'manifest': manifest,
    'inheritance': 'Firmware is identical. Re-export and rerun PCB/BOM/ERC/DRC checks for B-2; physical qualification remains outstanding.'
}, indent=2)+'\n')
print(OUT)
