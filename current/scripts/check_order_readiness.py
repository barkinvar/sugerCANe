"""Rev H pre-fabrication checks, including native routed-copper voltage drop.

This is a reproducible engineering screen. Physical qualification remains separate.
"""
from pathlib import Path
import argparse, hashlib, json, math, subprocess, sys
import numpy as np
import sexpdata
from shapely import STRtree
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points
import check_boost_spice as spice
ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/electrical/order_readiness.json'
GEOMETRY_EXPORT = r'''import pcbnew as p,json,sys
b=p.LoadBoard(sys.argv[1])
report={}
for net in ('V5_INTERNAL','BOOST_12V','SENSOR_5V','SENSOR_12V'):
 tracks=[];vias=[];pads=[]
 for t in b.GetTracks():
  if t.GetNetname()!=net:continue
  if isinstance(t,p.PCB_VIA):vias.append(dict(at=list(p.ToMM(t.GetPosition())),drill=p.ToMM(t.GetDrillValue()),width=p.ToMM(t.GetWidth(p.F_Cu)),layers=list(t.GetLayerSet().Seq())))
  else:tracks.append(dict(start=list(p.ToMM(t.GetStart())),end=list(p.ToMM(t.GetEnd())),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
 for f in b.GetFootprints():
  for d in f.Pads():
   if d.GetNetname()==net:
    contacts=[]
    for t in tracks:
     a,z=[p.VECTOR2I(p.FromMM(t[k][0]),p.FromMM(t[k][1])) for k in ('start','end')]
     if d.IsOnLayer(t['layer']) and d.GetEffectiveShape(t['layer']).Collide(p.SHAPE_SEGMENT(a,z,p.FromMM(t['width']))):
      center=list(p.ToMM(d.GetPosition()));v=[t['end'][k]-t['start'][k] for k in (0,1)]
      fraction=max(0,min(1,sum((center[k]-t['start'][k])*v[k] for k in (0,1))/sum(q*q for q in v)))
      contacts.append([*[t['start'][k]+fraction*v[k] for k in (0,1)],t['layer']])
    pads.append(dict(ref=f.GetReference(),number=d.GetNumber(),contacts=contacts))
 report[net]=dict(tracks=tracks,vias=vias,pads=pads,layer_names={i:b.GetLayerName(i) for i in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu)})
print(json.dumps(report))
'''


def copper_junctions(geo):
    """Contact-aware centerline network, independent of segment subdivision.

    Pads and via annuli are ideal conductors. Overlapping tracks receive a
    finite transverse link at their nearest centerline points. This remains a
    nominal DC planning model, not a current-crowding/field solution.
    """
    tracks=geo['tracks'];lines=[LineString([t['start'],t['end']]) for t in tracks]
    bodies=[line.buffer(t['width']/2,quad_segs=24) for line,t in zip(lines,tracks)]
    tree=STRtree(bodies);nodes=[];links=[];annuli=[]
    for i,t in enumerate(tracks):
     layer=t['layer']
     for j in tree.query(bodies[i]):
      j=int(j)
      if j<=i or tracks[j]['layer']!=layer or not bodies[i].intersects(bodies[j]):continue
      a,b=nearest_points(lines[i],lines[j]);na=(*a.coords[0],layer);nb=(*b.coords[0],layer)
      nodes.extend([na,nb]);links.append((na,nb,a.distance(b),min(t['width'],tracks[j]['width'])))
    for via in geo['vias']:
     center=Point(via['at']);annulus=center.buffer(via['width']/2,quad_segs=24)
     for i in tree.query(annulus):
      i=int(i);layer=tracks[i]['layer']
      if layer not in via['layers'] or not annulus.intersects(bodies[i]):continue
      q=lines[i].interpolate(lines[i].project(center));a=(*q.coords[0],layer);b=(*via['at'],layer)
      nodes.extend([a,b]);annuli.append((a,b))
    return nodes,links,annuli


