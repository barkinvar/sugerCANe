#!/usr/bin/env python3
"""Apply checked SES path/via geometry while preserving locked critical routes."""
from pathlib import Path
import sys,json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
src=Path(sys.argv[1]) if len(sys.argv)>1 else HW/'design/routed.routes.json'
out=Path(sys.argv[2]) if len(sys.argv)>2 else HW/'routed_pass1.kicad_pcb'
r=json.loads(src.read_text());b=p.LoadBoard(sys.argv[3] if len(sys.argv)>3 else str(HW/'prerouted.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()};nets=b.GetNetsByName()
def vec(xy):return p.VECTOR2I(p.FromMM(xy[0]),p.FromMM(xy[1]))
for rec in r['placement']:
 f=fp[rec['ref']];pos=p.ToMM(f.GetPosition())
 assert max(abs(pos[i]-rec['xy'][i]) for i in range(2))<.00011,(rec,pos)
 assert abs((f.GetOrientationDegrees()-rec['angle']+180)%360-180)<.01,(rec,f.GetOrientationDegrees())
assert set(r['nets']).issubset({str(k) for k in nets.keys()})
for t in list(b.GetTracks()):
 if not t.IsLocked():b.Remove(t)
protected=len(b.GetTracks())
# Fixed traces/vias are not returned in SES. Avoid a duplicate via on an existing one.
existing={(t.GetNetname(),t.GetPosition().x,t.GetPosition().y) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)}
for rec in r['tracks']:
 for a,c in zip(rec['points'],rec['points'][1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetWidth(p.FromMM(rec['width']));t.SetLayer(p.F_Cu if rec['layer']=='F.Cu' else p.B_Cu);t.SetNet(nets[rec['net']]);b.Add(t)
for rec in r['vias']:
 xy=vec(rec['xy']);key=(rec['net'],xy.x,xy.y)
 if key in existing:continue
 t=p.PCB_VIA(b);t.SetPosition(xy);t.SetWidth(p.FromMM(rec['diameter']));t.SetDrill(p.FromMM(rec['drill']));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[rec['net']]);b.Add(t);existing.add(key)
b.BuildConnectivity();p.SaveBoard(str(out),b)
print(f'Preserved {protected} locked items; total {len(b.GetTracks())} tracks/vias -> {out}')
