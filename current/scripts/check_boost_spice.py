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
CURVE = ROOT / 'sources/datasheets/samsung_CL31A226_characteristics.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_models():
    for entry in json.loads((SOURCE / 'manifest.json').read_text()):
        assert sha(SOURCE / entry['file']) == entry['sha256'], entry['file']
    for name, prefix in [('tps61085.lib', 'BST_'), ('tps2553-1.lib', 'SW_')]:
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


def capacitor_curve_function():
    """Piecewise-linear differential C(V), at 1 V intervals, typical 25 C data.

    ngspice's behavioral C= implements C(V)*dV/dt (not d(C(V)*V)/dt).
    Coefficients use hinge functions; outside 0..25 V retain endpoint C.
    """
    charts = json.loads(CURVE.read_text())
    data = next(c for c in charts if c['graphType'] == 'DCBias')['selectPartsList'][0]['chartList'][0]['data']
    grid = np.arange(26.)
    capacitance = 22e-6 * (1 + np.interp(grid, [float(p['x']) for p in data], [float(p['y']) for p in data]) / 100)
    slopes = np.r_[np.diff(capacitance), 0]
    terms = [f'{capacitance[0]:.12g}']
    for index, delta in enumerate(np.diff(np.r_[0, slopes])):
        if abs(delta) > 1e-18:
            terms.append(f'({delta:.12g})*max(x-{grid[index]:g},0)')
    return '.func capc(x) {' + '+'.join(terms) + '}'


def circuit(case, parts, electrical):
    def value(ref):
        return parts[ref]['value'].removesuffix('F').removesuffix('H')

    def nets(ref):
        return [net if net != 'GND' else '0' for net in parts[ref]['pins'].values()]

    def pins(ref, order):
        return ' '.join(parts[ref]['pins'][str(pin)] if parts[ref]['pins'][str(pin)] != 'GND' else '0' for pin in order)

    assert parts['U8']['mpn'] == 'TPS61085DGKR'
    assert parts['U9']['mpn'] == 'TPS2553DBVR-1'
    assert parts['D4']['mpn'] == 'B240A-13-F'
    assert parts['L2']['mpn'] == 'SRP5030TA-3R3M'
    assert parts['R63']['value'] == '13k' and parts['C69']['value'] == '33nF'
    for ref in ['C60', 'C62', 'C63', 'C64']:
        assert parts[ref]['mpn'] == 'CL31A226KAHNNNE' and parts[ref]['value'] == '22uF'
    assert nets('C60') == ['V5_BOOST', '0']
    assert all(nets(ref) == ['SENSOR_12V', '0'] for ref in ['C62','C63','C64'])
    vin = case.get('vin', electrical['buck']['nominal_V'])
    source = case.get('source', f'0 0 100u 0 200u {vin}')
    lines = [case['name'], '.include tps61085.lib', '.include tps2553-1.lib', '.include B240A.lib',
             f'Vsrc SOURCE 0 PWL({source})',
             'Rsource SOURCE V5_INTERNAL 0.05',
             'Cinternal V5_INTERNAL 0 25.92u',
             f'Bother V5_INTERNAL 0 I={{{case.get("other", 0.4)}*limit(v(V5_INTERNAL),0,1)}}',
             f'Xu9 {pins("U9", [1,2,3])} 0 {pins("U9", [4,5,6])} SW_TPS2553-1_TRANS',
             'Vlogic LOGIC 0 3.3', 'Rfault LOGIC PG_12V 40k']
    if case.get('bias_curve'):
        lines.insert(4, capacitor_curve_function())
    # U9 model's fourth pin is the DRV exposed pad; tie to common ground for DBV.
    # Only U9 /FAULT is modeled, not the parallel U7D voltage monitor.
    for ref in ['R62']:
        lines.append(f'{ref} {" ".join(nets(ref))} {value(ref)}')
    if case.get('switch_only'):
        lines += ['Cload V5_BOOST 0 8.64u', 'Rload V5_BOOST 0 10']
        output = 'V5_BOOST'
    else:
        lines += [f'Xu8 {pins("U8", [3,2,6,8,4,5,1,7])} BST_TPS61085',
                  f'L2 {nets("L2")[0]} LX {value("L2")}',
                  f'Rdcr LX {nets("L2")[1]} 0.032',
                  f'D4 {pins("D4", [2,1])} DI_B240A',
                  'Rcin V5_BOOST CI 0.01', f'Cin CI 0 {case.get("cin", 8.64)}u',
                  'Rcout SENSOR_12V CO 0.01', f'Cout CO 0 {case.get("cout", 10.8238)}u',
                  # Rail monitor upper divider is a small additional load.
                  'Rmonitor SENSOR_12V 0 101.8k']
        for ref in ['C61', 'C65', 'C66', 'R60', 'R61', 'R63', 'C69']:
            component_value = case.get('css', value(ref)) if ref == 'C66' else value(ref)
            lines.append(f'{ref} {" ".join(nets(ref))} {component_value}')
        if case.get('steps'):
            lines += ['Vload LOAD_CMD 0 PWL(0 0.03 5m 0.03 5.01m 0.3 7m 0.3 7.01m 0)',
                      'Bload SENSOR_12V 0 I={v(LOAD_CMD)*limit(v(SENSOR_12V),0,1)}']
        else:
            lines += ['Rload SENSOR_12V 0 40']
        if case.get('extra_cap'):
            lines += ['Rexternal SENSOR_12V EC 0.1', f'Cexternal EC 0 {case["extra_cap"]}u']
        if case.get('bias_curve'):
            lines = ['Cin CI 0 C={capc(v(CI))}' if line.startswith('Cin CI ') else
                     'Cout CO 0 C={3*capc(v(CO))}' if line.startswith('Cout CO ') else line for line in lines]
        output = 'SENSOR_12V'
    if case.get('short'):
        lines += [f'Vshort SHORT_CMD 0 PWL({case["short"]})',
                  f'Sshort {output} 0 SHORT_CMD 0 SHORT_MODEL',
                  '.model SHORT_MODEL SW(Ron=0.05 Roff=1e9 Vt=0.5 Vh=0.1)']
    save = '.save v(V5_INTERNAL) v(V5_BOOST) v(PG_12V) i(Vsrc)'
    if case.get('diagnostic'):
        save = save.replace('.save ', '.save v(xu9.u1_ios_delay) v(xu9.u1_ios_latch) v(xu9.u1_toggle) ')
    if not case.get('switch_only'):
        save += ' v(SENSOR_12V) v(BOOST_SS) v(BOOST_COMP) i(L2)'
    lines += [save, '.temp 25',
              '.options method=gear reltol=0.003 abstol=10n vntol=10u itl1=1000 itl4=1000',
              f'.tran 100n {case["end"]}m 0 {case.get("step", "25n")}', '.end']
    return '\n'.join(lines) + '\n'


