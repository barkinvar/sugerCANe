"""Final-native-board checks for assembly, selector and critical-route intent."""
from pathlib import Path
import json,math,collections,hashlib,heapq,argparse
import pcbnew as p
from layout_contract import WIDTH, HEIGHT, CONTRACT, BOTTOM_REFERENCES
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',type=Path,default=R/'hardware/FRC_Sensor_CAN.kicad_pcb');ap.add_argument('--output',type=Path,default=R/'reports/board_constraints.json');args=ap.parse_args()
b=p.LoadBoard(str(args.board))
parts=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
fps={f.GetReference():f for f in b.GetFootprints()}
assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<1e-6
fitted=[r for r,c in parts.items() if not c.get('exclude_bom')]
assert len(fitted)==140
assert {r for r in fitted if fps[r].IsFlipped()} == BOTTOM_REFERENCES
assert len([r for r in fitted if r.startswith('R')])==55
assert len([r for r in fitted if r.startswith('C')])==40
def pads(ref):return {d.GetNumber():d for d in fps[ref].Pads() if d.GetNumber()}
def nets(ref):return {n:d.GetNetname() for n,d in pads(ref).items()}
assert b.GetCopperLayerCount()==4
ground_zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
assert len(ground_zones) == 4
for zone in ground_zones:
 assert zone.GetNetname() == 'GND'
 assert abs(p.ToMM(zone.GetMinThickness())-CONTRACT['ground_pour_min_width_mm'][b.GetLayerName(zone.GetLayer())]) < 1e-6
 assert abs(p.ToMM(zone.GetLocalClearance())-.2) < 1e-6
 assert zone.GetIslandRemovalMode() == 0  # Always remove unconnected pour islands.
 expected = p.ZONE_CONNECTION_THT_THERMAL if zone.GetLayer() in (p.F_Cu,p.B_Cu) else p.ZONE_CONNECTION_FULL
 assert zone.GetPadConnection() == expected
 assert abs(p.ToMM(zone.GetThermalReliefSpokeWidth())-.3) < 1e-6
 assert abs(p.ToMM(zone.GetThermalReliefGap())-.25) < 1e-6
# Mount clearances must follow the relocated holes on every copper layer.
for ref,(x,y) in zip(('H1','H2'),CONTRACT['mounting_holes_top_left_mm']):
 areas=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='Mounting clearance '+ref]
 assert len(areas)==1,(ref,'missing named mounting clearance')
 z=areas[0]
 assert all(z.IsOnLayer(l) for l in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu))
 assert z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills()
 for a in range(0,360,15):
  dx=3.3*math.cos(math.radians(a));dy=3.3*math.sin(math.radians(a))
  assert z.Outline().Contains(p.VECTOR2I(p.FromMM(x+dx),p.FromMM(y+dy))),(ref,a)
