"""Create E from the preserved D2 native board, retaining upper/critical routing.
One-time construction helper; do not run over a subsequently routed E board.
"""
from pathlib import Path
import json
import pcbnew as p
R=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(R.parent/'rev_d2/hardware/FRC_Sensor_CAN.kicad_pcb'))
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
footprints=list(b.GetFootprints())
keep=footprints+list(b.GetTracks())+list(b.GetDrawings())+list(b.Zones())
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def stretch(v):return p.VECTOR2I(v.x,v.y+(p.FromMM(6) if v.y>p.FromMM(50.5) else 0))
# Add a 6 mm strip for electronic bias; sensor terminals retain their spacing.
for f in footprints:
 if f.GetReference() in ['JP103','JP203','JP303']:b.RemoveNative(f);continue
 f.SetPosition(stretch(f.GetPosition()))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):t.SetPosition(stretch(t.GetPosition()))
 else:t.SetStart(stretch(t.GetStart()));t.SetEnd(stretch(t.GetEnd()))
for d in b.GetDrawings():
 if isinstance(d,p.PCB_SHAPE):d.SetStart(stretch(d.GetStart()));d.SetEnd(stretch(d.GetEnd()))
 elif isinstance(d,p.PCB_TEXT):
  if any(x in d.GetText() for x in ['NPN','PNP','BIAS']):keep.append(d);b.RemoveNative(d);continue
  d.SetPosition(stretch(d.GetPosition()));d.SetText(d.GetText().replace('D-2','E'))
for zone in b.Zones():
 outline=zone.Outline()
 for k in range(outline.OutlineCount()):
  chain=outline.Outline(k)
  for n in range(chain.PointCount()):chain.SetPoint(n,stretch(chain.CPoint(n)))
for name in sorted({net for c in parts.values() for net in c['pins'].values() if net}):
 if name not in b.GetNetsByName():
  ni=p.NETINFO_ITEM(b,name);keep.append(ni);b.Add(ni)
nets=b.GetNetsByName()
# Branches whose physical termination changed are rerouted locally.
for t in list(b.GetTracks()):
 name=t.GetNetname()
 if name.startswith('VPORT'):
  b.RemoveNative(t);continue
 if name.startswith('PULL_PORT') or name.startswith('BIAS_GND'):
  t.SetNet(nets['SIG'+name[-1]])
# Disconnect the old R109 ground landing before assigning its switched drain net.
for ch in range(1,4):
 f=b.FindFootprintByReference(f'R{ch}09');pos=next(d.GetPosition() for d in f.Pads() if d.GetNumber()=='2')
 for t in list(b.GetTracks()):
  if t.GetNetname()=='GND' and ((isinstance(t,p.PCB_VIA) and t.GetPosition()==pos) or (not isinstance(t,p.PCB_VIA) and (t.GetStart()==pos or t.GetEnd()==pos))):b.RemoveNative(t)
for ref,c in parts.items():
 f=b.FindFootprintByReference(ref)
 if not f:
  f=p.FootprintLoad(str(R/'hardware/library/FRC_Sensor_CAN.pretty'),c['footprint'].split(':')[1]);assert f,ref
  keep.append(f);b.Add(f);f.SetReference(ref);f.SetFPIDAsString(c['footprint'])
  if ref=='R52':f.SetPosition(vec(45.5,57.5));f.SetOrientationDegrees(0)
  else:
   ch=int(ref[1]);off=int(ref[2:]);x=(ch-1)*16+(4 if off in [1,11] else 12)+(3.9 if ref.startswith('R') else 0)
   f.SetPosition(vec(x,53.45));f.SetOrientationDegrees(90 if ref.startswith('Q') else 0)
  f.Reference().SetVisible(False);f.Value().SetVisible(False)
 f.SetValue(c['value'])
 f.SetField('MPN',c.get('mpn',''));f.GetField('MPN').SetVisible(False)
 for pad in f.Pads():
  net=c['pins'].get(pad.GetNumber())
  if net:pad.SetNet(nets[net])
  elif pad.GetNumber() in c['pins']:pad.SetNetCode(0)
# Preserve two solid inner ground planes and refill against the modified pads.
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'),b)
print('Saved 52 x 70 mm E construction board; local routing required.')