CASES = [
    dict(name='switch_sanity', switch_only=True, other=0, end=50, step='1u',
         source='0 0 100u 0 200u 5.067 35m 5.067 35.1m 0 40m 0 40.1m 5.067',
         short='0 0 10m 0 10.001m 1 25m 1 25.001m 0'),
    dict(name='startup_full_load', end=6),
    dict(name='startup_half_timestep', end=6, step='12.5n'),
    dict(name='load_steps', steps=True, end=10),
    dict(name='low_input_capacitive_start', vin=4.913149, cout=66, extra_cap=100, end=12),
    dict(name='hot_short_reset', end=25,
         short='0 0 5m 0 5.001m 1 14m 1 14.001m 0',
         source='0 0 100u 0 200u 5.067 17m 5.067 17.1m 0 19m 0 19.1m 5.067'),
    dict(name='cold_short', end=16, short='0 1 12m 1 12.001m 0'),
    dict(name='startup_nominal_caps', vin=4.913149, cin=22, cout=66, end=10),
]

# Diagnostic variants; never substitute their results for the maintained board.
EXPERIMENTS = [
    dict(name='softstart_220n', vin=4.913149, cout=66, extra_cap=100, css='220n', end=14),
    dict(name='softstart_330n', vin=4.913149, cout=66, extra_cap=100, css='330n', end=14),
    dict(name='switch_rapid_reset', switch_only=True, diagnostic=True, other=0, end=50, step='1u',
         source='0 0 100u 0 200u 5.067 17m 5.067 17.1m 0 19m 0 19.1m 5.067',
         short='0 0 5m 0 5.001m 1 14m 1 14.001m 0'),
    dict(name='typical_bias_curve', bias_curve=True, end=7),
]