assert abs(pads('J8')['7'].GetThermalSpokeAngleDegrees()-45) < 1e-6
edges=[d for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts]
assert len(edges)==8
arcs=[d for d in edges if d.GetShape()==p.SHAPE_T_ARC]
assert len(arcs)==4 and all(abs(p.ToMM(d.GetRadius())-1.5)<1e-5 for d in arcs)
assert 'U3' not in fps
assert nets('U8')==parts['U8']['pins'] and nets('U9')=={k:v or '' for k,v in parts['U9']['pins'].items()}
assert nets('U9')['4']=='BOOST_12V' and nets('U9')['5']=='SENSOR_12V'
assert nets('U9')['6']=='FAULT_12V_N' and nets('U5')['9']=='FAULT_12V_N'
assert nets('U7')['10']=='+3V3' and nets('U7')['11']=='GND' and not nets('U7')['13']
assert nets('U4')['3']=='POWER_5V_EN' and nets('U5')['25']=='POWER_5V_EN'
assert nets('U5')['30']=='POWER_12V_EN' and nets('Q3')['1']=='POWER_12V_EN'
assert nets('Q2')['1']=='EFUSE_INHIBIT' and nets('R70')['1']=='BOOST_12V'
assert nets('U5')['14']=='ADC_5V' and nets('U5')['15']=='ADC_12V'
assert nets('U4')['4']=='FAULT_5V_N' and nets('U5')['10']=='FAULT_5V_N'
assert 'R64' not in fps and 'NT1' not in fps
selectors=[]
for ch in range(1,4):
 a=f'JP{ch}01'
 assert f'JP{ch}03' not in fps
 assert nets(a)=={'1':'SENSOR_5V','2':f'VPORT{ch}','3':'SENSOR_12V'}
 pp=pads(a);xx=[p.ToMM(pp[str(n)].GetPosition().x) for n in (1,2,3)]
 assert xx==sorted(xx) and all(abs(xx[i+1]-xx[i]-2)<1e-6 for i in (0,1))
 assert all(d.GetAttribute()==p.PAD_ATTRIB_PTH and abs(p.ToMM(d.GetDrillSize().x)-.85)<1e-6 for d in pp.values())
 assert all(min(p.ToMM(d.GetSize()))>=1.35 for d in pp.values())
 assert all(not d.IsOnLayer(p.F_Paste) for d in pp.values())
 assert all(abs(p.ToMM(d.GetPosition().y)-CONTRACT['selector_row_y_mm'])<1e-6 for d in pp.values())
 selectors.append(dict(reference=a,pads_left_to_right=list(nets(a).values()),drill_mm=.85,nominal_annulus_mm=.25))
 assert nets(f'Q{ch}01')=={'1':f'BIAS_UP{ch}_N','2':'+3V3','3':f'BIAS_SOURCE{ch}'}
 assert nets(f'Q{ch}02')=={'1':f'BIAS_DOWN{ch}','2':'GND','3':f'BIAS_SINK{ch}'}
 assert nets(f'R{ch}10')=={'1':f'BIAS_PORT{ch}','2':f'SIG{ch}'}
 assert nets(f'R{ch}09')=={'1':f'SIG{ch}','2':f'BIAS_SINK{ch}'}
 for ref in (f'Q{ch}01',f'Q{ch}02'):
  assert math.dist(p.ToMM(fps[ref].GetPosition()),CONTRACT['placements'][ref]['at_mm'])<1e-6
assert all(not d.IsOnLayer(p.F_Paste) for d in pads('JP2').values())
service=pads('J8');mapping={'1':'NRST','2':'UART_RX','3':'UART_TX','4':'SWCLK','5':'SWDIO','6':'+3V3','7':'GND','8':'GND','9':'BOOT0','10':'GND'}
assert nets('J8')==mapping
assert parts['J8']['mpn']=='PM254V-12-10P-H85'
assert fps['J8'].GetValue()=='2x5 SERVICE SOCKET 2.54mm'
for n,d in service.items():
 assert d.GetAttribute()==p.PAD_ATTRIB_PTH and not d.IsOnLayer(p.F_Paste)
 assert abs(p.ToMM(d.GetDrillSize().x)-1.1)<1e-6 and abs(p.ToMM(d.GetSize().x)-1.7)<1e-6
