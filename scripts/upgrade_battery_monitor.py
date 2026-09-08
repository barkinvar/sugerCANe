"""One-time revision-A correction: sense switched battery output at R23."""
from pathlib import Path
import shutil
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
backup=ROOT/'reports/revisions/before_switched_battery_monitor/FRC_Sensor_CAN.kicad_pcb'
backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copyfile(path,backup)
b=p.LoadBoard(str(path))
fp=b.FindFootprintByReference('R23')
pad=next(pad for pad in fp.Pads() if pad.GetNumber()=='1')
assert pad.GetNetname()=='VIN_PROT', 'Correction already applied or unexpected input board'
remove=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) or t.GetNetname()!='VIN_PROT' or t.GetLayer()!=p.F_Cu:continue
 a=t.GetStart();z=t.GetEnd()
 if 48.9<=p.ToMM(a.x)<=53.1 and 48.9<=p.ToMM(z.x)<=53.1 and 36.7<=p.ToMM(a.y)<=37.1 and 36.7<=p.ToMM(z.y)<=37.1:remove.append(t)
assert len(remove)==2,len(remove)
for t in remove:b.Remove(t)
pad.SetNet(b.GetNetsByName()['SENSOR_VBAT'])
b.BuildConnectivity();p.SaveBoard(str(path),b)
print('R23 now senses SENSOR_VBAT; removed its two old VIN_PROT branch tracks. New route required.')
