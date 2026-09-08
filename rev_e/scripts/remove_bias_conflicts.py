"""Remove only DRC-identified tracks for local Rev E construction rerouting."""
from pathlib import Path
import json,pcbnew as p
R=Path(__file__).resolve().parents[1];path=R/'hardware/FRC_Sensor_CAN.kicad_pcb';b=p.LoadBoard(str(path))
keep=list(b.GetTracks());tracks={t.m_Uuid.AsString():t for t in keep};remove=set()
for v in json.loads((R/'reports/drc/construction.json').read_text())['violations']:
 if v['type'] not in ['clearance','shorting_items','solder_mask_bridge','track_dangling','via_dangling']:continue
 candidates=[tracks[i['uuid']] for i in v['items'] if i['uuid'] in tracks]
 if candidates:
  t=max(candidates,key=lambda t:max(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y)))
  assert t.GetNetname() not in ['HSE_IN','HSE_OUT','BUCK_SW','BUCK_CB','BUCK_FB','BB_SW1','BB_SW2','BB_BOOT1','BB_BOOT2','BB_COMP','BB_COMP_RC']
  remove.add(t.m_Uuid.AsString())
for uid in remove:b.RemoveNative(tracks[uid])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
print('Removed',len(remove),'conflicting/dangling track pieces; rerouting required.')
