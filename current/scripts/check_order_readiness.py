"""Pre-order review and hypothetical power experiments; never a fabrication sign-off.

Run the review: python scripts/check_order_readiness.py
Optional long transient exploration: python scripts/check_order_readiness.py --simulate --jobs 2 [--reuse]
Verify retained evidence: python scripts/check_order_readiness.py --verify-report
Raw simulation files stay in ignored tmp/order-review. PCB/BOM are not changed.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess

import numpy as np
import matplotlib.pyplot as plt
import check_boost_spice as spice

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'tmp/order-review'
REPORT = ROOT / 'reports/electrical/order_readiness.json'
CASES = [
    dict(name='candidate_1u_full_cap_load', vin=4.913149, cin=22, cout=66,
         extra_cap=100, css='1u', end=45),
    dict(name='candidate_1u_small_input_hotshort', cin=1, css='1u', end=38,
         short='0 0 25m 0 25.001m 1 36m 1 36.001m 0'),
]


GEOMETRY_EXPORT = r'''import pcbnew as p,json,sys
b=p.LoadBoard(sys.argv[1])
report={}
for net in ('V5_INTERNAL','V5_BOOST','SENSOR_5V','SENSOR_12V'):
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
     if net=='V5_INTERNAL':result=solve(('L1','2'),{('U9','1'):1.1,('U4','1'):.31,('U2','1'):.1},('R1','1'))
     elif net=='V5_BOOST':result=solve(('U9','6'),{('L2','1'):1.1})
     else:
      source=('U4','6') if net=='SENSOR_5V' else ('D4','1');pin='1' if net=='SENSOR_5V' else '3'
      result={str(ch):solve(source,{(f'JP{ch}01',pin):.3}) for ch in range(1,4)}
     results[net]=result

    before = -results['V5_INTERNAL'][str(('U9', '1'))]
    after = -results['V5_BOOST'][str(('L2', '1'))]
    drop = before + after
    allowance = .12
    assert 0 < drop < allowance, (drop, allowance)
    return dict(method='Native routed-track resistor network with pad contacts and through vias; nodal DC solve',
                trace_temperature_C=85, copper_um=35, via_plating_um=20,
                boost_input_A=1.1, other_5V_sensor_A=.31, logic_A=.1,
                before_switch_drop_V=before, after_switch_drop_V=after,
                total_boost_path_drop_V=drop, revised_PCB_allowance_V=allowance,
                results=results, geometry_sha256=hashlib.sha256(geometry.encode()).hexdigest(),
                scope='Nominal etched dimensions and ideal pads. No temperature solution, ground return, contacts, cable or component resistance. Separate switch RON remains in electrical_checks.json.')


def pin_review(parts):
    # Independent manufacturer pin-function expectations, not copied symbol names.
    expected = {
        'U5': {'1': '+3V3', '2': 'HSE_IN', '3': 'HSE_OUT', '4': 'NRST',
               '5': '+3V3', '16': 'GND', '17': '+3V3', '21': 'CAN_RX',
               '22': 'CAN_TX', '23': 'SWDIO', '24': 'SWCLK', '31': 'BOOT0', '32': 'GND'},
        'U6': {'1': 'CAN_TX', '2': 'GND', '3': '+3V3', '4': 'CAN_RX',
               '5': '+3V3', '6': 'CANL', '7': 'CANH', '8': 'CAN_STB'},
        'U7': {'3': '+3V3', '12': 'GND', '2': 'INPUT1', '5': 'SENSE1',
               '4': 'REF_LOGIC', '1': 'INPUT2', '7': 'SENSE2', '6': 'REF_LOGIC',
               '14': 'INPUT3', '9': 'SENSE3', '8': 'REF_LOGIC', '13': 'PG_12V',
               '11': 'SENSE_12V', '10': 'REF_LOGIC'},
    }
    checks = {ref: all(parts[ref]['pins'][pin] == net for pin, net in pins.items())
              for ref, pins in expected.items()}
    checks['SWD_reset_and_BOOT0_exposed'] = all(net in parts['J8']['pins'].values()
                                              for net in ('SWDIO', 'SWCLK', 'NRST', 'BOOT0', 'GND', '+3V3'))
    checks['BOOT0_pulldown'] = parts['R22']['pins'] == {'1': 'BOOT0', '2': 'GND'} and parts['R22']['value'] == '10k'
    checks['CAN_defaults_to_standby'] = parts['R40']['pins'] == {'1': '+3V3', '2': 'CAN_STB'}
    assert all(checks.values()), checks
    return dict(checks=checks,
                power_switch_enable_nets={ref: parts[ref]['pins']['3'] for ref in ('U4', 'U9')},
                firmware_can_reset_power_switches=all(parts[ref]['pins']['3'] in
                    {net for pin, net in parts['U5']['pins'].items() if pin not in ('1', '5', '16', '17', '32') and net}
                    for ref in ('U4', 'U9')),
                scope='Manufacturer pin-function review plus retained native parity checks; not physical operation.')


def metrics(case, data):
    t = data['time']; output = data['v(sensor_12v)']
    assert t[-1] >= case['end']/1000 - 1e-10
    def bounds(key, a, b):
        values = data[key][(t >= a/1000) & (t <= b/1000)]
        assert len(values)
        return [float(values.min()), float(values.max())]
    def within(v, lo, hi):
        return lo <= v[0] <= v[1] <= hi
    above = data['v(v5_boost)'] > 2.29
    crossed = np.flatnonzero(output >= 11.4)
    result = dict(case=case,
                  first_11_4V_ms=float(t[crossed[0]]*1000) if len(crossed) else None,
                  output_peak_V=float(output.max()), peak_inductor_A=float(data['i(l2)'].max()),
                  boost_input_uvlo_drops=int(np.count_nonzero(above[:-1] & ~above[1:])),
                  final_output_range_V=bounds('v(sensor_12v)', case['end']-1, case['end']))
    if case.get('short'):
        result['preshort_output_range_V'] = bounds('v(sensor_12v)', 23, 24)
        result['checks'] = dict(regulated_before_short=within(result['preshort_output_range_V'], 11.4, 12.6),
                               disconnected_after_short=within(bounds('v(v5_boost)', 37, 38), -.1, .1),
                               linear_inductor_model_within_8A_domain=result['peak_inductor_A'] <= 8)
        result['disposition'] = ('Not an accepted hardware fix: 1 uF bulk input capacitance is below TI\'s '
                                 '10 uF typical application recommendation; real input ripple and buck interaction '
                                 'are absent. If preshort regulation fails, this does not establish a regulated hot-short result.')
    else:
        result['checks'] = dict(final_regulation=within(result['final_output_range_V'], 11.4, 12.6),
                               no_false_latch=within(bounds('v(pg_12v)', .2, case['end']), 3, 3.4),
                               no_UVLO_retries=result['boost_input_uvlo_drops'] == 0)
        result['disposition'] = ('Hypothetical C66=1 uF, fixed nameplate capacitors. A passing result would only '
                                 'justify further evaluation; it does not resolve short energy, reset recovery, '
                                 'actual upstream buck behavior or component corners.')
    result['screen_pass'] = all(result['checks'].values())
    return result


def inputs():
    paths = ['hardware/design/circuit.json', 'hardware/FRC_Sensor_CAN.kicad_pcb',
             'reports/electrical/electrical_checks.json', 'reports/electrical/boost_spice.json',
             'reports/design_parity.json', 'reports/board_constraints.json',
             'scripts/check_boost_spice.py', 'scripts/check_electrical.py', 'scripts/check_order_readiness.py']
    return {path: spice.sha(ROOT/path) for path in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulate', action='store_true', help='Run the optional, potentially hour-long hypothetical component cases')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--reuse', action='store_true')
    parser.add_argument('--verify-report', action='store_true')
    args = parser.parse_args()
    parts = json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
    electrical = json.loads((ROOT/'reports/electrical/electrical_checks.json').read_text())
    pins = pin_review(parts)
    distribution = power_distribution_screen()
    assert electrical['power']['boost_PCB_drop_allowance_V'] == distribution['revised_PCB_allowance_V']
    if args.verify_report:
        report = json.loads(REPORT.read_text())
        assert report['input_hashes'] == inputs()
        assert report['pin_review'] == pins
        assert report['power_distribution'] == distribution
        assert report['order_decision'] == 'HOLD: not qualified for a single final hardware order'
        assert report['physical_tests_performed'] is False
        assert report['planned_experiments'] == CASES
        assert report['accepted_hardware_substitutions'] == []
        assert report['completed_additional_transient_evidence'] is False
        print('PASS retained order-review evidence integrity. Order decision remains HOLD.')
        return
    if not args.simulate:
        report = dict(order_decision='HOLD: not qualified for a single final hardware order',
                      physical_tests_performed=False, hardware_changed=False,
                      input_hashes=inputs(), pin_review=pins, power_distribution=distribution,
                      accepted_hardware_substitutions=[], completed_additional_transient_evidence=False,
                      planned_experiments=CASES,
                      exploration_status='The two long component experiments were intentionally stopped before their requested end times. Neither is counted as a pass or fail, and neither supports a hardware substitution.',
                      reason='Startup, fault-current behavior, controlled reset and voltage monitoring require a combined hardware review. Capacitor-only experiments cannot close this order decision.',
                      scope='Native pin and DC routed-copper review plus retained original transient evidence. No new completed transient evidence, physical qualification, thermal/EMC or actual sensor tests.')
        REPORT.write_text(json.dumps(report, indent=2)+'\n')
        print(report['order_decision'])
        return
    WORK.mkdir(parents=True, exist_ok=True)
    spice.WORK = WORK
    spice.prepare_models()
    simulator = shutil.which('ngspice')
    if not simulator:
        raise SystemExit('ngspice is required')
    version = subprocess.check_output([simulator, '--version'], text=True).strip()
    models = {name: spice.sha(WORK/name) for name in ('tps61085.lib', 'tps2553-1.lib', 'B240A.lib')}
    def run(case):
        name = case['name']; deck = spice.circuit(case, parts, electrical)
        digest = hashlib.sha256((deck + version + json.dumps(models, sort_keys=True)).encode()).hexdigest()
        marker = WORK/(name+'.complete')
        if not (args.reuse and marker.exists() and marker.read_text() == digest):
            marker.unlink(missing_ok=True)
            (WORK/(name+'.cir')).write_text(deck)
            print('Running '+name, flush=True)
            subprocess.run([simulator, '-b', '-o', name+'.log', '-r', name+'.raw', name+'.cir'],
                           cwd=WORK, stdout=subprocess.DEVNULL, check=True, timeout=7200)
        assert (WORK/(name+'.cir')).read_text() == deck
        log = (WORK/(name+'.log')).read_text()
        assert not re.search(r'(?i)error|timestep too small|simulation interrupted|warning', log), log[-1000:]
        data = spice.read_raw(WORK/(name+'.raw'))
        result = metrics(case, data)
        marker.write_text(digest)
        result.update(netlist=deck, raw_sha256=spice.sha(WORK/(name+'.raw')), deck_and_models_sha256=digest)
        grid = np.linspace(0, case['end']/1000, 7000)
        compact = {key: np.interp(grid, data['time'], v) for key, v in data.items()}
        print(name+': '+json.dumps(result['checks']), flush=True)
        return result, compact
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
        runs = list(executor.map(run, CASES))
    report = dict(order_decision='HOLD: not qualified for a single final hardware order',
                  physical_tests_performed=False, hardware_changed=False,
                  input_hashes=inputs(), pin_review=pins, power_distribution=distribution, simulator=version, adapted_model_sha256=models,
                  scope='Hypothetical component changes. Same 25 C manufacturer-model port and ideal upstream source as boost_spice.json; no buck loop, saturation, PCB/cable parasitics, temperature or production corners.',
                  experiments=[row for row, data in runs])
    experiment_report = WORK/'completed_experiments.json'
    experiment_report.write_text(json.dumps(report, indent=2)+'\n')
    fig, axes = plt.subplots(2, 1, figsize=(11, 7))
    for ax, (row, data) in zip(axes, runs):
        for key, label in [('v(sensor_12v)', '12 V output'), ('v(v5_boost)', 'Boost input'), ('v(pg_12v)', 'U9 /FAULT')]:
            ax.plot(data['time']*1000, data[key], label=label, lw=1)
        ax.set_title(row['case']['name'].replace('_', ' ')+(' — screen PASS' if row['screen_pass'] else ' — screen FAIL'), fontsize=10)
        ax.set_xlabel('Time (ms)'); ax.set_ylabel('Voltage (V)'); ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle('Pre-order diagnostic experiments — PCB/BOM unchanged\nNo physical qualification; neither experiment is an accepted hardware fix', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .92)); fig.savefig(experiment_report.with_suffix('.png'), dpi=150); plt.close(fig)
    print(report['order_decision'])


if __name__ == '__main__':
    main()
