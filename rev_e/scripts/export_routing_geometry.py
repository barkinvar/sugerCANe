from pathlib import Path
import json,sys
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(ROOT/(sys.argv[1] if len(sys.argv)>1 else 'hardware/routed_pass1.kicad_pcb')))
obs=[];holes=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  bb=pad.GetBoundingBox();layers=[i for i,l in enumerate([p.F_Cu,p.B_Cu]) if pad.IsOnLayer(l)]
  obs.append({'type':'rect','reference':f.GetReference(),'net':pad.GetNetname(),'layers':layers,'smd':pad.GetAttribute()==p.PAD_ATTRIB_SMD,'bounds':[p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())]})
  drill=p.ToMM(pad.GetDrillSize());pos=p.ToMM(pad.GetPosition())
  if max(drill)>0:holes.append({'xy':list(pos),'radius':max(drill)/2})
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  pos=list(p.ToMM(t.GetPosition()));obs.append({'type':'circle','net':t.GetNetname(),'layers':[0,1],'xy':pos,'radius':p.ToMM(t.GetWidth(p.F_Cu))/2})
  holes.append({'xy':pos,'radius':p.ToMM(t.GetDrillValue())/2})
 else:
  obs.append({'type':'line','net':t.GetNetname(),'layers':[0 if t.GetLayer()==p.F_Cu else 1],'a':list(p.ToMM(t.GetStart())),'b':list(p.ToMM(t.GetEnd())),'width':p.ToMM(t.GetWidth())})
(ROOT/'hardware/design/routing_geometry.json').write_text(json.dumps({'obstacles':obs,'holes':holes}))
