"""Omit hand-fitted U5 from factory paste while preserving the native design."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
from gerbonara import GerberFile
from gerbonara.graphic_objects import Flash

R = Path(__file__).resolve().parents[1]
plan = json.loads((R/'bom/assembly_plan.json').read_text())
omit = set(plan['hand_solder_smt_references'])
assert omit == {'U5'} and plan['u5']['factory_paste'] is False
source = R/'output/fabrication/FRC_Sensor_CAN-F_Paste.gtp'
dest = R/'output/assembly/factory_top_paste.gtp'
g = GerberFile.open(source)
assert all(isinstance(o, Flash) for o in g.objects)
removed = [o for o in g.objects if o.attrs.get('.C', ('',))[0] in omit]
kept = [o for o in g.objects if o not in removed]
assert len(removed) == 32 and len(kept) == 325
manifest = json.loads((R/'reports/manufacturing/board_manifest.json').read_text())
u5 = next(c for c in manifest['components'] if c['reference']=='U5')
coords = lambda items: Counter((round(x,6), round(y,6)) for x,y in items)
assert coords((o.x,o.y) for o in removed) == coords((p['x_mm'],p['y_mm']) for p in u5['pads'])
def signature(o):
    return (round(o.x,6),round(o.y,6),str(o.aperture),o.polarity_dark,tuple(sorted(o.attrs.items())))
expected = Counter(signature(o) for o in kept)
# Preserve every aperture definition and every other command verbatim. A
# parse/write round trip can normalize macro parameters; it is unnecessary here.
lines = []
component = ''
deleted = 0
for line in source.read_text().splitlines(keepends=True):
    if line.startswith('%TO.C,'):
        component = line.strip()[6:-2]
    if line.strip() == '%TD*%':
        component = ''
    if component in omit and re.fullmatch(r'X-?\d+Y-?\d+D03\*\s*', line):
        deleted += 1
    else:
        lines.append(line)
assert deleted == 32
dest.write_text(''.join(lines))
actual = GerberFile.open(dest)
assert Counter(signature(o) for o in actual.objects)==expected
assert all(o.attrs.get('.C', ('',))[0] not in omit for o in actual.objects)
assert sum(o.attrs.get('.C')==('U9',) for o in actual.objects)==12, 'Preserve eight leads and four exposed-pad windows'
report = dict(result='PASS',purpose='Factory stencil only; U5 hand soldered by user',
    omitted_references=sorted(omit),removed_u5_apertures=32,retained_apertures=len(kept),
    all_other_paste_geometry_unchanged=True,native_board_unchanged=True,
    source=source.relative_to(R).as_posix(),output=dest.relative_to(R).as_posix(),
    input_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in [
        'bom/assembly_plan.json','hardware/FRC_Sensor_CAN.kicad_pcb',
        'reports/manufacturing/board_manifest.json',source.relative_to(R).as_posix(),
        'scripts/build_factory_stencil.py']},
    output_sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
(R/'reports/manufacturing/factory_stencil.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 32 U5 paste apertures omitted; 325 others preserved, including U9 exposed-pad windows')
