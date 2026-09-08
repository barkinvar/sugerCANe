"""Final-native-board checks for assembly, selector and critical-route intent."""
from pathlib import Path
import json,math,collections,hashlib
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'))
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
fps={f.GetReference():f for f in b.GetFootprints()}
assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<1e-6
fitted=[r for r,c in parts.items() if not c.get('exclude_bom')]
assert len(fitted)==89 and all(not fps[r].IsFlipped() for r in fitted)
assert len([r for r in fitted if r.startswith('R')])==33
assert len([r for r in fitted if r.startswith('C')])==29
def pads(ref):return {d.GetNumber():d for d in fps[ref].Pads() if d.GetNumber()}
def nets(ref):return {n:d.GetNetname() for n,d in pads(ref).items()}
assert nets('U3')['1']=='VIN_PROT' and nets('U3')['2']=='GND' and nets('U3')['3'].startswith('unconnected-')
assert nets('U4')['3']=='V5_INTERNAL' and nets('U4')['4'].startswith('unconnected-')
selectors=[]
for ch in range(1,4):
 a=f'JP{ch}01';z=f'JP{ch}03'
 assert nets(a)=={'1':'SENSOR_5V','2':f'VPORT{ch}','3':'SENSOR_VBAT'}
 assert nets(z)=={'1':f'PULL_PORT{ch}','2':f'SIG{ch}','3':f'BIAS_GND{ch}'}
 for ref in (a,z):
  pp=pads(ref);xx=[p.ToMM(pp[str(n)].GetPosition().x) for n in (1,2,3)]
  assert xx==sorted(xx) and abs(xx[1]-xx[0]-1.5)<1e-6
  assert all(not d.IsOnLayer(p.F_Paste) for d in pp.values())
  selectors.append(dict(reference=ref,pads_left_to_right=list(nets(ref).values())))
assert all(not d.IsOnLayer(p.F_Paste) for d in pads('JP2').values())
service=pads('J8');mapping={'1':'NRST','2':'UART_RX','3':'UART_TX','4':'SWCLK','5':'SWDIO','6':'+3V3','7':'GND','8':'GND','9':'BOOT0','10':'GND'}
assert nets('J8')==mapping
for n,d in service.items():
 assert not d.IsOnLayer(p.F_Paste) and abs(p.ToMM(d.GetSize().x)-.7874)<1e-6
expected=[(21.46,6.385),(22.73,6.385),(24,6.385),(25.27,6.385),(26.54,6.385),(26.54,5.115),(25.27,5.115),(24,5.115),(22.73,5.115),(21.46,5.115)]
for i,xy in enumerate(expected,1):assert all(abs(a-z)<1e-6 for a,z in zip(p.ToMM(service[str(i)].GetPosition()),xy))
tracks=collections.defaultdict(list);vias=collections.Counter()
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vias[t.GetNetname()]+=1
 else:tracks[t.GetNetname()].append(t)
critical={}
for net in ['HSE_IN','HSE_OUT','BUCK_SW','BUCK_CB','BUCK_FB']:
 tt=tracks[net];assert tt,net
 length=sum(p.ToMM(t.GetLength()) for t in tt)
 assert vias[net]==0 and all(t.GetLayer()==p.F_Cu for t in tt),(net,vias[net])
 assert length<30,(net,length)
 critical[net]=dict(total_track_length_mm=length,vias=vias[net],all_top=True)
widths={n:dict(total_track_length_mm=sum(p.ToMM(t.GetLength()) for t in tt),minimum_width_mm=min(p.ToMM(t.GetWidth()) for t in tt),via_count=vias[n]) for n,tt in tracks.items() if n in ('VIN_RAW','VIN_FUSED','VIN_PROT','V5_INTERNAL','SENSOR_5V','SENSOR_VBAT','VPORT1','VPORT2','VPORT3')}
for r in ['J1','J2','J3','J4','J5','J6']:
 f=fps[r];assert f.GetOrientationDegrees()==(180 if r in ['J1','J2','J3'] else 0)
 assert all(abs(p.ToMM(d.GetDrillSize().x)-1.1)<1e-6 for d in f.Pads())
for record in json.loads((R/'hardware/library/3d/vendor_connectors.json').read_text()):
 for path,sha in [('source_file','vendor_sha256'),('model_file','model_sha256')]:assert hashlib.sha256((R/record[path]).read_bytes()).hexdigest()==record[sha]
report=dict(result='PASS',fitted_top_parts=89,resistors=33,capacitors=29,board_thickness_mm=1.6,selectors=selectors,service_mapping=mapping,critical_routes=critical,power_net_geometry=widths,limitations='Track geometry inventory is not a thermal, impedance or trace-drop qualification. VIN_PROT includes the narrow low-current U3 enable branch; 3D and programming checks are nominal geometry, not physical fit.')
(R/'reports/board_constraints.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
