"""Audit D-2 against the preserved neighboring D checkout (development check)."""
from pathlib import Path
import json,hashlib
import pcbnew as p
R=Path(__file__).resolve().parents[1];D=R.parent/'rev_d'
old=json.loads((D/'hardware/design/circuit.json').read_text())['parts']
new=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
assert set(old)==set(new)
substitutions=json.loads((R/'bom/substitutions.json').read_text())
changed=[]
for ref in old:
 a,z=old[ref],new[ref]
 assert a['pins']==z['pins'],ref
 if ref in ('JP101','JP201','JP301'):
  assert a.get('exclude_bom') and not z.get('exclude_bom')
  assert z['mpn']=='M22-2010305'
  continue
 for key in ('value','footprint','tolerance','rated_power_W','dielectric','exclude_bom'):
  assert a.get(key)==z.get(key),(ref,key)
 if a['mpn']!=z['mpn']:changed.append(ref)
 if a.get('voltage')!=z.get('voltage'):
  assert a['mpn']=='CC0805KRX7R9BB104' and z['mpn']=='CL21B104KCFNNNE'
assert len(changed)==27
critical={'HSE_IN','HSE_OUT','BUCK_SW','BUCK_CB','BUCK_FB','BB_SW1','BB_SW2','BB_BOOT1','BB_BOOT2','BB_COMP','BB_COMP_RC'}
def routes(root):
 board=p.LoadBoard(str(root/'hardware/FRC_Sensor_CAN.kicad_pcb'));tracks=list(board.GetTracks());out=[]
 for t in tracks:
  if t.GetNetname() not in critical:continue
  assert not isinstance(t,p.PCB_VIA)
  out.append((t.GetNetname(),tuple(p.ToMM(t.GetStart())),tuple(p.ToMM(t.GetEnd())),p.ToMM(t.GetWidth()),t.GetLayer()))
 return sorted(out)
assert routes(D)==routes(R)
firmware=[]
for path in [*(D/'firmware/src').glob('*'),*(D/'firmware/include').glob('*'),D/'firmware/Makefile',*(D/'firmware').glob('*.ld')]:
 if not path.is_file():continue
 rel=path.relative_to(D);assert path.read_bytes()==(R/rel).read_bytes(),rel
 firmware.append(str(rel))
report=dict(result='PASS',baseline='Preserved Rev D',baseline_model_sha256=hashlib.sha256((D/'hardware/design/circuit.json').read_bytes()).hexdigest(),variant_model_sha256=hashlib.sha256((R/'hardware/design/circuit.json').read_bytes()).hexdigest(),all_114_component_pin_nets_equal=True,passive_substitutions=sorted(changed),power_headers=['JP101','JP201','JP301'],critical_track_geometry_unchanged=sorted(critical),firmware_sources_equal=firmware,scope='Passive values/footprints and component pin nets; named critical tracks; firmware sources. Sensor-area copper is rerouted and separately checked by native DRC and Gerber connectivity. Not physical qualification.')
(R/'reports/variant_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