for i in range(1,11):
 expected=(CONTRACT['service_origin_mm'][0]+(0 if i%2 else 2.54),CONTRACT['service_origin_mm'][1]+2.54*((i-1)//2))
 assert all(abs(a-z)<1e-6 for a,z in zip(p.ToMM(service[str(i)].GetPosition()),expected))
assert nets('D10')=={'1':'STATUS_DIN','2':'V5_INTERNAL','3':'','4':'GND'}
assert nets('U10')=={'1':'GND','2':'STATUS_DATA','3':'GND','4':'STATUS_5V_DATA','5':'V5_INTERNAL'}
assert nets('U5')['26']=='STATUS_DATA'
assert nets('R31')=={'1':'STATUS_DATA','2':'GND'} and parts['R31']['value']=='10k'
assert nets('R30')=={'1':'STATUS_5V_DATA','2':'STATUS_DIN'} and parts['R30']['value']=='330'
assert all(nets(r)=={'1':'V5_INTERNAL','2':'GND'} for r in ('C74','C75'))
assert all(abs(a-z)<1e-6 for a,z in zip(p.ToMM(fps['D10'].GetPosition()),CONTRACT['status_led_center_mm']))
assert fps['D10'].GetOrientationDegrees()==180
duct_courtyard=[g for g in fps['D10'].GraphicalItems() if g.GetLayer()==p.F_CrtYd]
assert len(duct_courtyard)==1 and duct_courtyard[0].GetShape()==p.SHAPE_T_CIRCLE
assert abs(p.ToMM(duct_courtyard[0].GetRadius())-3)<1e-6
for ref,minimum in [('D10',3),('C75',2)]:
 for d in pads(ref).values():
  bb=d.GetBoundingBox()
  edge=min(p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),WIDTH-p.ToMM(bb.GetRight()),HEIGHT-p.ToMM(bb.GetBottom()))
  assert edge>=minimum,(ref,'pad-to-board edge',edge)
edge_clearances={}
for ref,minimum in [('R101',2.19),('R103',2.04),('R203',2.04),('F1',2.06),('D102',2.09),('R22',2.07),('R109',2.02),('R104',1.97),('R30',1.69),('R31',1.69)]:
 distances=[]
 for d in pads(ref).values():
  bb=d.GetBoundingBox();distances.append(min(p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),WIDTH-p.ToMM(bb.GetRight()),HEIGHT-p.ToMM(bb.GetBottom())))
 edge_clearances[ref]=min(distances)
 assert min(distances)>=minimum,(ref,'pad-to-board edge',min(distances))
tracks=collections.defaultdict(list);vias=collections.Counter()
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vias[t.GetNetname()]+=1
 else:
  if t.GetLength()==0:continue
  assert t.GetLayer() in (p.F_Cu,p.B_Cu,p.In2_Cu),'In1 must remain an uninterrupted ground plane'
  tracks[t.GetNetname()].append(t)
critical={}
for net in ['HSE_IN','HSE_OUT','HSE_XTAL_OUT','BUCK_SW','BUCK_CB','BUCK_FB','BOOST_SW','BOOST_FB','BOOST_COMP','BOOST_COMP_RC','BOOST_SS']:
 tt=tracks[net];assert tt,net
 length=sum(p.ToMM(t.GetLength()) for t in tt)
 layer=p.F_Cu if net.startswith('HSE_') else p.B_Cu
 assert vias[net]==0 and all(t.GetLayer()==layer for t in tt),(net,vias[net])
 assert length<30,(net,length)
 critical[net]=dict(total_track_length_mm=length,vias=vias[net],layer=b.GetLayerName(layer))
# In2 is the immediate return plane for bottom switching/feedback copper.
for net in ['BUCK_SW','BUCK_CB','BUCK_FB','BOOST_SW','BOOST_FB','BOOST_COMP','BOOST_COMP_RC']:
 zones=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='Return plane under '+net]
 assert len(zones)==1,net
 zone=zones[0]
 assert zone.GetLayer()==p.In2_Cu and zone.GetDoNotAllowTracks() and zone.GetDoNotAllowVias()
 assert not zone.GetDoNotAllowZoneFills()
 for t in tracks[net]:
  margin=p.ToMM(t.GetWidth())/2+.49
  for fraction in (0,.25,.5,.75,1):
   a,z=t.GetStart(),t.GetEnd();x=a.x+round((z.x-a.x)*fraction);y=a.y+round((z.y-a.y)*fraction)
   for dx,dy in [(-margin,0),(margin,0),(0,-margin),(0,margin)]:
    assert zone.Outline().Contains(p.VECTOR2I(x+p.FromMM(dx),y+p.FromMM(dy))),net
widths={n:dict(total_track_length_mm=sum(p.ToMM(t.GetLength()) for t in tt),minimum_width_mm=min(p.ToMM(t.GetWidth()) for t in tt),via_count=vias[n]) for n,tt in tracks.items() if n in ('VIN_RAW','VIN_FUSED','VIN_PROT','V5_INTERNAL','BOOST_12V','SENSOR_5V','SENSOR_12V','VPORT1','VPORT2','VPORT3')}
for r in ['J1','J2','J3','J4','J5','J6']:
 f=fps[r];assert f.GetOrientationDegrees()==(180 if r in ['J1','J2','J3'] else 0)
 assert all(abs(p.ToMM(d.GetDrillSize().x)-1.1)<1e-6 for d in f.Pads())
