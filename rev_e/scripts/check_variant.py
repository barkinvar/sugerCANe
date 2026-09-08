"""Audit E against the preserved neighboring D2 checkout (development check)."""
from pathlib import Path
import json,hashlib
import pcbnew as p
R=Path(__file__).resolve().parents[1];D=R.parent/'rev_d2'
old=json.loads((D/'hardware/design/circuit.json').read_text())['parts']
new=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
removed={f'JP{ch}03' for ch in range(1,4)}
added={'R52'}|{f'{kind}{ch}{num:02}' for ch in range(1,4) for kind,num in [('Q',1),('Q',2),('R',11),('R',12)]}
assert set(old)-set(new)==removed and set(new)-set(old)==added
changed={'U5'}|{f'{kind}{ch}{num:02}' for ch in range(1,4) for kind,num in [('R',9),('R',10),('D',2)]}
for ref in set(old)&set(new)-changed:
 for key in ['pins','mpn','value','footprint','voltage','tolerance','rated_power_W','dielectric','exclude_bom']:
  assert old[ref].get(key)==new[ref].get(key),(ref,key)
critical={'HSE_IN','HSE_OUT','BUCK_SW','BUCK_CB','BUCK_FB','BB_SW1','BB_SW2','BB_BOOT1','BB_BOOT2','BB_COMP','BB_COMP_RC'}
def routes(root):
 board=p.LoadBoard(str(root/'hardware/FRC_Sensor_CAN.kicad_pcb'));tracks=list(board.GetTracks());out=[]
 for t in tracks:
  if t.GetNetname() not in critical:continue
  assert not isinstance(t,p.PCB_VIA)
  out.append((t.GetNetname(),tuple(p.ToMM(t.GetStart())),tuple(p.ToMM(t.GetEnd())),p.ToMM(t.GetWidth()),t.GetLayer()))
 return sorted(out)
assert routes(D)==routes(R)
report=dict(result='PASS',baseline='Preserved Rev D2',removed_bias_selectors=sorted(removed),added_parts=sorted(added),changed_circuit_parts=sorted(changed),critical_track_geometry_unchanged=sorted(critical),firmware_change='Rev E protocol 4, hardware 5, application 0.6.0; D2 preserved',scope='Circuit delta and named critical tracks. Native DRC/export checks separately required. Not physical qualification.')
(R/'reports/variant_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
