"""Independent exported schematic / board / model connectivity and metadata audit.
Run with kicad-python after KiCad has exported a fresh XML netlist.
"""
from pathlib import Path
from collections import defaultdict
import json,xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
x=ET.parse(ROOT/'hardware/design/schematic.net.xml').getroot()
sch={};errors=[]
for net in x.findall('./nets/net'):
    for node in net.findall('node'):
        if node.attrib['ref'].startswith('#'):continue
        key=(node.attrib['ref'],node.attrib['pin'])
        assert key not in sch,key
        sch[key]=net.attrib['name']
b=p.LoadBoard(str(ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'))
board=defaultdict(list)
for f in b.GetFootprints():
    ref=f.GetReference()
    if ref.startswith('H'):continue
    if ref not in parts:errors.append(f'Unexpected PCB footprint {ref}');continue
    c=parts[ref]
    if f.GetValue()!=c['value']:errors.append(f'{ref}: PCB value differs')
    if f.GetFPIDAsString()!=c['footprint']:errors.append(f'{ref}: footprint differs')
    if f.GetFieldText('MPN')!=c.get('mpn',''):errors.append(f'{ref}: MPN differs')
    for pad in f.Pads():
        if pad.GetNumber():board[(ref,pad.GetNumber())].append(pad.GetNetname())
for ref,c in parts.items():
    for pin,net in c['pins'].items():
        k=(ref,pin)
        for source,nets in [('schematic',[sch.get(k)]),('PCB',board.get(k,[]))]:
            if not nets:errors.append(f'{ref}.{pin}: missing {source} pad');continue
            for actual in nets:
                correct=actual==net if net else actual is None or actual=='' or actual.startswith('unconnected-')
                if not correct:errors.append(f'{ref}.{pin}: {source} {actual!r} != model {net!r}')
for k in board:
    if k[0] not in parts or k[1] not in parts[k[0]]['pins']:errors.append(f'Unexpected PCB pad {k}')
for comp in x.findall('./components/comp'):
    ref=comp.attrib['ref']
    if ref.startswith('#'):continue
    if ref not in parts:errors.append(f'Unexpected schematic component {ref}');continue
    if comp.findtext('value')!=parts[ref]['value']:errors.append(f'{ref}: schematic value differs')
    if comp.findtext('footprint')!=parts[ref]['footprint']:errors.append(f'{ref}: schematic footprint differs')
    fields={f.attrib['name']:f.text or '' for f in comp.findall('./fields/field')}
    if fields.get('MPN','')!=parts[ref].get('mpn',''):errors.append(f'{ref}: schematic MPN differs')
result={'physical_components':len(parts),'model_pin_count':sum(len(c['pins']) for c in parts.values()),
        'unique_named_nets':len({n for c in parts.values() for n in c['pins'].values() if n}),
        'schematic_nodes':len(sch),'board_numbered_pads':sum(map(len,board.values())),
        'errors':errors,'pass':not errors}
out=ROOT/'reports/design_parity.json';out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));raise SystemExit(bool(errors))