for record in json.loads((R/'hardware/library/3d/vendor_connectors.json').read_text()):
 for path,sha in [('source_file','vendor_sha256'),('model_file','model_sha256')]:assert hashlib.sha256((R/record[path]).read_bytes()).hexdigest()==record[sha]
report=dict(result='PASS',fitted_top_parts=len(fitted)-len(BOTTOM_REFERENCES),fitted_bottom_parts=len(BOTTOM_REFERENCES),bottom_references=sorted(BOTTOM_REFERENCES),board_size_mm=[WIDTH,HEIGHT],resistors=55,capacitors=40,board_thickness_mm=1.6,selectors=selectors,service_mapping=mapping,critical_routes=critical,inner_service_and_monitor_routes={net:sum(p.ToMM(t.GetLength()) for t in tracks[net] if t.GetLayer()==p.In2_Cu) for net in sorted({'+3V3','UART_RX','UART_TX','BIAS_UP2_N','ADC_5V','POWER_5V_EN','BIAS_DOWN2','POWER_12V_EN','BIAS_DOWN1'})},power_net_geometry=widths,limitations='Track geometry inventory is not a thermal, impedance or trace-drop qualification. VIN_PROT includes narrow low-current enable branches; 3D and programming checks are nominal geometry, not physical fit.')
# At least six plated thermal vias outside the exposed-pad paste window.
u9=pads('U9')['9'];center=u9.GetPosition()
thermal=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND' and (t.GetPosition()-center).EuclideanNorm()<p.FromMM(3)]
assert len(thermal)>=6
for t in thermal:assert not u9.HitTest(t.GetPosition()),'Unfilled via in U9 paste pad'
assert all(abs(a-z)<1e-6 for a,z in zip(p.ToMM(u9.GetSize()),(2.4,3.1)))
paste=[d for d in fps['U9'].Pads() if not d.GetNumber() and d.IsOnLayer(p.B_Paste)]
assert len(paste)==4 and not u9.IsOnLayer(p.B_Paste)
area=0
for d in paste:
 w,h=p.ToMM(d.GetSize());radius=p.ToMM(d.GetRoundRectCornerRadius())
 area+=w*h-(4-math.pi)*radius*radius
coverage=area/(2.4*3.1)
assert .50<coverage<.65
report['improved_edge_clearances_mm']=edge_clearances
report['board_corner_radius_mm']=1.5
report['input_bias_transistor_positions_mm']={r:CONTRACT['placements'][r]['at_mm'] for r in ['Q101','Q102','Q201','Q202','Q301','Q302']}
report['edge_scope']='Pad bounding boxes to finished edges. R1/R2 retain original 1.30 mm edge clearance and local buck feedback routing. Terminals/test pads/termination bridge have intentional exceptions.'
report['efuse_assembly']=dict(exposed_pad_mm=[2.4,3.1],external_ground_thermal_vias=len(thermal),paste_windows=len(paste),paste_coverage_fraction=coverage)
# These explicit local paths prevent a future placement change from leaving
# input bypass capacitors remote from the buck, despite passing ordinary DRC.
def local_path(net,first,last,layer=p.F_Cu):
 graph=collections.defaultdict(list)
 def key(at):return (at.x,at.y)
 for t in tracks[net]:
  if t.GetLayer()!=layer:continue
  a,z=key(t.GetStart()),key(t.GetEnd());length=p.ToMM(t.GetLength())
  graph[a].append((z,length));graph[z].append((a,length))
 # Pad copper joins endpoints even when a redundant under-pad segment was
 # removed. Charge the full geometric distance through the pad; do not treat
 # the connection as a zero-length shortcut or rely on a ground-plane path.
 ends=list(graph)
 for fp in fps.values():
  for pad in fp.Pads():
   if pad.GetNetname()!=net or not pad.IsOnLayer(layer):continue
   center=key(pad.GetPosition())
   for end in ends:
    if end!=center and pad.HitTest(p.VECTOR2I(*end)):
     delta=p.ToMM(int(round(math.dist(center,end))))
     graph[center].append((end,delta));graph[end].append((center,delta))
 start,goal=key(first.GetPosition()),key(last.GetPosition());queue=[(0,start)];best={start:0}
 while queue:
  length,node=heapq.heappop(queue)
  if length!=best[node]:continue
  if node==goal:return length
  for nxt,delta in graph[node]:
   if length+delta<best.get(nxt,float('inf')):
    best[nxt]=length+delta;heapq.heappush(queue,(length+delta,nxt))
 raise AssertionError(('Missing direct bypass path',net,b.GetLayerName(layer)))
