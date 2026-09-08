"""Create concise factory instructions and an upload packet, without submitting it."""
from pathlib import Path
import csv
import json
import runpy
import shutil
import zipfile
R=Path(__file__).resolve().parents[1]
# Shared typography/parser also rebuilds the up-to-date engineering handbook.
ns=runpy.run_path(str(R/'scripts/build_handbook.py'))
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.pagesizes import A4
story=[Paragraph('FRC Sensor CAN B-2 · Factory instructions',ns['styles']['chapter'])]
story+=ns['convert'](R/'docs/FACTORY_ORDER.md')
story += [PageBreak(),Paragraph('Reviewed component substitutions',ns['styles']['chapter'])]
story+=ns['convert'](R/'docs/PART_CHANGES.md')
SimpleDocTemplate(str(R/'output/documentation/Factory_RevB2.pdf'),pagesize=A4,
    leftMargin=42,rightMargin=42,topMargin=48,bottomMargin=43).build(story,onFirstPage=ns['page'],onLaterPages=ns['page'])

readme='''FRC SENSOR CAN — REV B-2 PROTOTYPE QUOTATION / BUILD DATA

Requested service: PCB fabrication plus full turnkey top-side SMT and THT assembly.
Finished PCB: 60 x 68 mm, 2 layers, 1.6 mm FR-4, 1 oz finished copper, ENIG.
Per unit: 128 SMT components + 16 THT components; ten configuration shunts bagged.
All fitted MPNs are explicit. The MCU and horizontal Weidmuller terminals require
global sourcing; incomplete JLCPCB automatic matching must not silently omit parts.

Read output/documentation/Factory_RevB2.pdf before quoting or panelizing. The supplied Gerbers describe
the single functional PCB. Factory processing rails/fiducials, component sourcing,
library rotation matching and assembly-process review remain to be completed.
Do not add tooling holes inside the routed board. THT terminal overhang requires
depaneling before terminal installation or an equivalent supporting fixture.

output/assembly/CPL_JLCPCB.csv: lower-left PCB origin, mm, +X right, +Y up, all Top. Through-hole
centers are offset from native pin-one origins. pad_coordinates.csv is authoritative
for electrical pad locations and orientation matching. No pogo connector is fitted.

Quote quantities 2, 5, 10 and 25 where the service permits. Quote separately:
PCB/ENIG/panel tooling, components and attrition, SMT/THT labor, hidden-pad inspection,
optional programming/basic rail tests, shipping and destination import charges.
No destination, shipping account or payment information is supplied in this packet.

Programming images: firmware/build/sensor_can.hex, or .bin at 0x08000000.
Use the custom TC2050 electrical wiring in docs/WIRING.md, not an assumed stock cable.
Factory programming and functional qualification are not implied by placement data.
The board is unbuilt and has no physical test results. Ship all shunts loose.

This packet has not been uploaded to a manufacturer and no order has been placed.
'''
(R/'order/READ_ME_FIRST.txt').write_text(readme)
files={
    'order/READ_ME_FIRST.txt':'READ_ME_FIRST.txt',
    'order/RevB2_Gerbers.zip':'RevB2_Gerbers.zip',
    'bom/BOM_turnkey.csv':'BOM_turnkey.csv','bom/BOM_JLCPCB.csv':'BOM_JLCPCB.csv',
    'bom/ACCESSORIES.csv':'ACCESSORIES.csv',
    'output/assembly/CPL_JLCPCB.csv':'CPL_JLCPCB.csv',
    'output/assembly/pad_coordinates.csv':'pad_coordinates.csv',
    'output/assembly/coordinate_offsets.csv':'coordinate_offsets.csv',
    'output/assembly/top_assembly.pdf':'top_assembly.pdf',
    'output/assembly/bottom_markings.pdf':'bottom_markings.pdf',
    'output/assembly/schematic.pdf':'schematic.pdf',
    'output/assembly/interactive_bom.html':'interactive_bom.html',
    'output/documentation/Factory_RevB2.pdf':'Factory_RevB2.pdf',
    'output/documentation/BOM_RevB2.pdf':'BOM_RevB2.pdf',
    'output/documentation/Mechanical_RevB2_1to1.pdf':'Mechanical_RevB2_1to1.pdf',
    'output/mechanical/FRC_Sensor_CAN.step':'FRC_Sensor_CAN_RevB2.step',
    'docs/WIRING.md':'WIRING.md','docs/FACTORY_ORDER.md':'FACTORY_ORDER.md',
    'docs/PART_CHANGES.md':'PART_CHANGES.md',
    'docs/CAN_PROTOCOL.md':'CAN_PROTOCOL.md',
    'docs/TIMING.md':'TIMING.md',
    'firmware/README.md':'PROGRAMMING.md',
    'firmware/build/sensor_can.hex':'sensor_can.hex','firmware/build/sensor_can.bin':'sensor_can.bin',
    'sources/weidmuller_horizontal_1824420000.pdf':'connector_1824420000.pdf',
    'sources/weidmuller_horizontal_1824430000.pdf':'connector_1824430000.pdf',
}
files={path:(name if path.startswith('order/') else path) for path,name in files.items()}
import hashlib
hashes=[]
with zipfile.ZipFile(R/'order/RevB2_Factory_Upload.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path,name in files.items():
        p=R/path;z.write(p,name)
        hashes.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {name}')
    z.writestr('SHA256SUMS.txt','\n'.join(hashes)+'\n')
with zipfile.ZipFile(R/'order/RevB2_Factory_Upload.zip') as z:
    import posixpath
    import re
    assert z.testzip() is None
    names = set(z.namelist())
    for line in z.read('SHA256SUMS.txt').decode().splitlines():
        digest, name = line.split('  ', 1)
        assert hashlib.sha256(z.read(name)).hexdigest() == digest, name
    for name in names:
        if not name.endswith('.md'):
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', z.read(name).decode()):
            if re.match(r'^[a-z]+:|^#', target):
                continue
            destination = posixpath.normpath(posixpath.join(posixpath.dirname(name), target.split('#')[0]))
            assert destination in names, (name, target)
print(R/'order/RevB2_Factory_Upload.zip')
