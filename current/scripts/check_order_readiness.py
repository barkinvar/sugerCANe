"""Rev H pre-fabrication checks, including native routed-copper voltage drop.

This is a reproducible engineering screen. Physical qualification remains separate.
"""
from pathlib import Path
import argparse, hashlib, json, math, subprocess
import numpy as np
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
  if isinstance(t,p.PCB_VIA):vias.append(dict(at=list(p.ToMM(t.GetPosition())),drill=p.ToMM(t.GetDrillValue())))
  else:tracks.append(dict(start=list(p.ToMM(t.GetStart())),end=list(p.ToMM(t.GetEnd())),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
 for f in b.GetFootprints():
  for d in f.Pads():
   if d.GetNetname()==net:
    contacts=[]
    for t in tracks:
     for key in ('start','end'):
      if d.IsOnLayer(t['layer']) and d.HitTest(p.VECTOR2I(p.FromMM(t[key][0]),p.FromMM(t[key][1]))):contacts.append([*t[key],t['layer']])
    pads.append(dict(ref=f.GetReference(),number=d.GetNumber(),contacts=contacts))
 report[net]=dict(tracks=tracks,vias=vias,pads=pads)
print(json.dumps(report))
'''


def power_distribution_screen():
    """DC track/via network, 85 C, nominal 35 um copper, ideal conducting pads.

    Ignore power/ground plane resistance, connector/header/contact resistance and
    IC on-resistance here. The model checks the PCB-drop planning allowance only.
    """
    geometry = subprocess.check_output(['kicad-python', '-c', GEOMETRY_EXPORT,
        str(ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb')], text=True)
    report = json.loads(geometry)
    results = {}
    for net,geo in report.items():
     parent={};edges=[]
     def root(n):
      parent.setdefault(n,n)
      if parent[n]!=n:parent[n]=root(parent[n])
      return parent[n]
     def join(a,b):parent[root(a)]=root(b)
     def node(x,y,l):return (round(x,6),round(y,6),l)
     for t in geo['tracks']:
      a=node(*t['start'],t['layer']);b=node(*t['end'],t['layer']);root(a);root(b)
     for pad in geo['pads']:
      ref=(pad['ref'],pad['number']);root(ref)
      for point in pad['contacts']:join(ref,node(*point))
     # Split tracks at existing endpoints so T junctions are real network nodes.
     nodes=[n for n in parent if len(n)==3]
     rho=1.724e-5*(1+.00393*65) # ohm mm at 85C
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
      ends.sort(key=lambda n:n[2])
      if len(ends)==2:edges.append((*ends,rho*1.6/(math.pi*via['drill']*.020)))
      elif len(ends)>2:raise RuntimeError(('multilayer via needs physical lengths',via,ends))
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
     if net=='V5_INTERNAL':result=solve(('L1','2'),{('L2','1'):1.3,('U4','1'):.51,('U2','1'):.13,('U10','5'):.001,('D10','2'):.019},('R1','1'))
     elif net=='BOOST_12V':result=solve(('D4','1'),{('U9','4'):.41})
     else:
      source=('U4','6') if net=='SENSOR_5V' else ('U9','5');pin='1' if net=='SENSOR_5V' else '3'
      result={str(ch):solve(source,{(f'JP{ch}01',pin):.3}) for ch in range(1,4)}
     results[net]=result

    before = -results['V5_INTERNAL'][str(('L2', '1'))]
    after = -results['BOOST_12V'][str(('U9', '4'))]
    drop = before
    allowance = .12
    assert 0 < drop < allowance, (drop, allowance)
    return dict(method='Native routed-track resistor network with pad contacts and through vias; nodal DC solve',
                trace_temperature_C=85, copper_um=35, via_plating_um=20,
                boost_input_A=1.3, other_5V_sensor_A=.51, logic_A=.13, RGB_buffer_A=.02,
                buck_to_boost_drop_V=before, boost_to_efuse_drop_V=after,
                total_boost_path_drop_V=drop, revised_PCB_allowance_V=allowance,
                results=results, geometry_sha256=hashlib.sha256(geometry.encode()).hexdigest(),
                scope='Nominal etched dimensions and ideal pads. No temperature solution, ground return, contacts, cable or component resistance. Separate switch RON remains in electrical_checks.json.')


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
    checks['SWD_reset_and_BOOT0_exposed'] = all(net in parts['J8']['pins'].values()
                                              for net in ('SWDIO', 'SWCLK', 'NRST', 'BOOT0', 'GND', '+3V3'))
    checks['BOOT0_pulldown'] = parts['R22']['pins'] == {'1': 'BOOT0', '2': 'GND'} and parts['R22']['value'] == '10k'
    checks['CAN_defaults_to_standby'] = parts['R40']['pins'] == {'1': '+3V3', '2': 'CAN_STB'}
    checks['12V_disable_derived_from_raw_supply'] = parts['R70']['pins']=={'1':'BOOST_12V','2':'EFUSE_INHIBIT'}
    checks['12V_enable_defaults_low'] = parts['R75']['pins']=={'1':'POWER_12V_EN','2':'GND'}
    checks['5V_enable_defaults_low'] = parts['R71']['pins']=={'1':'POWER_5V_EN','2':'GND'}
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
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--verify-report',action='store_true');args=ap.parse_args()
    parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
    pins=pin_review(parts);distribution=power_distribution_screen()
    transient=json.loads((ROOT/'reports/electrical/boost_spice.json').read_text())
    assert transient['result']=='PASS transient screening only'
    assert all(r['pass'] for r in transient['cases'])
    result=dict(order_decision='PASS pre-fabrication engineering screens; unbuilt prototype',
                physical_tests_performed=False,hardware_changed=True,revision='H',
                input_hashes=inputs(),pin_review=pins,power_distribution=distribution,
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