def copper_depths(board_path):
    """Copper-center depths from the saved stackup, in millimeters."""
    board=sexpdata.loads(Path(board_path).read_text())
    setup=next(v for v in board if isinstance(v,list) and str(v[0])=='setup')
    stack=next(v for v in setup if isinstance(v,list) and str(v[0])=='stackup')
    depth=0.;result={}
    for layer in stack[1:]:
     if str(layer[0])!='layer':continue
     fields={str(v[0]):v[1] for v in layer[2:] if isinstance(v,list)}
     if fields.get('type') not in ('copper','core','prepreg'):continue
     thickness=float(fields['thickness'])
     if fields['type']=='copper':result[str(layer[1])]=depth+thickness/2
     depth+=thickness
    assert len(result)==4 and 1.5<depth<1.7,('Unexpected stackup',result,depth)
    return result


def dc_solver(geo,depths):
    """Return a nodal DC solver for one net, with explicit copper contacts."""
    contact_nodes,contact_links,annuli=copper_junctions(geo)
    parent={};edges=[]
    def root(n):
     parent.setdefault(n,n)
     if parent[n]!=n:parent[n]=root(parent[n])
     return parent[n]
    def join(a,b):parent[root(a)]=root(b)
    def node(x,y,l):return (round(x,6),round(y,6),l)
    for t in geo['tracks']:
     a=node(*t['start'],t['layer']);b=node(*t['end'],t['layer']);root(a);root(b)
    for n in contact_nodes:root(node(*n))
    for a,b in annuli:join(node(*a),node(*b))
    for a,b,length,width in contact_links:
     if length<.000001:join(node(*a),node(*b))
    for pad in geo['pads']:
     ref=(pad['ref'],pad['number']);root(ref)
     for point in pad['contacts']:join(ref,node(*point))
    # Split tracks at existing endpoints so T junctions are real network nodes.
    nodes=[n for n in parent if len(n)==3]
    rho=1.724e-5*(1+.00393*65) # ohm mm at 85C
    for a,b,length,width in contact_links:
     if length>=.000001:edges.append((node(*a),node(*b),rho*length/(width*.035)))
    for t in geo['tracks']:
     a=np.array(t['start']);b=np.array(t['end']);length=np.linalg.norm(b-a);points=[]
     for n in nodes:
      if n[2]!=t['layer']:continue
      q=np.array(n[:2]);f=np.dot(q-a,b-a)/(length*length)
      if -.000001<=f<=1.000001 and np.linalg.norm(q-(a+f*(b-a)))<.000001:points.append((f,n))
     points.sort()
     for (f1,n1),(f2,n2) in zip(points,points[1:]):
      if f2-f1>1e-10:edges.append((n1,n2,rho*length*(f2-f1)/(t['width']*.035)))
    for via in geo['vias']:
     ends=[n for n in nodes if n[:2]==tuple(round(q,6) for q in via['at'])]
     ends.sort(key=lambda n:depths[geo['layer_names'][str(n[2])]])
     for a,b in zip(ends,ends[1:]):
      span=depths[geo['layer_names'][str(b[2])]]-depths[geo['layer_names'][str(a[2])]]
      edges.append((a,b,rho*span/(math.pi*via['drill']*.020)))
    nodes=sorted({root(n) for n in parent},key=str);index={n:i for i,n in enumerate(nodes)}
    G=np.zeros((len(nodes),len(nodes)))
    for a,b,R in edges:
     a=index[root(a)];b=index[root(b)]
     if a==b:continue
     G[a,a]+=1/R;G[b,b]+=1/R;G[a,b]-=1/R;G[b,a]-=1/R
    def solve(source,loads,reference=None):
     current=np.zeros(len(nodes));current[index[root(source)]]=sum(loads.values())
     for dest,amp in loads.items():current[index[root(dest)]]-=amp
     expected=current.copy()
     k=index[root(reference or source)];G2=G.copy();G2[k,:]=0;G2[k,k]=1;current[k]=0
     v=np.linalg.solve(G2,current)
     assert np.max(np.abs(G@v-expected))<1e-8, 'DC network violates current conservation'
     return {str(pin):float(v[index[root(pin)]]) for pin in [source,*loads]}
    return solve


