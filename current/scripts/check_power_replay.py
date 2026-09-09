"""Replay completed SPICE rail traces through the actual firmware power monitor.

One-way replay at 1 ms; commanded shutdown does not feed back into SPICE.
This checks monitor timing and ADC-error margins, not hardware/software co-simulation.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess
import numpy as np
from check_boost_spice import read_raw

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'tmp/power-replay'
REPORT=ROOT/'reports/electrical/power_replay.json'
RUNNER=r'''#include "power.h"
#include <stdio.h>
int main(void) {
 sc_power p; sc_power_init(&p,0,true);
 unsigned t,a,b,f;
 while(scanf("%u,%u,%u,%u",&t,&a,&b,&f)==4) {
  if(a>65535||b>65535||f>3)return 2;
  sc_power_update(&p,t,true,(uint16_t)a,(uint16_t)b,(uint8_t)f);
  printf("%u,%u,%u,%u\n",t,p.enabled,p.good,p.latched);
 }
 return ferror(stdin)?1:0;
}
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--traces',type=Path,default=ROOT/'tmp/spice')
 ap.add_argument('--verify-report',action='store_true')
 args=ap.parse_args()
 power_report='reports/electrical/boost_spice.json'
 if json.loads((ROOT/power_report).read_text())['result']!='PASS transient screening only':
  power_report='reports/electrical/boost_spice_partial.json'
 inputs={p:sha(ROOT/p) for p in ['firmware/src/power.c','firmware/include/power.h',
         'scripts/check_power_replay.py','reports/electrical/electrical_checks.json',
         power_report,'reports/electrical/order_readiness.json']}
 if args.verify_report:
  r=json.loads(REPORT.read_text());assert r['input_hashes']==inputs
  assert r['result']=='PASS firmware waveform replay only' and len(r['cases'])==16
  assert all(c['pass'] and all(c['checks'].values()) for c in r['cases'])
  print('PASS firmware waveform replay integrity');return
 WORK.mkdir(parents=True,exist_ok=True);(WORK/'runner.c').write_text(RUNNER)
 REPORT.write_text(json.dumps(dict(result='INCOMPLETE',input_hashes=inputs),indent=2)+'\n')
 env=os.environ.copy();lib=Path(env.get('CANDI_TOOLS_ROOT',Path.home()/'.local/share/candi-tools'))/'native-gcc/usr/lib/x86_64-linux-gnu'
 env['LD_LIBRARY_PATH']=str(lib)+':'+env.get('LD_LIBRARY_PATH','')
 subprocess.run(['host-gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                 '-fsanitize=address,undefined','-I'+str(ROOT/'firmware/include'),
                 str(WORK/'runner.c'),str(ROOT/'firmware/src/power.c'),'-o',str(WORK/'runner')],check=True,env=env)
 cases=[];t=np.arange(601)
 source=json.loads((ROOT/power_report).read_text())
 by_name={r['case']['name']:r for r in source['cases']}
 drop=json.loads((ROOT/'reports/electrical/order_readiness.json').read_text())['power_distribution']['sensor_branch_drop_V_at_300mA']
 for name in ['efuse_large_capacitance','efuse_min_limit_cap_tolerance','efuse_hot_short_and_reset','five_volt_start_short_and_reset']:
  raw=args.traces/(name+'.raw');assert sha(raw)==by_name[name]['raw_trace_sha256']
  d=read_raw(raw);five=name.startswith('five');fault_case='short' in name
  clock=t/1000 if five else np.maximum(0,t-58)/1000
  if name=='efuse_hot_short_and_reset':
   # Hold the pre-short regulated sample to let the firmware leave startup grace.
   clock=np.where(t<=98,np.maximum(0,t-58)/1000,np.where(t<=350,.040,.040+(t-350)/1000))
  rail='5v' if five else '12v';bit=2 if five else 1
  voltage=np.interp(clock,d['time'],d[f'v(sensor_{rail})'])
  fault=np.interp(clock,d['time'],d[f'v(fault_{rail}_n)'])<.8
  voltage[t<(10 if five else 60)]=0
  branch_drop=max(drop['SENSOR_'+rail.upper()].values())
  for gain in [-.025,.025]:
   for offset in [-.09,.09]:
    measured=np.clip(np.rint((np.maximum(0,voltage-branch_drop)*(1+gain)+offset)*1000),0,65535).astype(int)
    mv12=np.where(t>=60,12000,0);mv5=np.where(t>=10,5000,0)
    if five:mv5=measured
    else:mv12=measured
    text=''.join(f'{ms},{a},{b},{bit if f else 0}\n' for ms,a,b,f in zip(t,mv12,mv5,fault))
    run=subprocess.run([str(WORK/'runner')],input=text,text=True,capture_output=True,check=True,env=env)
    state=np.array([[int(v) for v in row.split(',')] for row in run.stdout.splitlines()])
    assert len(state)==len(t)
    trips=t[(state[:,3]&bit)!=0]
    checks={'other_rail_stays_enabled':bool(np.all((state[t>=60,1]&(3^bit))!=0))}
    if fault_case:
     checks['fault_latches']=bool(len(trips))
     checks['shutdown_deadline']=bool(len(trips) and (25<=trips[0]<=40 if five else 355<=trips[0]<=375))
     checks['no_automatic_restart']=bool(len(trips) and np.all((state[t>=trips[0],1]&bit)==0))
    else:
     checks['no_false_startup_trip']=not len(trips)
     checks['healthy_before_300ms']=bool(state[299,2]&bit)
     checks['remains_enabled']=bool(np.all((state[t>=60,1]&bit)!=0))
    cases.append(dict(name=name,gain_error=gain,offset_error_V=offset,PCB_drop_V=branch_drop,
                      raw_sha256=sha(raw),first_trip_ms=int(trips[0]) if len(trips) else None,
                      checks=checks,pass_=all(checks.values())))
 for c in cases:c['pass']=c.pop('pass_')
 report=dict(result='PASS firmware waveform replay only' if all(c['pass'] for c in cases) else 'FAIL',
             input_hashes=inputs,cases=cases,sample_interval_ms=1,
             scope='Actual power.c compiled with ASan/UBSan; four completed SPICE traces each replayed at four ADC-error corners, with worst current-layout branch drop at 300 mA. Twelve-volt enable aligned to firmware 60 ms. Running short delayed by holding the pre-short regulated sample. Last trace sample held after trace end. Other rail idealized.',
             limitations='One-way replay: disable commands do not change the recorded circuit. No MCU execution timing, ADC RC dynamics, CAN scheduling, ground-return/contact resistance or closed-loop hardware/firmware correlation. 470 uF remains a diagnostic beyond the supported 100 uF load. No physical qualification.')
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 print(report['result']);print([(c['name'],c['first_trip_ms'],c['pass']) for c in cases])
 if not all(c['pass'] for c in cases):raise SystemExit(1)

if __name__=='__main__':main()
