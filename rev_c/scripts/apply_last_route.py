from pathlib import Path
import pcbnew as p
import json,sys
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
b=p.LoadBoard(str(HW/(sys.argv[2] if len(sys.argv)>2 else 'finishing.kicad_pcb')));r=json.loads((HW/f'design/last_route_{sys.argv[1]}.json').read_text());net=b.GetNetsByName()[r['net']]
def v(pt):return p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))
points=[[*r['path'][0][:1],*r['start_exact']]]+r['path']+[[*r['path'][-1][:1],*r['goal_exact']]]
for a,c in zip(points,points[1:]):
 if a==c:continue
 if a[0]!=c[0]:
  assert a[1:]==c[1:]
  point=v(a[1:]);reuse=False
  for old in b.GetTracks():
   if isinstance(old,p.PCB_VIA) and old.GetNetname()==r['net'] and (old.GetPosition()-point).EuclideanNorm()<p.FromMM(.025):reuse=True;break
  if not reuse:
   for fp in b.GetFootprints():
    for pad in fp.Pads():
     if pad.GetNetname()==r['net'] and pad.IsOnLayer(p.F_Cu) and pad.IsOnLayer(p.B_Cu) and (pad.GetPosition()-point).EuclideanNorm()<p.FromMM(.025):reuse=True;break
  if reuse:continue
  t=p.PCB_VIA(b);t.SetPosition(v(a[1:]));t.SetWidth(p.FromMM(r['via_diameter']));t.SetDrill(p.FromMM(r['via_drill']));t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(v(a[1:]));t.SetEnd(v(c[1:]));t.SetWidth(p.FromMM(r['width']));t.SetLayer(p.F_Cu if a[0]==0 else p.B_Cu)
 t.SetNet(net);b.Add(t)
b.BuildConnectivity();p.SaveBoard(str(HW/(sys.argv[2] if len(sys.argv)>2 else 'finishing.kicad_pcb')),b)