def evaluate(case, d):
    t = d['time']
    def window(key, start, end):
        mask = (t >= start / 1000) & (t <= end / 1000)
        assert mask.any(), (key, start, end)
        return d[key][mask]
    def span(key, start, end):
        v = window(key, start, end)
        return [float(v.min()), float(v.max())]
    def within(key, start, end, low, high):
        bounds = span(key, start, end)
        return low <= bounds[0] and bounds[1] <= high
    fault = 'v(pg_12v)'
    out = 'v(v5_boost)' if case.get('switch_only') else 'v(sensor_12v)'
    result = dict(case=case, checks={}, output_peak_V=float(d[out].max()))
    check = result['checks']
    assert t[-1] >= case['end'] / 1000 - 1e-10, 'Transient stopped early'
    if case.get('switch_only'):
        rapid = case['name'] == 'switch_rapid_reset'
        check['normal_output'] = within(out, 4, 4.9 if rapid else 9, 4.8, 5.1)
        current = -window('i(vsrc)', 6 if rapid else 11, 11 if rapid else 16)
        result['limited_input_A'] = [float(current.min()), float(current.max())]
        check['current_limit'] = bool(1.1 < current.min() <= current.max() < 1.3)
        a, b = (14.5, 16.5) if rapid else (26, 34)
        check['latched_after_short_removed'] = within(out, a, b, -0.01, 0.1) and within(fault, a, b, 0, 0.1)
        check['power_cycle_recovers'] = within(out, 24 if rapid else 44, 30 if rapid else 50, 4.8, 5.1)
        short_time = .005001 if rapid else .010001
        k = np.where((t > short_time + .00001) & (d[fault] < .1))[0][0]
        result['fault_delay_ms'] = float((t[k] - short_time) * 1000)
        if rapid:
            result['deglitch_state_while_unpowered'] = span('v(xu9.u1_ios_delay)', 17.2, 18.9)
    elif case['name'] in ('hot_short_reset', 'cold_short'):
        a, b = (14.5, 16.5) if case['name'] == 'hot_short_reset' else (13, 16)
        check['remains_latched_after_removing_short'] = within('v(v5_boost)', a, b, -0.1, 0.1) and within(fault, a, b, 0, .1)
        if case['name'] == 'hot_short_reset':
            check['regulated_before_short'] = within(out, 4.5, 4.9, 11.4, 12.6)
            check['recovers_after_power_cycle'] = within(out, 24, 25, 11.4, 12.6)
    else:
        check['no_false_latch'] = within(fault, .2, case['end'], 3, 3.4)
        above_uvlo = d['v(v5_boost)'] > 2.29
        result['boost_input_uvlo_drops'] = int(np.count_nonzero(above_uvlo[:-1] & ~above_uvlo[1:]))
        check['final_regulation'] = within(out, case['end']-1, case['end'], 11.4, 12.6)
        result['final_output_range_V'] = span(out, case['end']-1, case['end'])
        reached = np.where(d[out] >= 11.4)[0]
        result['first_11_4V_ms'] = float(t[reached[0]] * 1000) if len(reached) else None
        if case.get('steps'):
            result['load_step_range_V'] = span(out, 4.9, 10)
            check['step_excursion_within_10_8_to_13_2V'] = within(out, 4.9, 10, 10.8, 13.2)
            check['full_load_regulation'] = within(out, 6.5, 6.9, 11.4, 12.6)
        else:
            grid = np.linspace((case['end']-1)/1000, case['end']/1000, 10000)
            result['steady_total_5V_input_A'] = float(np.mean(np.interp(grid, t, -d['i(vsrc)'])))
    if not case.get('switch_only'):
        result['peak_inductor_A'] = float(d['i(l2)'].max())
        if case.get('short'):
            # 8 A is the manufacturer's 20%-inductance-drop rating, not a
            # destruction threshold. Crossing it invalidates a linear-L peak.
            check['linear_inductor_model_within_8A_domain'] = result['peak_inductor_A'] <= 8
            result['time_above_8A_us'] = float(np.sum(np.diff(t) * (d['i(l2)'][:-1] > 8)) * 1e6)
    result['pass'] = all(check.values())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--case', action='append', choices=[c['name'] for c in CASES + EXPERIMENTS])
    parser.add_argument('--reuse', action='store_true', help='Reuse completed traces only when model/deck hashes match')
    parser.add_argument('--verify-report', action='store_true', help='Check saved evidence matches this circuit, script and source models without rerunning SPICE')
    parser.add_argument('--require-pass', action='store_true', help='Reject saved evidence with any failed screening criteria')
    args = parser.parse_args()
    if args.verify_report:
        report = json.loads((REPORT / 'boost_spice.json').read_text())
        assert report['result'] in ['PASS transient screening only', 'FAIL']
        assert report['circuit_sha256'] == sha(ROOT / 'hardware/design/circuit.json')
        assert report['script_sha256'] == sha(Path(__file__))
        assert report['electrical_sha256'] == sha(REPORT / 'electrical_checks.json')
        assert report['capacitor_curve_sha256'] == sha(CURVE)
        assert report['sources'] == json.loads((SOURCE / 'manifest.json').read_text())
        for entry in report['sources']:
            assert sha(SOURCE / entry['file']) == entry['sha256']
        assert [row['case'] for row in report['cases']] == CASES
        assert all(row['pass'] == all(row['checks'].values()) for row in report['cases'])
        expected_pass = all(row['pass'] for row in report['cases']) and report['timestep_repeat']['pass']
        assert (report['result'] == 'PASS transient screening only') == expected_pass
        experiments = REPORT / 'boost_spice_experiments.json'
        if experiments.exists():
            diagnostic = json.loads(experiments.read_text())
            assert diagnostic['circuit_sha256'] == report['circuit_sha256']
            assert diagnostic['script_sha256'] == report['script_sha256']
            assert diagnostic['capacitor_curve_sha256'] == report['capacitor_curve_sha256']
            assert [row['case'] for row in diagnostic['cases']] == EXPERIMENTS
            parts = json.loads((ROOT / 'hardware/design/circuit.json').read_text())['parts']
            budgets = json.loads((REPORT / 'electrical_checks.json').read_text())
            for row in diagnostic['cases']:
                assert row['pass'] == all(row['checks'].values())
                assert row['simulated_netlist'].splitlines()[1:] == circuit(row['case'], parts, budgets).splitlines()[1:]
        print('PASS evidence integrity: SPICE report matches circuit, budgets, script and models. Screening outcome: ' + report['result'])
        if args.require_pass and not expected_pass:
            raise SystemExit('Unresolved transient screening findings; see docs/VALIDATION.md')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    prepare_models()
    parts = json.loads((ROOT / 'hardware/design/circuit.json').read_text())['parts']
    electrical = json.loads((REPORT / 'electrical_checks.json').read_text())
    simulator = shutil.which('ngspice')
    if not simulator:
        raise SystemExit('Install ngspice with XSPICE/PSpice compatibility support; tested version 42')
    version = subprocess.check_output([simulator, '--version'], text=True).strip()
    selected = [c for c in CASES + EXPERIMENTS if (not args.case and c in CASES) or (args.case and c['name'] in args.case)]
    def run(case):
        name = case['name']
        deck = WORK / f'{name}.cir'
        deck.write_text(circuit(case, parts, electrical))
        digest = hashlib.sha256((deck.read_text() + version + ''.join(sha(WORK / n) for n in ['tps61085.lib','tps2553-1.lib','B240A.lib'])).encode()).hexdigest()
        marker = WORK / f'{name}.complete'
        if not (args.reuse and marker.exists() and marker.read_text() == digest):
            marker.unlink(missing_ok=True)
            print(f'Running {name}', flush=True)
            subprocess.run([simulator, '-b', '-o', f'{name}.log', '-r', f'{name}.raw', deck.name], cwd=WORK, stdout=subprocess.DEVNULL, check=True, timeout=1800)
            log = (WORK / f'{name}.log').read_text()
            if re.search(r'(?i)error|timestep too small|simulation interrupted|warning', log):
                raise RuntimeError(f'Review simulator diagnostic: {WORK / (name + ".log")}')
            d = read_raw(WORK / f'{name}.raw')
            assert d['time'][-1] >= case['end']/1000 - 1e-10
            marker.write_text(digest)
        d = read_raw(WORK / f'{name}.raw')
        result = evaluate(case, d)
        result['deck_and_model_hash'] = digest
        # Uniform sampling avoids giving densely sampled switching edges more weight.
        grid = np.linspace(0, case['end']/1000, 6000)
        compact = {n: np.interp(grid, d['time'], v) for n, v in d.items()}
        print(f'{name}: {"PASS" if result["pass"] else "FAIL"} {result["checks"]}', flush=True)
        return result, compact
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        runs = list(pool.map(run, selected))
    repeat = None
    by_name = {r[0]['case']['name']: r[0] for r in runs}
    if 'startup_full_load' in by_name and 'startup_half_timestep' in by_name:
        a, b = (by_name[n] for n in ['startup_full_load', 'startup_half_timestep'])
        delta_ms = abs(a['first_11_4V_ms'] - b['first_11_4V_ms']) if a['first_11_4V_ms'] is not None and b['first_11_4V_ms'] is not None else 1e9
        delta_v = max(abs(x-y) for x,y in zip(a['final_output_range_V'], b['final_output_range_V']))
        repeat = dict(startup_time_difference_ms=delta_ms, steady_extrema_difference_V=delta_v,
                      pass_condition='Startup crossing within 0.1 ms and steady extrema within 30 mV; not a full simulator-port validation',
                      **{'pass': delta_ms < .1 and delta_v < .03})
    passed = all(r[0]['pass'] for r in runs) and (repeat is None or repeat['pass'])
    report = dict(result='PASS transient screening only' if passed else 'FAIL', timestep_repeat=repeat,
                  scope='U9 + U8 + D4 vendor models, 25 C typical silicon. Behavioral models ported to ngspice, not correlated against PSpice or a board. Not whole-board qualification.',
                  source_assumptions='Ideal ramped 5 V source with 50 milliohm series resistance, 25.92 uF reservoir and 0.4 A simultaneous logic/5 V load except switch sanity. No LMR51420 control loop/current limit, no regulator ripple, no thermal/PCB/cable parasitic extraction.',
                  passive_assumptions='Defaults: C60 fixed 8.64 uF, output bank fixed 10.8238 uF. Case cin/cout/extra_cap fields override these. Diagnostic bias_curve=true uses Samsung typical differential C(V), interpolated at 1 V intervals; css overrides C66 only in a hypothetical experiment. ESR 10 milliohm assumed; inductor DCR 32 milliohm from Bourns typical value. No magnetic saturation, dielectric hysteresis or thermal model. 50 milliohm idealized short. PG trace represents U9 /FAULT only.',
                  numerical_notes='PSpice Boolean XOR translated to !=; duplicate PARAMS removed; helper subcircuits/models namespaced. Gear integration avoids observed trapezoidal artificial latch reset. No semiconductor parameter tuning. Adaptive raw points used for extrema; overview plot decimated and cannot show switching ripple or short-current peaks.',
                  simulator=version, circuit_sha256=sha(ROOT / 'hardware/design/circuit.json'),
                  script_sha256=sha(Path(__file__)), electrical_sha256=sha(REPORT / 'electrical_checks.json'),
                  capacitor_curve_sha256=sha(CURVE),
                  sources=json.loads((SOURCE / 'manifest.json').read_text()), cases=[r[0] for r in runs])
    suffix = '_partial' if args.case else ''
    destination = WORK if args.case else REPORT
    (destination / f'boost_spice{suffix}.json').write_text(json.dumps(report, indent=2) + '\n')
    columns = min(2, len(runs))
    rows = (len(runs) + columns - 1) // columns
    fig, axes = plt.subplots(rows, columns, figsize=(12, 3.1*rows), squeeze=False)
    for ax in axes.flat[len(runs):]:
        ax.set_visible(False)
    for ax, (r, d) in zip(axes.flat, runs):
        t = d['time'] * 1000
        for key, label in [('v(sensor_12v)','12 V output'),('v(v5_boost)','Boost input'),('v(pg_12v)','U9 /FAULT')]:
            if key in d:
                ax.plot(t, d[key], label=label, lw=1)
        ax.set_title(r['case']['name'].replace('_', ' ') + (' — PASS' if r['pass'] else ' — FAIL'), fontsize=10)
        ax.set_ylabel('Voltage (V)'); ax.set_xlabel('Time (ms)'); ax.grid(alpha=.2)
        ax.legend(loc='best', fontsize=8)
    fig.suptitle('Rev F manufacturer-model transient screening\nIdealized upstream supply; no thermal or physical qualification', fontsize=12)
    fig.tight_layout(rect=(0,0,1,.96))
    fig.savefig(destination / f'boost_spice{suffix}.png', dpi=150)
    plt.close(fig)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
