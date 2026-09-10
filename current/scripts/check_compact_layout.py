"""Verify compact placement, critical copper identity and exact reviewed repairs."""
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
fabrication=CONTRACT['fabrication_options']
small_vias=0
for via in new.GetTracks():
 if isinstance(via,p.PCB_VIA):
  drill=p.ToMM(via.GetDrillValue());diameter=p.ToMM(via.GetWidth(p.F_Cu))
  assert drill>=fabrication['minimum_via_drill_mm']-1e-6
  small=abs(diameter-.5)<1e-6 and abs(drill-.3)<1e-6
  small_vias+=small
  limit=fabrication['small_via_annulus_mm'] if small else fabrication['other_via_minimum_annulus_mm']
  assert (diameter-drill)/2>=limit-1e-6,('Via annulus below reviewed size-specific requirement',diameter,drill,limit)
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
old_by_id={t.m_Uuid.AsString():signature(t,True) for t in old.GetTracks() if t.GetNetname() in transforms}
new_by_id={t.m_Uuid.AsString():signature(t) for t in new.GetTracks() if t.GetNetname() in transforms}
def freeze(value):
 return tuple(freeze(v) for v in value) if isinstance(value,list) else value
expected_routes=list(old_routes);changed_ids=set();adjusted_nets=set();adjusted_count=0
adjustments=CONTRACT.get('critical_route_adjustments',[])
for repair in adjustments:
 assert repair['net'] in transforms and repair['reason'] and repair['reviewed_from_commit']
 adjusted_nets.add(repair['net'])
 for item in repair['items']:
  uid=item['uuid'];before=freeze(item['before']);after=freeze(item['after'])
  assert uid not in changed_ids,('Duplicate critical repair',uid)
  changed_ids.add(uid)
  assert after[0]==repair['net'] and after[1]=='track'
  assert old_by_id.get(uid)==before,('Critical repair baseline differs',uid)
  assert new_by_id.get(uid)==after,('Critical repair differs from reviewed geometry',uid)
  if before is not None:
   assert before[0:3]==after[0:3],'Critical repair changed net, kind or layer'
   expected_routes.remove(before);adjusted_count+=1
  expected_routes.append(after)
assert sorted(expected_routes)==new_routes,'Clock/converter copper differs beyond declared transforms and exact repairs'
# A DC-connected GND net can still leave the boost IC with a remote return.
# Require a nearby through via in the SAME filled bottom-copper polygon as
# U8.4, also landed in the immediately adjacent In2 ground plane. Distances
# below are pad-to-via straight-line spacing, not impedance or path length.
u8_ground=next(d for d in newfp['U8'].Pads() if d.GetNumber()=='4')
bottom_ground=next(z for z in new.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.GetLayer()==p.B_Cu).GetFilledPolysList(p.B_Cu)
inner_ground=next(z for z in new.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.GetLayer()==p.In2_Cu).GetFilledPolysList(p.In2_Cu)
local_ground=[]
for via in new.GetTracks():
 if not isinstance(via,p.PCB_VIA) or via.GetNetname()!='GND':continue
 if via.GetViaType()!=p.VIATYPE_THROUGH or not {p.B_Cu,p.In2_Cu}.issubset(via.GetLayerSet().Seq()):continue
 distance=math.dist(p.ToMM(u8_ground.GetPosition()),p.ToMM(via.GetPosition()))
 if distance>3.2 or not inner_ground.Contains(via.GetPosition()):continue
 if any(bottom_ground.Contains(u8_ground.GetPosition(),i) and bottom_ground.Contains(via.GetPosition(),i) for i in range(bottom_ground.OutlineCount())):
  local_ground.append(dict(uuid=via.m_Uuid.AsString(),at_mm=list(p.ToMM(via.GetPosition())),pad_to_via_spacing_mm=distance,
   diameter_mm=p.ToMM(via.GetWidth(p.F_Cu)),drill_mm=p.ToMM(via.GetDrillValue()),through_via=True))
assert local_ground,'Boost ground return lacks a local via in its bottom copper island and In2 plane'
assert small_vias==fabrication['small_via_count'],'Reviewed small-via inventory changed'
report=dict(result='PASS',variant=CONTRACT['variant'],baseline_commit=CONTRACT['baseline_commit'],
 baseline_size_mm=[52,74],size_mm=[WIDTH,HEIGHT],saved_area_mm2=52*74-WIDTH*HEIGHT,
 bounding_area_reduction_percent=100*(1-WIDTH*HEIGHT/(52*74)),bottom_references=sorted(BOTTOM_REFERENCES),
 placement_changes=changes,unchanged_electrical_sources={f:sha((R/f).read_bytes()) for f in unchanged},
 fabrication_rule_changes=fabrication_changes,fabrication_options=fabrication,minimum_via_annulus_mm=.1,
 project_sha256=sha(args.board.with_suffix('.kicad_pro').read_bytes()),
 preserved_critical_nets=sorted(set(transforms)-adjusted_nets),verified_critical_nets=sorted(transforms),
 preserved_critical_tracks_and_vias=len(old_routes)-adjusted_count,verified_critical_tracks_and_vias=len(new_routes),
 critical_route_adjustments=adjustments,critical_route_transforms=CONTRACT['critical_route_transforms'],
 boost_local_ground=dict(pad='U8.4',maximum_spacing_mm=3.2,vias=local_ground,scope='Same filled bottom-copper polygon and adjacent In2 GND plane; nominal geometry only, not return-path impedance qualification.'),
 board_sha256=sha(args.board.read_bytes()),
 limitations='Checks nominal layout/electrical identity, rigidly transformed critical copper and exact reviewed local repairs. Supply interconnects are rerouted and independently DC-screened. Native DRC, routing style, exported copper checks and physical qualification remain separate.')
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('PASS compact layout:',WIDTH,'x',HEIGHT,'mm;',len(BOTTOM_REFERENCES),'bottom parts;',len(old_routes)-adjusted_count,'critical copper items preserved;',len(changed_ids),'exact repaired/added items verified')
