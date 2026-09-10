"""Audit the limited drilling/stack change against the prior compact order board."""
from pathlib import Path
import copy,hashlib,json,subprocess
import sexpdata as sx
from check_order_readiness import copper_stack, power_distribution_screen

R=Path(__file__).resolve().parents[1]
baseline='156d7dd'
path=R/'hardware/FRC_Sensor_CAN.kicad_pcb'
before=subprocess.check_output(['git','show',baseline+':current/hardware/FRC_Sensor_CAN.kicad_pcb'],cwd=R)
expected=sx.loads(before.decode());actual=sx.loads(path.read_text())
def tag(v):return str(v[0]) if isinstance(v,list) and v else ''
changed=[]
for via in [v for v in expected if tag(v)=='via']:
    fields={tag(v):v for v in via[1:] if isinstance(v,list)}
    if fields['drill'][1]==.2:
        assert fields['size'][1]==.5
        fields['drill'][1]=.3
        changed.append(str(fields['uuid'][1]))
assert len(changed)==180
setup=next(v for v in expected if tag(v)=='setup')
stack=next(v for v in setup if tag(v)=='stackup')
for layer in stack[1:]:
    if tag(layer)!='layer':continue
    fields={tag(v):v for v in layer[2:] if isinstance(v,list)}
    if layer[1] in ('In1.Cu','In2.Cu'):fields['thickness'][1]=.0175
    elif fields.get('type',[None,None])[1]=='core':fields['thickness'][1]=1.075
assert expected==actual,'PCB changed beyond 180 via drills and the specified stack thicknesses'
_,thicknesses=copper_stack(path)
assert thicknesses=={'F.Cu':.035,'In1.Cu':.0175,'In2.Cu':.0175,'B.Cu':.035}
scratch=R/'tmp/cost-defaults';scratch.mkdir(parents=True,exist_ok=True)
old=scratch/'baseline.kicad_pcb';old.write_bytes(before)
comparison={name:power_distribution_screen(board) for name,board in [('previous_1oz_all_layers',old),('current_1oz_outer_half_oz_inner',path)]}
result=dict(result='PASS limited fabrication change and DC allowances',baseline_commit=baseline,
    board_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),via_drills_changed=len(changed),
    changed_via_uuids=changed,minimum_via_drill_mm=.3,small_via_annulus_mm=.1,
    unchanged='All footprints, pad sizes/nets, component positions/rotations, trace coordinates/widths, via centers/land diameters, copper fills, keepouts, mask/paste and silkscreen',
    copper_um_by_layer={k:v*1000 for k,v in thicknesses.items()},dc_comparison=comparison,
    manufacturer_basis='https://jlcpcb.com/capabilities/Capabilities?type=1',
    limitations='0.10 mm is nominal via annulus, not remaining copper after drill/registration tolerance. DC is evaluated at 85 C with 18 um average via plating; it excludes plane/ground-return resistance, current crowding and temperature rise. Half-ounce inner copper reduces lateral heat spreading. Factory DFM and physical qualification remain required.',
    input_hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),R/'scripts/check_order_readiness.py',R/'hardware/design/layout_contract.json']})
(R/'reports/manufacturing/fabrication_options.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['result'])
for name,r in comparison.items():print(name,'boost mV',1000*r['buck_to_boost_drop_V'],'input@2A mV',1000*r['input_feed']['total_drop_V'],'max sensor mV',1000*max(v for branches in r['full_sensor_copper_drop_V_at_300mA'].values() for v in branches.values()))