local={}
for ref,vin_limit,gnd_limit in [('C2',5.5,10),('C3',2.2,6)]:
 vin=local_path('VIN_PROT',pads(ref)['1'],pads('U1')['3'],p.B_Cu)
 gnd=local_path('GND',pads(ref)['2'],pads('U1')['1'],p.B_Cu)
 assert vin<vin_limit and gnd<gnd_limit,(ref,vin,gnd)
 local[ref]=dict(vin_bottom_path_mm=vin,ground_bottom_path_mm=gnd)
report['buck_local_bypass']=local
report['status_optical_access']=dict(center_top_left_mm=CONTRACT['status_led_center_mm'],reserved_diameter_mm=6,suggested_duct_bore_mm=4,LED_nominal_height_mm=.65,duct_lower_face_above_PCB_mm=[.85,1.15],board_edge_clearance_mm=WIDTH-CONTRACT['status_led_center_mm'][0]-3,mount_H2_center_distance_mm=math.dist(CONTRACT['status_led_center_mm'],CONTRACT['mounting_holes_top_left_mm'][1]),scope='6 mm circular component courtyard reserved for a non-contact printed duct; native DRC checks adjacent courtyards. Nominal dimensions; enclosure tolerances, viewing angle and brightness require physical qualification.')
report['status_routes']={net:dict(track_length_mm=sum(p.ToMM(t.GetLength()) for t in tracks[net]),vias=vias[net],layers=sorted({b.GetLayerName(t.GetLayer()) for t in tracks[net]})) for net in ('STATUS_5V_DATA','STATUS_DIN')}
led_bypass={}
for ref,ic,pin,limit in [('C74','U10','5',3),('C75','D10','2',4)]:
 length=local_path('V5_INTERNAL',pads(ref)['1'],pads(ic)[pin])
 assert length<limit,(ref,length)
 led_bypass[ref]=dict(supply_top_path_mm=length)
report['rgb_local_bypass']=led_bypass
route_layers={}
for layer in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu):
 tt=[t for group in tracks.values() for t in group if t.GetLayer()==layer]
 exceptions=[]
 for t in tt:
  dx=abs(t.GetEnd().x-t.GetStart().x);dy=abs(t.GetEnd().y-t.GetStart().y)
  # Match the strict routing gate: only native coordinate-rounding tolerance.
  assert not isinstance(t,p.PCB_ARC),'Curved copper centerline'
  if min(dx,dy,abs(dx-dy))>p.FromMM(.00002):
   exceptions.append(dict(net=t.GetNetname(),start_mm=list(p.ToMM(t.GetStart())),end_mm=list(p.ToMM(t.GetEnd())),length_mm=p.ToMM(t.GetLength())))
 assert not exceptions,('Non-45-degree routes',exceptions)
 route_layers[b.GetLayerName(layer)]=dict(segments=len(tt),length_mm=sum(p.ToMM(t.GetLength()) for t in tt),non_45_degree_segments=exceptions)
report['routing_inventory']=dict(layers=route_layers,vias=sum(vias.values()),scope='Straight horizontal/vertical/45-degree centerlines enforced. The separate routing_rules.json gate also rejects redundant geometry, tiny free jogs and sharp free bends. Rounded copper end caps are normal. Native DRC and independent Gerber checks establish connectivity/clearance, not EMC qualification.')
args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
