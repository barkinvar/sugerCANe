"""Verify contracted compact placement and transformed critical copper identity."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,math,argparse
import pcbnew as p
from layout_contract import CONTRACT,WIDTH,HEIGHT,BOTTOM_REFERENCES
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',type=Path,default=R/'hardware/FRC_Sensor_CAN.kicad_pcb');ap.add_argument('--output',type=Path,default=R/'reports/compact/layout_verification.json');args=ap.parse_args()
sha=lambda data:hashlib.sha256(data).hexdigest()
def baseline(path):
 return subprocess.check_output(['git','show',CONTRACT['baseline_commit']+':current/'+path],cwd=R)
unchanged=['hardware/design/circuit.json','hardware/design/circuit.py','firmware/src/power.c','hardware/FRC_Sensor_CAN.kicad_dru']
unchanged += [str(f.relative_to(R)) for f in sorted((R/'hardware').glob('*.kicad_sch'))]
for file in unchanged:assert (R/file).read_bytes()==baseline(file),('Electrical source changed',file)
project=json.loads(args.board.with_suffix('.kicad_pro').read_text())
reference_project=json.loads(baseline('hardware/FRC_Sensor_CAN.kicad_pro'))
fabrication_changes=CONTRACT.get('fabrication_rule_overrides',{})
assert set(fabrication_changes)<= {'min_through_hole_diameter'}
for key,change in fabrication_changes.items():
 assert key=='min_through_hole_diameter' and change['baseline_mm']==.3 and change['value_mm']==.2
 assert reference_project['board']['design_settings']['rules'][key]==change['baseline_mm']
 assert project['board']['design_settings']['rules'][key]==change['value_mm']
 project['board']['design_settings']['rules'][key]=change['baseline_mm']
assert project==reference_project,'Unreviewed native project rule or configuration change'
with tempfile.NamedTemporaryFile(suffix='.kicad_pcb') as f:
 f.write(baseline('hardware/FRC_Sensor_CAN.kicad_pcb'));f.flush();old=p.LoadBoard(f.name)
new=p.LoadBoard(str(args.board))
for via in new.GetTracks():
 if isinstance(via,p.PCB_VIA):
  assert p.ToMM(via.GetDrillValue())>=.2-1e-6
  assert p.ToMM(via.GetWidth(p.F_Cu)-via.GetDrillValue())/2>=.15-1e-6,'Via annulus below 0.15 mm'
oldfp={f.GetReference():f for f in old.GetFootprints()};newfp={f.GetReference():f for f in new.GetFootprints()}
assert set(oldfp)==set(newfp)==set(CONTRACT['placements'])
changes=[]
for ref,f in newfp.items():
 before=oldfp[ref];spec=CONTRACT['placements'][ref]
 oldpos=list(p.ToMM(before.GetPosition()));newpos=list(p.ToMM(f.GetPosition()))
 assert f.IsFlipped()==(spec['side']=='bottom'),(ref,'side')
 assert math.dist(newpos,spec['at_mm'])<1e-6 and abs(f.GetOrientationDegrees()-spec['rotation_deg'])<1e-6,(ref,'placement')
 assert f.GetFPIDAsString()==before.GetFPIDAsString() and f.GetValue()==before.GetValue(),ref
 # Apply the new rigid pose to a baseline footprint and compare native copper.
 expected=p.FOOTPRINT(before)
 if expected.IsFlipped()!=f.IsFlipped():expected.Flip(expected.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
 expected.SetOrientationDegrees(f.GetOrientationDegrees());expected.SetPosition(f.GetPosition())
 def pads(fp):
  return sorted((d.GetNumber(),d.GetNetname(),d.GetShape(),tuple(round(x,6) for x in p.ToMM(d.GetPosition())),tuple(round(x,6) for x in p.ToMM(d.GetSize())),tuple(round(x,6) for x in p.ToMM(d.GetDrillSize())),round(d.GetOrientationDegrees()%180,6),tuple(d.GetLayerSet().Seq())) for d in fp.Pads())
 assert pads(f)==pads(expected),(ref,'pad geometry or net identity')
 changes.append(dict(reference=ref,before_mm=oldpos,after_mm=newpos,side=spec['side']))
old_labels={t.m_Uuid.AsString():t.GetNetname() for t in old.GetTracks()}
for t in new.GetTracks():
 uid=t.m_Uuid.AsString()
 if uid in old_labels:assert t.GetNetname()==old_labels[uid],('Retained copper net changed',uid)
transforms={n:t for t in CONTRACT['critical_route_transforms'] for n in t['nets']}
def signature(t,transform=False):
 net=t.GetNetname();spec=transforms[net]
 def point(pos):
  x,y=p.ToMM(pos)
  if transform:x,y=spec['x_scale']*x+spec['x_offset_mm'],y+spec['y_offset_mm']
  return round(x,5),round(y,5)
 if isinstance(t,p.PCB_VIA):return (net,'via',point(t.GetPosition()),round(p.ToMM(t.GetWidth(p.F_Cu)),6),round(p.ToMM(t.GetDrillValue()),6))
 layer=(p.B_Cu if spec['side']=='bottom' else p.F_Cu) if transform else t.GetLayer()
 return(net,'track',layer,tuple(sorted([point(t.GetStart()),point(t.GetEnd())])),round(p.ToMM(t.GetWidth()),6))
old_routes=sorted(signature(t,True) for t in old.GetTracks() if t.GetNetname() in transforms)
new_routes=sorted(signature(t) for t in new.GetTracks() if t.GetNetname() in transforms)
assert old_routes==new_routes,'Clock/converter copper differs beyond its declared rigid transform'
report=dict(result='PASS',variant=CONTRACT['variant'],baseline_commit=CONTRACT['baseline_commit'],
 baseline_size_mm=[52,74],size_mm=[WIDTH,HEIGHT],saved_area_mm2=52*74-WIDTH*HEIGHT,
 bounding_area_reduction_percent=100*(1-WIDTH*HEIGHT/(52*74)),bottom_references=sorted(BOTTOM_REFERENCES),
 placement_changes=changes,unchanged_electrical_sources={f:sha((R/f).read_bytes()) for f in unchanged},
 fabrication_rule_changes=fabrication_changes,minimum_via_annulus_mm=.15,
 project_sha256=sha(args.board.with_suffix('.kicad_pro').read_bytes()),
 preserved_critical_nets=sorted(transforms),preserved_critical_tracks_and_vias=len(old_routes),critical_route_transforms=CONTRACT['critical_route_transforms'],
 board_sha256=sha(args.board.read_bytes()),
 limitations='Checks nominal layout/electrical identity and rigidly transformed critical copper. Supply interconnects are rerouted and independently DC-screened. Native DRC, routing style, exported copper checks and physical qualification remain separate.')
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('PASS compact layout:',WIDTH,'x',HEIGHT,'mm;',len(BOTTOM_REFERENCES),'bottom parts;',len(old_routes),'critical copper items preserved')
