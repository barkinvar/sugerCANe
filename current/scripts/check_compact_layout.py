"""Verify compact placement and electrical/critical-route preservation."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
import pcbnew as p
from layout_contract import CONTRACT,WIDTH,HEIGHT,BOTTOM_REFERENCES
R=Path(__file__).resolve().parents[1]
sha=lambda data:hashlib.sha256(data).hexdigest()
def baseline(path):
 return subprocess.check_output(['git','show',CONTRACT['baseline_commit']+':current/'+path],cwd=R)
unchanged=['hardware/design/circuit.json','hardware/design/circuit.py','firmware/src/power.c','hardware/FRC_Sensor_CAN.kicad_pro','hardware/FRC_Sensor_CAN.kicad_dru']
unchanged += [str(f.relative_to(R)) for f in sorted((R/'hardware').glob('*.kicad_sch'))]
for file in unchanged:assert (R/file).read_bytes()==baseline(file),('Electrical source changed',file)
with tempfile.NamedTemporaryFile(suffix='.kicad_pcb') as f:
 f.write(baseline('hardware/FRC_Sensor_CAN.kicad_pcb'));f.flush();old=p.LoadBoard(f.name)
new=p.LoadBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'))
oldfp={f.GetReference():f for f in old.GetFootprints()};newfp={f.GetReference():f for f in new.GetFootprints()}
assert set(oldfp)==set(newfp)
expected_shift={r for r,f in oldfp.items() if p.ToMM(f.GetPosition().y)>=55}
allowed=expected_shift|{'C101'}
changes=[]
for ref,f in newfp.items():
 before=oldfp[ref];oldpos=list(p.ToMM(before.GetPosition()));newpos=list(p.ToMM(f.GetPosition()))
 assert f.IsFlipped()==(ref in BOTTOM_REFERENCES),(ref,'side')
 assert f.GetFPIDAsString()==before.GetFPIDAsString() and f.GetValue()==before.GetValue()
 assert [(d.GetNumber(),d.GetNetname()) for d in f.Pads()]==[(d.GetNumber(),d.GetNetname()) for d in before.Pads()],ref
 if ref not in allowed:
  assert oldpos==newpos and f.GetOrientationDegrees()==before.GetOrientationDegrees(),(ref,'Unexpected placement change')
 else:changes.append(dict(reference=ref,before_mm=oldpos,after_mm=newpos,side='bottom' if f.IsFlipped() else 'top'))
critical={'HSE_IN','HSE_OUT','HSE_XTAL_OUT','BUCK_SW','BUCK_CB','BUCK_FB','BOOST_SW','BOOST_FB','BOOST_COMP','BOOST_COMP_RC','VIN_RAW','VIN_FUSED','VIN_PROT','V5_INTERNAL','BOOST_12V'}
def signature(t):
 if isinstance(t,p.PCB_VIA):return (t.GetNetname(),'via',tuple(p.ToMM(t.GetPosition())),p.ToMM(t.GetWidth(p.F_Cu)),p.ToMM(t.GetDrillValue()))
 return(t.GetNetname(),'track',t.GetLayer(),tuple(p.ToMM(t.GetStart())),tuple(p.ToMM(t.GetEnd())),p.ToMM(t.GetWidth()))
old_routes=sorted(signature(t) for t in old.GetTracks() if t.GetNetname() in critical)
new_routes=sorted(signature(t) for t in new.GetTracks() if t.GetNetname() in critical)
assert old_routes==new_routes,'Critical clock/converter/input-power copper changed'
report=dict(result='PASS',variant=CONTRACT['variant'],baseline_commit=CONTRACT['baseline_commit'],
 baseline_size_mm=[52,74],size_mm=[WIDTH,HEIGHT],saved_area_mm2=52*74-WIDTH*HEIGHT,
 bounding_area_reduction_percent=100*(1-WIDTH*HEIGHT/(52*74)),bottom_references=sorted(BOTTOM_REFERENCES),
 placement_changes=changes,unchanged_electrical_sources={f:sha((R/f).read_bytes()) for f in unchanged},
 preserved_critical_nets=sorted(critical),preserved_critical_tracks_and_vias=len(old_routes),
 board_sha256=sha((R/'hardware/FRC_Sensor_CAN.kicad_pcb').read_bytes()),
 limitations='Checks nominal layout/electrical identity. Native DRC, routing style, independent exported copper checks and physical qualification are separate.')
(R/'reports/compact/layout_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS compact layout:',WIDTH,'x',HEIGHT,'mm;',len(BOTTOM_REFERENCES),'bottom parts;',len(old_routes),'critical copper items preserved')
