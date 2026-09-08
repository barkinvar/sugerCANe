"""Check exact scope of the purchasing variant against a frozen Rev B signature."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import sexpdata as sx
R=Path(__file__).resolve().parents[1]
def tag(x,t):return isinstance(x,list) and x and str(x[0])==t
def child(x,t):return next((c for c in x if tag(c,t)),None)
def digest(x):return hashlib.sha256(sx.dumps(x).encode()).hexdigest()
def signature(root):
    b=sx.loads((root/'hardware/FRC_Sensor_CAN.kicad_pcb').read_text())
    tracks=[x for x in b if isinstance(x,list) and x and str(x[0]) in ('segment','arc','via','zone')]
    pads={}
    for f in b:
        if not tag(f,'footprint'):continue
        ref=next(q[2] for q in f if tag(q,'property') and q[1]=='Reference')
        pads[ref]=digest([f[1],child(f,'at'),child(f,'layer')]+[q for q in f if tag(q,'pad')])
    firmware={}
    for sub in ['src','include','build']:
        for p in (root/'firmware'/sub).glob('*'):
            if p.is_file() and (sub!='build' or p.suffix in ('.bin','.hex','.elf')):
                firmware[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    return dict(copper_tracks_vias_zones_sha256=digest(tracks),footprint_pad_signatures=pads,
        parts=json.loads((root/'hardware/design/circuit.json').read_text())['parts'],firmware_sha256=firmware)
base_path=R/'bom/base_variant_signature.json'
if '--record-base' in sys.argv:
    assert not base_path.exists()
    base_path.write_text(json.dumps(signature(R.parent/'rev_b'),indent=2)+'\n')
base=json.loads(base_path.read_text());now=signature(R)
assert base['copper_tracks_vias_zones_sha256']==now['copper_tracks_vias_zones_sha256']
assert base['footprint_pad_signatures']==now['footprint_pad_signatures']
assert base['firmware_sha256']==now['firmware_sha256']
assert base['parts'].keys()==now['parts'].keys()
sub=json.loads((R/'bom/substitutions.json').read_text())
changed=[]
for ref,c in now['parts'].items():
    old=base['parts'][ref]
    for field in ['pins','kind','value','footprint','rated_power_W','tolerance','dielectric','temperature_coefficient_ppm_C','exclude_bom']:
        assert c.get(field)==old.get(field),(ref,field)
    if old['mpn'] in sub:
        assert c['mpn']==sub[old['mpn']][0]
        if c['kind']=='C':assert old['voltage']=='50V' and c['voltage']=='100V'
        changed.append(ref)
    else:
        assert c['mpn']==old['mpn'] and c.get('voltage')==old.get('voltage')
x=ET.parse(R/'hardware/design/schematic.net.xml')
checked=0
for c in x.findall('./components/comp'):
    ref=c.attrib['ref']
    if ref not in now['parts']:continue
    fields={f.attrib['name']:f.text or '' for f in c.findall('./fields/field')}
    assert fields.get('MPN','')==now['parts'][ref].get('mpn',''),ref
    checked+=1
report=dict(result='PASS',changed_mpn_references=changed,changed_count=len(changed),
    schematic_mpn_checked=checked,copper_tracks_vias_zones_unchanged=True,
    footprint_placement_and_pad_geometry_unchanged=True,firmware_unchanged=True,
    base_signature_sha256=hashlib.sha256(base_path.read_bytes()).hexdigest(),
    board_sha256=hashlib.sha256((R/'hardware/FRC_Sensor_CAN.kicad_pcb').read_bytes()).hexdigest(),
    scope='Scope/parity check against frozen horizontal Rev B; component equivalence is supported separately by datasheet review; not physical validation')
(R/'reports/variant_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
