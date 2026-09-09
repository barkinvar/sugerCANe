"""Transient screening with manufacturer models; not whole-board qualification.

Run from any directory: python scripts/check_boost_spice.py --jobs 2
Raw traces/decks stay in ignored tmp/spice. Only summary JSON/PNG are published.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import re
import shutil
import subprocess

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources/spice'
WORK = ROOT / 'tmp/spice'
REPORT = ROOT / 'reports/electrical'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_models():
    for entry in json.loads((SOURCE / 'manifest.json').read_text()):
        assert sha(SOURCE / entry['file']) == entry['sha256'], entry['file']
    for name, prefix in [('tps61085.lib', 'BST_'), ('tps2553-1.lib', 'SW_'), ('tps259620.lib', 'EF_')]:
        text = (SOURCE / name).read_text()
        # Syntax adaptation only. Do not tune semiconductor behavior to pass.
        text = text.replace('PARAMS: PARAMS:', 'PARAMS:')
        # PSpice ^ means Boolean XOR here; ngspice interprets it as power.
        text = re.sub(r'V\(A\) > \{VTHRESH\}\s*\^\s*\+?\s*V\(B\) > \{VTHRESH\}',
                      '(V(A) > {VTHRESH}) != (V(B) > {VTHRESH})', text)
        names = set(re.findall(r'^\s*\.(?:subckt|model)\s+(\S+)', text, re.M | re.I))
        lookup = {name.lower(): prefix + name for name in names}
        pattern = r'(?<![\w])(' + '|'.join(map(re.escape, sorted(names, key=len, reverse=True))) + r')(?![\w])'
        text = re.sub(pattern, lambda m: lookup[m[0].lower()], text, flags=re.I)
        (WORK / name).write_text(text)
    shutil.copyfile(SOURCE / 'B240A.lib', WORK / 'B240A.lib')
    (WORK / '.spiceinit').write_text('set ngbehavior=psa\n')


def read_raw(path):
    with path.open('rb') as stream:
        header = []
        while True:
            line = stream.readline()
            if not line:
                raise ValueError(f'Incomplete raw file: {path}')
            if line == b'Binary:\n':
                break
            header.append(line.decode().strip())
        nv = int(next(x.split(':')[1] for x in header if x.startswith('No. Variables:')))
        count = int(next(x.split(':')[1] for x in header if x.startswith('No. Points:')))
        start = header.index('Variables:') + 1
        names = [x.split()[1] for x in header[start:start + nv]]
        data = np.fromfile(stream, dtype=np.float64).reshape(-1, nv)
        assert len(data) == count and np.isfinite(data).all(), path
    return dict(zip(names, data.T))


def circuit(case, parts, electrical):
    def net(n):return '0' if n=='GND' else n
    def pins(ref,order):return ' '.join(net(parts[ref]['pins'][str(i)]) for i in order)
    def passive(ref):
        v=parts[ref]['value'].removesuffix('F').removesuffix('H')
        return f'{ref} {pins(ref,[1,2])} {v}'
    if case.get('five_only'):
        lines=[case['name'],'.include tps2553-1.lib',
          'Vsrc SOURCE 0 PWL(0 0 4m 5.067153284671533)', 'Rsource SOURCE V5_INTERNAL .12',
          'Cinternal V5_INTERNAL 0 25.92u', 'Bother V5_INTERNAL 0 I={1.3*limit(v(V5_INTERNAL),0,1)}',
          f'Xu4 {pins("U4",[1,2,3])} 0 {pins("U4",[4,5,6])} SW_TPS2553-1_TRANS',
          passive('R10'), passive('C11'), passive('C12'),
          'Vlogic LOGIC 0 3.3','Rfault LOGIC FAULT_5V_N 40k',
          'Ven POWER_5V_EN 0 PWL(0 0 10m 0 10.001m 3.3 45m 3.3 45.001m 0 55m 0 55.001m 3.3)',
          'Rext SENSOR_5V EC .1', 'Cext EC 0 22u',
          'Bload SENSOR_5V 0 I={.3*limit(v(SENSOR_5V),0,1)}',
          'Vshort SHORT 0 PWL(0 0 25m 0 25.001m 1 35m 1 35.001m 0)',
          'Sshort SENSOR_5V 0 SHORT 0 SHORTMODEL', '.model SHORTMODEL SW(Ron=.05 Roff=1e12 Vt=.5 Vh=.1)',
          '.save v(V5_INTERNAL) v(SENSOR_5V) v(FAULT_5V_N) i(Vsrc)',
          '.options method=gear reltol=.003 abstol=10n vntol=10u itl1=1000 itl4=1000 cshunt=1e-15',
          '.tran 100n 75m 0 500n', '.end']
        return '\n'.join(lines)+'\n'
    assert parts['U9']['mpn']=='TPS259620DDAR' and parts['R62']['value']=='2.61k'
    assert parts['C70']['value']=='47nF' and parts['U8']['mpn']=='TPS61085DGKR'
    assert parts['C65']['value']=='1uF' and parts['C71']['value']=='1uF'
    assert parts['U9']['pins']['4']=='BOOST_12V' and parts['U9']['pins']['5']=='SENSOR_12V'
    vin=case.get('vin',electrical['buck']['nominal_V'])
    lines=[case['name'],'.include tps61085.lib','.include tps2553-1.lib','.include tps259620.lib','.include B240A.lib',
           'Vlogic LOGIC 0 3.3','Rfault LOGIC FAULT_12V_N 40k']
    if case.get('efuse_only'):
        lines += ['Vsrc SOURCE 0 PWL(0 0 1u 12.003)','Rsource SOURCE BOOST_12V .12','Cin BOOST_12V 0 66u']
    else:
        lines += [f'Vsrc SOURCE 0 PWL({case.get("source",f"0 0 100u 0 200u {vin}")})',
                  'Rsource SOURCE V5_INTERNAL .12','Cinternal V5_INTERNAL 0 25.92u',
                  'Bother V5_INTERNAL 0 I={.4*limit(v(V5_INTERNAL),0,1)}',
                  f'Xu8 {pins("U8",[3,2,6,8,4,5,1,7])} BST_TPS61085',
                  'L2 V5_INTERNAL LX 3.3u','Rdcr LX BOOST_SW .032',
                  'D4 BOOST_SW BOOST_12V DI_B240A',
                  'Rcin V5_INTERNAL CI .01',f'Cin CI 0 {case.get("cin",8.64)}u',
                  'Rcout BOOST_12V CO .01',f'Cout CO 0 {case.get("cout",10.8238)}u']
        for r in ['C61','C66','R60','R61','R63','C69']:lines.append(passive(r))
    if case.get('boost_only'):
        lines += ['Vload LOAD 0 PWL(0 .03 4m .03 4.01m .31 6m .31 6.01m .41 8m .41 8.01m 0)',
                  'Bload BOOST_12V 0 I={v(LOAD)*limit(v(BOOST_12V),0,1)}']
    else:
        lines += [f'Xef {pins("U9",[1,2,3,4,5,6,7])} OVC EF_TPS259620_TRANS PARAMS: Cdvdt=47n']
        for r in ['R62','R68','R69','C65','C70','C71']:lines.append(passive(r))
        if case.get('limit_surrogate'):
            # Only this stress case changes the test resistor. The fitted BOM
            # stays 2.61k; 2.92k makes this typical model limit below the
            # calculated minimum of the actual part/resistor combination.
            lines[lines.index(passive('R62'))]='R62 EFUSE_ILM 0 2.92k'
            lines.append('* Current-limit surrogate: 2.92k test resistor; fitted R62 is 2.61k')
        lines += [f'Vdisable DISABLE 0 PWL({case.get("disable","0 0")})',
                  ('Bdisable EFUSE_EN 0 I={v(EFUSE_EN)*limit(v(DISABLE)/3.3,0,1)/2}' if case.get('efuse_only') else 'Sdisable EFUSE_EN 0 DISABLE 0 DISABLE_MODEL'),
                  '.model DISABLE_MODEL VSWITCH(Ron=2 Roff=1e9 Von=2 Voff=.5)',
                  'Rext SENSOR_12V EC .1',f'Cext EC 0 {case.get("extra_cap",100)}u',
                  'Bload SENSOR_12V 0 I={.3*limit(v(SENSOR_12V),0,1)}',
                  # Behavioral clamps screen energy/current, not fast diode dynamics.
                  'D5 0 SENSOR_12V DI_B240A',
                  'BTVS BOOST_12V 0 I={max(0,(v(BOOST_12V)-14.4)/.382)}',
                  'RADC SENSOR_12V 0 220k',
                  f'Vshort SHORT 0 PWL({case.get("short","0 0")})',
                  'Sshort SENSOR_12V 0 SHORT 0 SHORTMODEL',
                  ('.model SHORTMODEL SW(Ron=.05 Roff=1e12 Vt=.5 Vh=.1)' if case.get('efuse_only') else '.model SHORTMODEL VSWITCH(Ron=.05 Roff=1e12 Von=.9 Voff=.1)')]
    lines += ['.save v(V5_INTERNAL) v(BOOST_12V) v(SENSOR_12V) v(EFUSE_EN) v(FAULT_12V_N) i(Vsrc)'+(' i(L2)' if not case.get('efuse_only') else ''),
              '.options method=gear reltol=.003 abstol=10n vntol=10u itl1=1000 itl4=1000 cshunt=1e-15',
              f'.tran 100n {case["end"]}m 0 {case.get("step","50n")}', '.end']
    if case.get('efuse_only'):
        lines=[x.replace('v(V5_INTERNAL) ','') for x in lines]
    if case.get('boost_only'):
        lines=[x.replace('v(SENSOR_12V) ','').replace('v(EFUSE_EN) ','') for x in lines]
    if case.get('xtrtol'):
        assert case['xtrtol'] in (2,7) and not case.get('efuse_only')
        lines=[x.replace('.options method=gear ',f'.options klu method=gear xtrtol={case["xtrtol"]} ') for x in lines]
    return '\n'.join(lines)+'\n'

CASES=[
 dict(name='combined_low_input_capacitive_start',vin=4.913149,cin=22,cout=66,extra_cap=100,end=40,source='0 0 4m 4.913149',xtrtol=2),
 dict(name='boost_load_steps',boost_only=True,end=10),
 dict(name='efuse_hot_short_and_reset',efuse_only=True,step='1u',end=130,
      disable='0 3.3 2m 3.3 2.001m 0 90m 0 90.001m 3.3 95m 3.3 95.001m 0',
      short='0 0 45m 0 45.001m 1 85m 1 85.001m 0'),
 dict(name='efuse_cold_short_and_reset',efuse_only=True,step='1u',end=130,
      disable='0 3.3 2m 3.3 2.001m 0 90m 0 90.001m 3.3 95m 3.3 95.001m 0',
      short='0 1 85m 1 85.001m 0'),
 dict(name='efuse_large_capacitance',efuse_only=True,extra_cap=470,step='1u',end=150),
 dict(name='efuse_thermal_latch',efuse_only=True,step='5u',end=1200,
      disable='0 3.3 2m 3.3 2.001m 0 1100m 0 1100.001m 3.3 1110m 3.3 1110.001m 0',
      short='0 0 45m 0 45.001m 1 1000m 1 1000.001m 0'),
 dict(name='efuse_hot_short_half_step',efuse_only=True,step='500n',end=130,
      disable='0 3.3 2m 3.3 2.001m 0 90m 0 90.001m 3.3 95m 3.3 95.001m 0',
      short='0 0 45m 0 45.001m 1 85m 1 85.001m 0'),
 dict(name='five_volt_start_short_and_reset',five_only=True,end=75),
 dict(name='efuse_min_limit_cap_tolerance',efuse_only=True,limit_surrogate=True,
      extra_cap=120,step='1u',end=200),
]

def combined_repeat_case():
    return dict(CASES[0],xtrtol=7,step='25n',trace_name='combined_low_input_capacitive_start_trtol7_25n')

def evaluate(case,d):
    t=d['time'];checks={};result={'case':case,'checks':checks}
    assert t[-1]>=case['end']/1000-1e-10,'Simulation stopped early'
    def span(key,a,b):
        x=d[key][(t>=a/1000)&(t<=b/1000)];assert len(x);return [float(x.min()),float(x.max())]
    def within(key,a,b,lo,hi):
        x=span(key,a,b);return lo<=x[0] and x[1]<=hi
    if case.get('five_only'):
        checks['startup_regulation']=within('v(sensor_5v)',20,24,4.65,5.5)
        checks['no_false_startup_fault']=within('v(fault_5v_n)',10,24,3,3.4)
        checks['short_latched']=within('v(sensor_5v)',34,35,-.1,.1)
        checks['fault_asserted']=within('v(fault_5v_n)',34,44,-.1,.2)
        checks['off_after_short_removed']=within('v(sensor_5v)',36,44,-.1,.1)
        checks['explicit_reset_recovers']=within('v(sensor_5v)',74,75,4.65,5.5)
        checks['output_below_5_6V']=float(d['v(sensor_5v)'].max())<5.6
        result['final_output_range_V']=span('v(sensor_5v)',74,75)
        result['pass']=all(checks.values());return result
    out='v(boost_12v)' if case.get('boost_only') else 'v(sensor_12v)'
    checks['final_regulation']=within(out,case['end']-1,case['end'],11.4,12.6)
    result['final_output_range_V']=span(out,case['end']-1,case['end'])
    result['peak_output_V']=float(d[out].max())
    checks['output_below_13V']=result['peak_output_V']<13
    if case.get('limit_surrogate'):
        current=-d['i(vsrc)'][(t>=.020)&(t<=.050)]
        result['charging_source_current_A']=[float(current.min()),float(current.max())]
        checks['surrogate_limit_below_calculated_minimum']=.300<float(current.min()) and float(current.max())<.314699
        reached=np.flatnonzero(d[out]>=11.4)
        result['first_11_4V_ms']=float(t[reached[0]]*1000) if len(reached) else None
        checks['charged_before_startup_grace']=bool(len(reached) and t[reached[0]]<.200)
    if case.get('short'):
        result['short_input_A']=[-x for x in reversed(span('i(vsrc)',60,80))]
        checks['short_current_bounded']=result['short_input_A'][1]<.41
        checks['short_output_low']=within(out,60,80,-.1,.1)
        if 'hot_short' in case['name']:checks['pre_short_regulation']=within(out,35,44,11.4,12.6)
        if 'thermal_latch' in case['name']:
            checks['thermal_fault_asserted']=within('v(fault_12v_n)',900,999,-.1,.2)
            checks['latched_after_short_removed']=within(out,1005,1090,-.1,.1)
    if case.get('boost_only'):
        checks['full_load_regulation']=within(out,5.5,5.9,11.4,12.6)
        checks['fault_limit_load_regulation']=within(out,7.5,7.9,11.4,12.6)
        checks['step_excursion']=within(out,4,10,10.8,13.2)
    if not case.get('efuse_only'):
        result['peak_inductor_A']=float(d['i(l2)'].max())
        checks['inductor_linear_domain']=result['peak_inductor_A']<8
        checks['below_minimum_switch_current_limit']=result['peak_inductor_A']<2
        checks['boost_input_above_uvlo_after_start']=within('v(v5_internal)',5 if case.get('source') else .3,case['end'],2.4,5.5)
    if not case.get('boost_only') and 'cold_short' not in case['name']:
        stop=44 if case.get('short') else case['end']
        checks['no_false_startup_fault']=within('v(fault_12v_n)',.3,stop,3,3.4)
    result['pass']=all(checks.values());return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case',action='append',choices=[c['name'] for c in CASES])
    ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--reuse',action='store_true')
    ap.add_argument('--verify-report',action='store_true');ap.add_argument('--require-pass',action='store_true')
    args=ap.parse_args();WORK.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    prepare_models();parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
    electrical=json.loads((REPORT/'electrical_checks.json').read_text())
    assert abs(CASES[0]['vin']-electrical['buck']['with_40mV_regulation_budget_V'][0])<1e-6,'Update the low-input stress case for the revised buck budget'
    version=subprocess.check_output(['ngspice','--version'],text=True).strip()
    files=['tps61085.lib','tps2553-1.lib','tps259620.lib','B240A.lib']
    def digest(deck):return hashlib.sha256((deck+version+''.join(sha(WORK/f) for f in files)).encode()).hexdigest()
    if args.verify_report:
        report=json.loads((REPORT/'boost_spice.json').read_text())
        assert report['circuit_sha256']==sha(ROOT/'hardware/design/circuit.json')
        assert report['script_sha256']==sha(Path(__file__))
        assert report['sources']==json.loads((SOURCE/'manifest.json').read_text())
        assert [r['case'] for r in report['cases']]==CASES
        for r in report['cases']:
            assert r['deck_and_model_hash']==digest(circuit(r['case'],parts,electrical))
            assert r['pass']==all(r['checks'].values())
        repeat=report['combined_solver_repeat'];secondary=repeat['secondary']
        assert secondary['case']==combined_repeat_case()
        assert secondary['deck_and_model_hash']==digest(circuit(secondary['case'],parts,electrical))
        assert secondary['pass']==all(secondary['checks'].values())
        assert repeat['pass']==(secondary['pass'] and all(v<.05 for v in repeat['voltage_difference_V'].values()) and repeat['peak_inductor_difference_A']<.02)
        passed=all(r['pass'] for r in report['cases']) and report['timestep_repeat']['pass'] and repeat['pass']
        assert (report['result']=='PASS transient screening only')==passed
        if args.require_pass:assert passed
        print('PASS evidence integrity:',report['result']);return
    selected=[c for c in CASES if not args.case or c['name'] in args.case]
    def run(c):
        name=c.get('trace_name',c['name']);deck=circuit(c,parts,electrical);h=digest(deck);marker=WORK/f'{name}.complete'
        (WORK/f'{name}.cir').write_text(deck)
        if not (args.reuse and marker.exists() and marker.read_text()==h):
            marker.unlink(missing_ok=True)
            print('Running',name,flush=True)
            subprocess.run(['ngspice','-b','-o',f'{name}.log','-r',f'{name}.raw',f'{name}.cir'],cwd=WORK,stdout=subprocess.DEVNULL,check=True,timeout=8*3600)
            log=(WORK/f'{name}.log').read_text()
            if re.search(r'(?i)error|timestep too small|simulation interrupted',log):raise RuntimeError(f'Review {name}.log')
            warnings=[line for line in log.splitlines() if 'warning' in line.lower()]
            allowed=('Warning: singular matrix:', 'Warning: Dynamic gmin stepping failed', 'Warning: True gmin stepping failed', 'Warning: source stepping failed')
            assert all(line.startswith(allowed) for line in warnings), warnings
            # Initial zero-supply OP falls back to a successful transient operating point.
            if warnings: assert 'Transient op finished successfully' in log and 'No. of Data Rows' in log, log[:2000]
            d=read_raw(WORK/f'{name}.raw');assert d['time'][-1]>=c['end']/1000-1e-10;marker.write_text(h)
        d=read_raw(WORK/f'{name}.raw');r=evaluate(c,d);r['deck_and_model_hash']=h;r['simulated_netlist']=deck
        r['raw_trace_sha256']=sha(WORK/f'{name}.raw')
        r['initial_transient_OP_fallback']='Transient op finished successfully' in (WORK/f'{name}.log').read_text()
        (WORK/f'{name}.result.json').write_text(json.dumps(r,indent=2)+'\n')
        print(name,r['checks'],flush=True)
        grid=np.linspace(0,c['end']/1000,8000);return r,{n:np.interp(grid,d['time'],v) for n,v in d.items()}
    queued=selected+([combined_repeat_case()] if not args.case else [])
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:all_runs=list(pool.map(run,queued))
    runs=all_runs[:len(selected)]
    passed=all(r['pass'] for r,d in all_runs)
    report=dict(result='PASS transient screening only' if passed else 'FAIL',
        scope='Rev G vendor TPS61085/TPS259620/TPS2553-1 models, 27C typical silicon. Syntax-only ngspice ports; no PSpice/board correlation. Combined startup with a 4ms source ramp plus separate boost load/fault-limit steps, eFuse fault/reset cases and 5V-switch fault/reset. Not physical qualification.',
        source_assumptions='Boost cases: ideal upstream 5 V source, 120 milliohm series resistance, 25.92 uF internal capacitance, 0.4 A concurrent logic/5 V load. The standalone 5 V switch case instead has 1.3 A concurrent internal load. Standalone eFuse cases use an ideal 12.003 V source with 120 milliohm series resistance and 66 uF reservoir. Upstream buck control loop/current limit and PCB/cable inductance are not modeled.',
        passive_assumptions='Boost C60 and reservoir use explicit derated/nameplate case values; C61/C65/C71 1uF nominal. Inductor 3.3uH and 32mOhm DCR, linear below its 8A/20%-inductance-drop domain. External capacitor ESR .1ohm. One explicitly identified current-limit surrogate uses a 2.92k test resistor instead of fitted R62=2.61k, giving typical-model current below the calculated 314.699mA minimum, with 120uF external capacitance. This tests reduced charging headroom, not all silicon corners. D5 uses the B240A vendor model; D6 behavioral clamp approximates static conduction only. Q2 enable uses 2ohm final shunt resistance; standalone fault tests apply a finite 1us conductance ramp to avoid a discontinuous behavioral-device transition. No transistor timing claim. eFuse thermal timing is manufacturer-model-only, not temperature qualification.',
        numerical_notes='Gear integration, 1fF numerical node shunt, relative tolerance .003. Combined startup uses KLU/xtrtol=2 with maximum step 50 ns and a complete KLU/xtrtol=7 repeat at maximum step 25 ns; both must pass the same electrical criteria and the voltage/peak-current comparison. Original xtrtol=1 stopped numerically near 28.971 ms and is retained as an incomplete diagnostic. Vendor helper names prefixed; duplicate PARAMS removed and Boolean XOR syntax translated. No semiconductor parameters tuned. Standalone zero-supply operating-point warnings are accepted only after successful transient OP fallback and complete transient output. Other warnings/errors fail. Extreme values use all adaptive timesteps; plots decimated.',
        circuit_sha256=sha(ROOT/'hardware/design/circuit.json'),script_sha256=sha(Path(__file__)),
        simulator=version,sources=json.loads((SOURCE/'manifest.json').read_text()),cases=[r for r,d in runs])
    if not args.case:
        a=read_raw(WORK/'efuse_hot_short_and_reset.raw');b=read_raw(WORK/'efuse_hot_short_half_step.raw')
        grid=np.linspace(.003,.13,12701);keep=np.ones(len(grid),bool)
        for edge in [.045,.085,.090,.095]:keep &= np.abs(grid-edge)>10e-6
        delta={key:float(np.abs(np.interp(grid,a['time'],a[key])-np.interp(grid,b['time'],b[key]))[keep].max())
               for key in ['v(sensor_12v)','i(vsrc)']}
        converged=delta['v(sensor_12v)']<.05 and delta['i(vsrc)']<.005
        report['timestep_repeat']={'pass':converged,'max_step_s':[1e-6,.5e-6],
            'output_difference_V':delta['v(sensor_12v)'],'source_current_difference_A':delta['i(vsrc)'],
            'scope':'3-130ms at 10us sample intervals, excluding +/-10us around ideal test-switch edges; raw extrema separately checked in both cases.'}
        passed &= converged
        primary=runs[0][0];secondary=all_runs[-1][0]
        a=read_raw(WORK/'combined_low_input_capacitive_start.raw')
        b=read_raw(WORK/(combined_repeat_case()['trace_name']+'.raw'))
        grid=np.linspace(0,.040,80001)
        delta={key:float(np.abs(np.interp(grid,a['time'],a[key])-np.interp(grid,b['time'],b[key])).max())
               for key in ['v(v5_internal)','v(boost_12v)','v(sensor_12v)']}
        peak_delta=abs(primary['peak_inductor_A']-secondary['peak_inductor_A'])
        converged=secondary['pass'] and all(v<.05 for v in delta.values()) and peak_delta<.02
        report['combined_solver_repeat']={'pass':converged,'voltage_difference_V':delta,
            'peak_inductor_difference_A':peak_delta,'secondary':secondary,
            'scope':'Complete 0-40 ms comparison at 0.5 us intervals: KLU/Gear xtrtol=2, maximum step 50 ns, versus xtrtol=7, maximum step 25 ns, both with reltol=.003 and identical circuit/models. Each full adaptive trace independently passes all electrical criteria. Voltage differences must stay below 50 mV and peak-inductor difference below 20 mA. Numerical sensitivity, not physical correlation.'}
        passed &= converged
        if not passed:report['result']='FAIL'
    dest=WORK if args.case else REPORT;suffix='_partial' if args.case else ''
    (dest/f'boost_spice{suffix}.json').write_text(json.dumps(report,indent=2)+'\n')
    fig,axes=plt.subplots((len(runs)+1)//2,2,figsize=(12,3.2*((len(runs)+1)//2)),squeeze=False)
    for ax in axes.flat:ax.set_visible(False)
    for ax,(r,d) in zip(axes.flat,runs):
        ax.set_visible(True)
        for key,label in [('v(boost_12v)','Raw boost'),('v(sensor_12v)','Protected 12 V'),('v(fault_12v_n)','eFuse fault'),('v(sensor_5v)','Protected 5 V'),('v(fault_5v_n)','5 V fault')]:
            if key in d:ax.plot(d['time']*1000,d[key],label=label,lw=1)
        if not args.case and r['case']==CASES[0]:
            repeat_data=all_runs[-1][1]
            repeat_label='25 ns repeat '+('PASS' if report['combined_solver_repeat']['pass'] else 'FAIL')
            ax.plot(repeat_data['time']*1000,repeat_data['v(sensor_12v)'],'--',label=repeat_label,lw=.8)
        ax.set_title(r['case']['name'].replace('_',' ')+' — '+('PASS' if r['pass'] else 'FAIL'),fontsize=9)
        ax.set_xlabel('ms');ax.set_ylabel('V');ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.suptitle('Rev G transient screening — '+('PASS' if passed else 'FAIL')+'\nVendor models, idealized upstream supply');fig.tight_layout()
    fig.savefig(dest/f'boost_spice{suffix}.png',dpi=150);plt.close(fig)
    raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