def power_distribution_screen():
    """DC track/via network, 85 C, nominal 35 um copper, ideal conducting pads.

    Ignore power/ground plane resistance, connector/header/contact resistance and
    IC on-resistance here. The model checks the PCB-drop planning allowance only.
    """
    geometry = subprocess.check_output(['kicad-python', '-c', GEOMETRY_EXPORT,
        str(ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb')], text=True)
    report = json.loads(geometry)
    depths=copper_depths(ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb')
    results = {}
    for net,geo in report.items():
     solve=dc_solver(geo,depths)
     if net=='V5_INTERNAL':result=solve(('L1','2'),{('L2','1'):1.3,('U4','1'):.51,('U2','1'):.13,('U10','5'):.001,('D10','2'):.019},('R1','1'))
     elif net=='BOOST_12V':result=solve(('D4','1'),{('U9','4'):.41})
     else:
      source=('U4','6') if net=='SENSOR_5V' else ('U9','5');pin='1' if net=='SENSOR_5V' else '3'
      result={str(ch):solve(source,{(f'JP{ch}01',pin):.3}) for ch in range(1,4)}
     results[net]=result

    before = results['V5_INTERNAL'][str(('L1', '2'))]-results['V5_INTERNAL'][str(('L2', '1'))]
    after = -results['BOOST_12V'][str(('U9', '4'))]
    drop = before
    allowance = .12
    assert 0 < drop < allowance, (drop, allowance)
    sensor_drops = {net: {ch: -value[str((f'JP{ch}01', pin))]
                          for ch,value in results[net].items()}
                    for net,pin in [('SENSOR_5V','1'),('SENSOR_12V','3')]}
    rail_allowance = json.loads((ROOT/'reports/electrical/electrical_checks.json').read_text())['rail_monitor']['ADC_error_budget']['post_switch_copper_allowance_V']
    assert all(0 < v < rail_allowance for branch in sensor_drops.values() for v in branch.values()), sensor_drops
    return dict(method='Native routed-track resistor network with geometric pad/via/track contacts; nodal DC solve',
                trace_temperature_C=85, copper_um=35, via_plating_um=20,
                copper_center_depths_mm=depths,
                boost_input_A=1.3, other_5V_sensor_A=.51, logic_A=.13, RGB_buffer_A=.02,
                buck_to_boost_drop_V=before, boost_to_efuse_drop_V=after,
                total_boost_path_drop_V=drop, revised_PCB_allowance_V=allowance,
                sensor_branch_drop_V_at_300mA=sensor_drops, sensor_branch_allowance_V=rail_allowance,
                results=results, geometry_sha256=hashlib.sha256(geometry.encode()).hexdigest(),
                scope='Nominal etched dimensions, ideal pads/via annuli and finite transverse links between overlapping track centerlines. No current-crowding or temperature solution, ground return, connector contacts, cable or component resistance. Separate switch RON remains in electrical_checks.json.')


def pin_review(parts):
    # Independent manufacturer pin-function expectations, not copied symbol names.
    expected = {
        'U1': {'1':'GND','2':'BUCK_SW','3':'VIN_PROT','4':'BUCK_FB','5':'VIN_PROT','6':'BUCK_CB'},
        'U2': {'1':'V5_INTERNAL','2':'GND','3':'V5_INTERNAL','4':None,'5':'+3V3'},
        'U8': {'1':'BOOST_COMP','2':'BOOST_FB','3':'V5_INTERNAL','4':'GND',
               '5':'BOOST_SW','6':'V5_INTERNAL','7':'V5_INTERNAL','8':'BOOST_SS'},
        'Q1': {'1':'VIN_PROT','2':'VIN_PROT','3':'VIN_PROT','4':'REV_GATE',
               '5':'VIN_FUSED','6':'VIN_FUSED','7':'VIN_FUSED','8':'VIN_FUSED'},
        'D4': {'1':'BOOST_12V','2':'BOOST_SW'},
        'D5': {'1':'SENSOR_12V','2':'GND'},
        'D6': {'1':'BOOST_12V','2':'GND'},
        'U5': {'1': '+3V3', '2': 'HSE_IN', '3': 'HSE_OUT', '4': 'NRST',
               '5': '+3V3', '16': 'GND', '17': '+3V3', '21': 'CAN_RX',
               '22': 'CAN_TX', '23': 'SWDIO', '24': 'SWCLK', '31': 'BOOT0', '32': 'GND'},
        'U6': {'1': 'CAN_TX', '2': 'GND', '3': '+3V3', '4': 'CAN_RX',
               '5': '+3V3', '6': 'CANL', '7': 'CANH', '8': 'CAN_STB'},
        'U7': {'3': '+3V3', '12': 'GND', '2': 'INPUT1', '5': 'SENSE1',
               '4': 'REF_LOGIC', '1': 'INPUT2', '7': 'SENSE2', '6': 'REF_LOGIC',
               '14': 'INPUT3', '9': 'SENSE3', '8': 'REF_LOGIC', '13': None,
               '11': 'GND', '10': '+3V3'},
    }
    expected.update({
        'U4': {'1':'V5_INTERNAL','2':'GND','3':'POWER_5V_EN','4':'FAULT_5V_N','5':'V5_ILIM','6':'SENSOR_5V'},
        'U9': {'1':'GND','2':'EFUSE_SS','3':'EFUSE_EN','4':'BOOST_12V','5':'SENSOR_12V','6':'FAULT_12V_N','7':'EFUSE_ILM','8':None,'9':'GND'},
        'D10': {'1':'STATUS_DIN','2':'V5_INTERNAL','3':None,'4':'GND'},
        'U10': {'1':'GND','2':'STATUS_DATA','3':'GND','4':'STATUS_5V_DATA','5':'V5_INTERNAL'},
        'Q2': {'1':'EFUSE_INHIBIT','2':'GND','3':'EFUSE_EN'},
        'Q3': {'1':'POWER_12V_EN','2':'GND','3':'EFUSE_INHIBIT'},
    })
    expected['U5'].update({'9':'FAULT_12V_N','10':'FAULT_5V_N','14':'ADC_5V','15':'ADC_12V',
                           '25':'POWER_5V_EN','26':'STATUS_DATA','27':'BIAS_DOWN3','28':'BIAS_DOWN1','29':'BIAS_DOWN2','30':'POWER_12V_EN'})
    checks = {ref: all(parts[ref]['pins'][pin] == net for pin, net in pins.items())
              for ref, pins in expected.items()}
    for ref,mpn in [('U4','TPS2553DBVR-1'),('U8','TPS61085DGKR'),
                    ('U9','TPS259620DDAR'),('U7','LM339LVDR')]:
        checks[ref+'_model_matches_fitted_part'] = parts[ref]['mpn']==mpn
    checks['power_values_match_analytical_budgets'] = all(parts[ref]['value']==value for ref,value in {
        'R10':'59k','R62':'2.61k','R68':'100k','R69':'12.1k','R70':'100k',
        'C70':'47nF','R60':'100k','R61':'11.5k'}.items())
    checks['three_input_channels_share_DC_corner_basis'] = all(
        parts[f'R{ch}{suffix}'].get(field)==parts[f'R1{suffix}'].get(field)
        for ch in (2,3) for suffix in ('01','03','04','05','09','10')
        for field in ('value','tolerance','temperature_coefficient_ppm_C'))
    checks['SWD_reset_and_BOOT0_exposed'] = all(net in parts['J8']['pins'].values()
                                              for net in ('SWDIO', 'SWCLK', 'NRST', 'BOOT0', 'GND', '+3V3'))
    checks['BOOT0_pulldown'] = parts['R22']['pins'] == {'1': 'BOOT0', '2': 'GND'} and parts['R22']['value'] == '10k'
    checks['CAN_defaults_to_standby'] = parts['R40']['pins'] == {'1': '+3V3', '2': 'CAN_STB'}
    checks['12V_disable_derived_from_raw_supply'] = parts['R70']['pins']=={'1':'BOOST_12V','2':'EFUSE_INHIBIT'}
    checks['12V_enable_defaults_low'] = parts['R75']['pins']=={'1':'POWER_12V_EN','2':'GND'} and parts['R75']['value']=='10k'
    checks['5V_enable_defaults_low'] = parts['R71']['pins']=={'1':'POWER_5V_EN','2':'GND'} and parts['R71']['value']=='10k'
    checks['raw_reservoir_before_limiter'] = all(parts[r]['pins']=={'1':'BOOST_12V','2':'GND'} for r in ['C62','C63','C64'])
    assert all(checks.values()), checks
    return dict(checks=checks, firmware_can_reset_power_switches=True,
                scope='Independent manufacturer pin-function expectations and default-off circuit intent, alongside native parity checks.')

def inputs():
    paths = ['hardware/design/circuit.json','hardware/FRC_Sensor_CAN.kicad_pcb',
             'reports/electrical/electrical_checks.json','reports/electrical/boost_spice.json',
             'reports/design_parity.json','reports/board_constraints.json',
             'scripts/check_boost_spice.py','scripts/check_electrical.py','scripts/check_order_readiness.py']
    return {path:spice.sha(ROOT/path) for path in paths}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify-report',action='store_true')
    ap.add_argument('--allow-incomplete',action='store_true',help='Record fresh CAD/DC evidence with a HOLD decision while full power evidence is incomplete; never approves fabrication')
    args=ap.parse_args()
    parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
    pins=pin_review(parts);distribution=power_distribution_screen()
    transient=json.loads((ROOT/'reports/electrical/boost_spice.json').read_text())
    complete = transient['result']=='PASS transient screening only'
    if complete or not args.allow_incomplete:
        subprocess.run([sys.executable,str(ROOT/'scripts/check_boost_spice.py'),'--verify-report','--require-pass'],check=True)
        assert complete and all(r['pass'] for r in transient['cases'])
    result=dict(order_decision=('PASS pre-fabrication engineering screens; unbuilt prototype' if complete else
                               'HOLD: full power-transient evidence incomplete or failing; CAD/DC screens pass'),
                physical_tests_performed=False,revision='H',
                power_distribution_valid_for_current_layout=True, full_power_transient_pass=complete,
                input_hashes=inputs(),pin_review=pins,power_distribution=distribution,
                protection_boundary={
                 'covered_fault_scenarios':'Sensor-supply shorts to ground, overload and explicit recovery under the documented model assumptions.',
                 'cross_connection_5V_to_12V_supported':False,
                 'U4_OUT_absolute_maximum_V':7,
                 'reason':'A 12 V cross-connection exceeds the TPS2553-1 OUT absolute maximum. Current limiting and software voltage monitoring do not guarantee survival of U4 or a 5 V sensor.',
                 'source':'https://www.ti.com/lit/ds/symlink/tps2553.pdf',
                 'other_exclusions':'External power applied to sensor outputs, arbitrary reverse powering and externally driven fault transients.'},
                resolved_rev_f_findings=['Output eFuse isolates reservoir from a sensor short',
                 'Boost input no longer passes through the former 1.2 A switch',
                 'Controlled output slew and staggered firmware startup',
                 'Explicit CAN reset and default-off rail enables',
                 'ADC monitoring replaces coarse comparator rail indication',
                 'Buck input capacitors relocated with verified local VIN and ground paths'],
                limitations='Ideal pad/nominal copper DC model; no ground-return/contact/cable resistance or thermal solution. Vendor transient models use an idealized upstream 5 V supply and typical silicon. No board has been assembled or measured. Follow docs/VALIDATION.md for physical acceptance.')
    if args.verify_report:
        assert json.loads(REPORT.read_text())==result
        print('PASS retained pre-fabrication review integrity');return
    REPORT.write_text(json.dumps(result,indent=2)+'\n');print(result['order_decision'])
if __name__=='__main__':main()
