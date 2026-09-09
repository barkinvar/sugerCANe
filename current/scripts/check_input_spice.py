"""Screen three sensor inputs with TI's LM393LV model linked for LM339LV.

Bias FETs, blocking diode and sensors are bounded circuit abstractions. This
complements the independent DC corner budget; it does not qualify real sensors.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
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
from check_boost_spice import read_raw

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'tmp/spice/input-screen'
REPORT = ROOT / 'reports/electrical/input_spice.json'
CASES = ['pushpull', 'logic_limits', 'npn', 'pnp', 'float_open',
         'float_driven', 'hysteresis', 'supply_reset', 'pushpull_half_step', 'logic_limits_half_step']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_deck(name, parts):
    base = name.removesuffix('_half_step')
    def passive(ref):
        item = parts[ref]
        pins = ['0' if n == 'GND' else n for n in item['pins'].values()]
        value = item['value'].removesuffix('F').replace('M', 'meg')
        return f'{ref} {" ".join(pins)} {value}'

    assert parts['U7']['mpn'] == 'LM339LVDR'
    for ch in range(1,4):
        assert parts[f'R{ch}10']['value'] == '1k' and parts[f'R{ch}09']['value'] == '10k'
    # 15 ohm hot FET and 0.55 V forward-diode allowances match the DC budget.
    rail = 3.3 * (.97 if name == 'npn' else 1)
    supply = ('PWL(0 0 1m 3.3 8m 3.3 9m 0 11m 0 12m 3.3)'
              if name == 'supply_reset' else str(rail))
    lines = [name, '.include lm393lv.lib', f'VDD +3V3 0 {supply}']
    lines += [passive(r) for r in ['R50', 'R51', 'C51', 'R52']]
    for ch in range(1, 4):
        sig, sense, out = f'SIG{ch}', f'SENSE{ch}', f'INPUT{ch}'
        for n in ['01', '03', '04', '05']:
            lines.append(passive(f'R{ch}{n}'))
        lines.append(passive(f'C{ch}01'))
        cmp_pin = [('5', '4', '2'), ('7', '6', '1'), ('9', '8', '14')][ch-1]
        assert [parts['U7']['pins'][p] for p in cmp_pin] == [sense, 'REF_LOGIC', out]
        lines += [f'Xcmp{ch} {sense} REF_LOGIC +3V3 0 {out} LM393LV',
                  f'Ccable{ch} {sig} 0 {[.1, 1, 10][ch-1]}n']
        high = [3.3, 5, 24][ch-1]
        if base in ['pushpull', 'logic_limits']:
            if base == 'logic_limits':
                high = [30, 2.4, 1.2][ch-1]
            lines += [f'Vsig{ch} DRIVER{ch} 0 PWL(0 0 4m 0 4.001m {high} 8m {high} 8.001m 0)',
                      f'Rdriver{ch} DRIVER{ch} {sig} 10']
        elif name == 'npn':
            lines += [f'Bup{ch} +3V3 {sig} I={{max(0,(v(+3V3)-v({sig})-.55)/1015)}}',
                      f'Bleak{ch} {sig} 0 I={{100u*(1-v(ACT))}}',
                      f'Vsat{ch} LOW{ch} 0 1.2',
                      f'Bsink{ch} {sig} LOW{ch} I={{v(ACT)*max(0,(v({sig})-1.2)/.05)}}']
        elif name == 'pnp':
            lines += [f'Rdown{ch} {sig} 0 10015',
                      f'Bleak{ch} 0 {sig} I={{100u*(1-v(ACT))}}',
                      f'Vhigh{ch} HIGH{ch} 0 {high}',
                      f'Bsource{ch} HIGH{ch} {sig} I={{v(ACT)*max(0,({high}-v({sig}))/10)}}']
        elif name in ['float_open', 'float_driven']:
            lines += [f'Bup{ch} +3V3 {sig} I={{v(UP)*max(0,(v(+3V3)-v({sig})-.55)/1015)}}',
                      f'Bdown{ch} {sig} 0 I={{(1-v(UP))*v({sig})/10015}}']
            if name == 'float_driven':
                lines += [f'Vsig{ch} DRIVER{ch} 0 {[1.2,2.4,3.3][ch-1]}',
                          f'Rdriver{ch} DRIVER{ch} {sig} .05']
        elif name == 'hysteresis':
            lines.append(f'Vsig{ch} {sig} 0 PWL(0 0 3m 0 5m 3.3 7m 3.3 9m 0)')
        elif name == 'supply_reset':
            lines.append(f'Vsig{ch} {sig} 0 {[0,3.3,30][ch-1]}')
    if name in ['npn', 'pnp']:
        lines.append('Vact ACT 0 PWL(0 0 4m 0 4.01m 1 8m 1 8.01m 0)')
    if name.startswith('float_'):
        lines.append('Vup UP 0 PWL(0 1 4m 1 4.01m 0 6m 0 6.01m 1 8m 1 8.01m 0 10m 0 10.01m 1)')
    signals = ['+3V3', 'REF_LOGIC'] + [f'{s}{ch}' for ch in range(1,4) for s in ['SIG','SENSE','INPUT']]
    lines += ['.save ' + ' '.join(f'v({s})' for s in signals),
              '.options method=trap reltol=.001 abstol=1p vntol=1u',
              '.tran 500n 16m 0 ' + ('500n' if name.endswith('_half_step') else '1u'), '.end']
    return '\n'.join(lines) + '\n'


def evaluate(name, d):
    base = name.removesuffix('_half_step')
    t = d['time']; checks = {}; details = {}
    assert t[-1] >= .016 - 1e-10
    def level(ch, lo, hi, high):
        v = d[f'v(input{ch})'][(t >= lo/1000) & (t <= hi/1000)]
        assert len(v)
        return bool(np.min(v) > .7 * 3.3) if high else bool(np.max(v) < .3 * 3.3)
    for ch in range(1,4):
        checks[f'ch{ch}_sense_safe_range'] = bool(d[f'v(sense{ch})'].min() > -.1 and d[f'v(sense{ch})'].max() < 5.5)
        checks[f'ch{ch}_output_rail_bounds'] = bool(d[f'v(input{ch})'].min() > -.3 and d[f'v(input{ch})'].max() < 3.6)
        if base in ['pushpull', 'logic_limits', 'npn', 'pnp']:
            active_high = name != 'npn' and not (base == 'logic_limits' and ch == 3)
            idle_high = name == 'npn'
            checks[f'ch{ch}_inactive_before'] = level(ch,3,3.9,idle_high)
            checks[f'ch{ch}_active'] = level(ch,6,7.9,active_high)
            checks[f'ch{ch}_inactive_after'] = level(ch,10,15,idle_high)
        elif name.startswith('float_'):
            for ms, up in [(3.9,True),(5.9,False),(7.9,True),(9.9,False),(11.9,True)]:
                expected = up if name == 'float_open' else ch != 1
                checks[f'ch{ch}_probe_{ms}ms'] = level(ch,ms,ms+.05,expected)
        elif name == 'hysteresis':
            state=d[f'v(input{ch})']>1.65
            rising=np.flatnonzero(~state[:-1]&state[1:]);falling=np.flatnonzero(state[:-1]&~state[1:])
            rising=rising[t[rising]>.003];falling=falling[t[falling]>.003]
            checks[f'ch{ch}_one_rising_and_falling_edge']=len(rising)==len(falling)==1
            if len(rising)==len(falling)==1:
                vr=float(d[f'v(sig{ch})'][rising[0]]);vf=float(d[f'v(sig{ch})'][falling[0]])
                checks[f'ch{ch}_threshold_and_hysteresis']=1.2<vf<vr<2.4
                details[f'ch{ch}_threshold_V']={'rising':vr,'falling':vf}
        elif name == 'supply_reset':
            checks[f'ch{ch}_on']=level(ch,4,7,ch!=1)
            checks[f'ch{ch}_off']=level(ch,10,10.9,False)
            checks[f'ch{ch}_recovered']=level(ch,15,16,ch!=1)
    return {'name':name,'pass':all(checks.values()),'checks':checks,'measurements':details,
            'trace_complete':True,'final_time_s':float(t[-1]),'samples':len(t)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jobs',type=int,default=4)
    ap.add_argument('--verify-report',action='store_true')
    args=ap.parse_args();WORK.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sources/spice/lm393lv.lib'
    manifest=json.loads(source.with_name('input_manifest.json').read_text())
    assert sha(source)==manifest['sha256']
    shutil.copyfile(source,WORK/source.name)
    (WORK/'.spiceinit').write_text('set ngbehavior=psa\n')
    parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
    version=subprocess.check_output(['ngspice','--version'],text=True).strip()
    if args.verify_report:
        report=json.loads(REPORT.read_text())
        assert report['circuit_sha256']==sha(ROOT/'hardware/design/circuit.json')
        assert report['script_sha256']==sha(Path(__file__)) and report['model']==manifest
        assert report['simulator']==version
        assert [r['name'] for r in report['cases']]==CASES
        for r in report['cases']:
            assert r['netlist']==make_deck(r['name'],parts)
            assert r['trace_complete'] and r['final_time_s']>=.016-1e-10
            assert r['pass']==all(r['checks'].values())
        assert report['result']=='PASS input transient screening only'
        assert all(r['pass'] for r in report['cases']) and report['timestep_repeat']['pass']
        assert all(v<.05 for v in report['timestep_repeat']['max_output_difference_V'].values())
        print('PASS input transient report integrity');return
    REPORT.write_text(json.dumps(dict(result='INCOMPLETE',reason='Input transient run in progress or interrupted',
                                     circuit_sha256=sha(ROOT/'hardware/design/circuit.json'),
                                     script_sha256=sha(Path(__file__))),indent=2)+'\n')
    def run(name):
        deck=make_deck(name,parts);(WORK/f'{name}.cir').write_text(deck)
        subprocess.run(['ngspice','-b','-o',f'{name}.log','-r',f'{name}.raw',f'{name}.cir'],
                       cwd=WORK,check=True,stdout=subprocess.DEVNULL,timeout=120)
        log=(WORK/f'{name}.log').read_text()
        assert not re.search(r'(?i)error|warning|timestep too small|simulation interrupted',log),name
        data=read_raw(WORK/f'{name}.raw');result=evaluate(name,data)
        result.update(netlist=deck,raw_sha256=sha(WORK/f'{name}.raw'))
        (WORK/f'{name}.result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(name,result['pass'],flush=True)
        return result,data
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results=list(pool.map(run,CASES))
    grid=np.linspace(0,.016,32001)
    keep=np.ones(len(grid),dtype=bool)
    for edge in [.004,.008]:keep &= np.abs(grid-edge)>100e-6
    delta={}
    for name in ['pushpull','logic_limits']:
        a=results[CASES.index(name)][1];b=results[CASES.index(name+'_half_step')][1]
        delta[name]=max(float(np.max(np.abs(np.interp(grid,a['time'],a[f'v(input{ch})'])-
                                           np.interp(grid,b['time'],b[f'v(input{ch})']))[keep])) for ch in range(1,4))
    repeat_pass=all(v<.05 for v in delta.values())
    passed=all(r['pass'] for r,d in results) and repeat_pass
    report=dict(result='PASS input transient screening only' if passed else 'FAIL',
                circuit_sha256=sha(ROOT/'hardware/design/circuit.json'),script_sha256=sha(Path(__file__)),
                model=manifest,simulator=version,cases=[r for r,d in results],
                timestep_repeat={'pass':repeat_pass,'max_output_difference_V':delta,'maximum_steps_us':[1,.5],
                                 'comparison':'0-16 ms, excluding +/-100 us around driven edges; all raw samples still checked for voltage limits'},
                numerical_notes='Trapezoidal integration, reltol=.001, no artificial node shunt. Both nominal and logic-limit cases repeat at half the maximum timestep. Initial Gear integration failed numerically during the 30 V transition; it is not passing evidence or evidence of hardware failure.',
                assumptions='TI LM393LV model linked for LM339LV, typical 600 ns delay, offset and 60 ohm output. Native divider/feedback/reference RC values and all three channels. Cable capacitances 0.1/1/10 nF. Bias FET on-resistance 15 ohm and blocking diode 0.55 V; ideal reverse blocking. NPN/PNP OFF leakage 100 uA. Controlled sensor/bias changes take 1-10 us.',
                limitations='No actual MOSFET gate/reset timing, diode leakage dynamics, cable inductance, EMC, package coupling, temperature corners or external sensor startup model. DC corner/leakage checks remain separate. Off-supply case checks this comparator model, not whole-board backfeed. No physical qualification.')
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    fig,axes=plt.subplots(4,2,figsize=(12,11))
    for ax,(r,d) in zip(axes.flat,results[:8]):
        idx=np.linspace(0,len(d['time'])-1,min(5000,len(d['time']))).astype(int)
        for ch in range(1,4):ax.plot(d['time'][idx]*1000,d[f'v(input{ch})'][idx],label=f'Input {ch}',lw=.8)
        ax.set_title(r['name'].replace('_',' ')+' — '+('PASS' if r['pass'] else 'FAIL'))
        ax.set_xlabel('Time (ms)');ax.set_ylabel('Comparator output (V)');ax.legend(fontsize=7);ax.grid(alpha=.2)
    fig.suptitle('Rev H input transient screen — typical comparator model and bounded bias abstractions')
    fig.tight_layout();fig.savefig(REPORT.with_suffix('.png'),dpi=150);plt.close(fig)
    if not passed:raise SystemExit(1)


if __name__=='__main__':
    main()
