"""One-time Rev A refinement: move VOUT feedback pickup outside the inductor body.

The saved native PCB is authoritative. This historical transform is not part of
the normal release validator and refuses an unexpected starting geometry.
"""
from pathlib import Path
import shutil
import hashlib
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(path))
def xy(v):return tuple(round(n,6) for n in p.ToMM(v))
def point(v):return p.VECTOR2I(p.FromMM(v[0]),p.FromMM(v[1]))
targets=[
    ((29.725,26.0),(27.7983,26.0),p.F_Cu),
    ((27.7909,25.9926),(27.5987,25.9926),p.F_Cu),
    ((27.7983,26.0),(27.7909,25.9926),p.F_Cu),
    ((27.5987,20.1771),(27.5987,25.9926),p.B_Cu),
    ((25.8109,18.3893),(27.5987,20.1771),p.B_Cu),
]
found=[];via=None
for t in b.GetTracks():
    if t.GetNetname()!='V5_INTERNAL':continue
    if isinstance(t,p.PCB_VIA):
        if xy(t.GetPosition())==(27.5987,25.9926):via=t
    elif (xy(t.GetStart()),xy(t.GetEnd()),t.GetLayer()) in targets:found.append(t)
assert len(found)==len(targets) and via is not None,'Unexpected starting layout or refinement already applied'
backup=ROOT/'hardware/before_feedback_pickup.kicad_pcb'
if backup.exists():
    assert hashlib.sha256(backup.read_bytes()).digest()==hashlib.sha256(path.read_bytes()).digest(),'Backup differs from current board; inspect before repeating'
else:
    shutil.copy2(path,backup)
via_nets={t.m_Uuid.AsString():t.GetNetname() for t in b.GetTracks() if isinstance(t,p.PCB_VIA)}
net=via.GetNetCode()
for t in found:b.Delete(t)
via.SetPosition(point((30.5,20)))
for a,z,layer in [
    ((30.5,20),(32.525,20),p.F_Cu),
    ((25.8109,18.3893),(28.8893,18.3893),p.B_Cu),
    ((28.8893,18.3893),(30.5,20),p.B_Cu),
]:
    t=p.PCB_TRACK(b);t.SetNetCode(net);t.SetLayer(layer);t.SetWidth(p.FromMM(.5))
    t.SetStart(point(a));t.SetEnd(point(z));b.Add(t)
p.ZONE_FILLER(b).Fill(b.Zones())
assert via_nets=={t.m_Uuid.AsString():t.GetNetname() for t in b.GetTracks() if isinstance(t,p.PCB_VIA)},'Refill changed an existing via net'
p.SaveBoard(str(path),b)
print('Moved VOUT sensing pickup to C13 positive terminal, outside the inductor body; zones refilled.')
