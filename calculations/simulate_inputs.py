#!/usr/bin/env python3
"""TI typical comparator SPICE + actual firmware debounce, at 100 sampling phases."""
from pathlib import Path
import ctypes as ct
import json, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];SPICE=ROOT/'calculations/spice';OUT=ROOT/'reports/spice'
OUT.mkdir(parents=True,exist_ok=True)
SPICE.mkdir(parents=True,exist_ok=True)
# Keep the vendor source intact. ngspice needs a named diode-area parameter.
original=(ROOT/'sources/models/lm2901_ti/lm2901.lib').read_text()
(SPICE/'lm2901_ngspice.lib').write_text('* ngspice42 syntax adaptation: positional diode area -> area=; no value changes.\n'+original.replace('D_DESD AN CAT model22 {area}','D_DESD AN CAT model22 area={area}'))
subprocess.run(['host-gcc','-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'firmware/include'),str(ROOT/'firmware/src/sensor_core.c'),'-o',str(OUT/'libsensor_core.so')],check=True)
class Inputs(ct.Structure):
 _fields_=[('changed_at',ct.c_uint32*4),('rising',ct.c_uint32*4),('raw',ct.c_uint8),('candidate',ct.c_uint8),('stable',ct.c_uint8),('invert',ct.c_uint8),('debounce_ms',ct.c_uint16),('initialized',ct.c_bool)]
lib=ct.CDLL(str(OUT/'libsensor_core.so'))
lib.sc_inputs_init.argtypes=[ct.POINTER(Inputs),ct.c_uint8,ct.c_uint8,ct.c_uint16,ct.c_uint32]
lib.sc_inputs_update.argtypes=[ct.POINTER(Inputs),ct.c_uint8,ct.c_uint32]
assert ct.sizeof(Inputs)==40
cases=[('logic_3v3','push',True,3.3,12,0),('logic_5v','push',True,5,12,0),('industrial_12v','push',False,12,12,0),('industrial_30v_at_6v_battery','push',False,30,6,0),('npn_10v_500uA_leak','npn',False,10,12,.0005),('pnp_12v_500uA_leak','pnp',False,12,12,.0005),('open_drain_3v3_50uA_leak','npn',True,3.3,12,.00005)]
results={};fig,axes=plt.subplots(4,2,figsize=(12,11),constrained_layout=True)
for ax,(name,kind,logic,level,vbat,leak) in zip(axes.flat,cases):
 stimulus='PWL(0 0 1m 0 1.001m 1 1.05m 1 1.051m 0 3m 0 3.001m 1 8m 1 8.001m 0 12m 0)'
 source=f'Vstim stim 0 {stimulus}\n'
 if kind=='push':source+=f'Bsignal signal 0 V={level}*v(stim)\n'
 elif kind=='npn':source+=f'Vport port 0 {level}\nVdiode port pull .45\nRpull pull signal 4.7k\nBleak signal 0 I={leak}\nBcontrol control 0 V=1-v(stim)\nSnpn signal 0 control 0 sensor_switch\n'
 elif kind=='pnp':source+=f'Vport port 0 {level}\nIleak port signal {leak}\nSpnp port signal stim 0 sensor_switch\nRpull signal 0 4.7k\n'
 net=f'''* {name}: actual Rev A divider, hysteresis and filter; typical TI model
.include lm2901_ngspice.lib
.model sensor_switch SW(Ron=10 Roff=1e12 Vt=.5 Vh=0)
Vbat vbat 0 {vbat}
Vlogic vlogic 0 3.3
{source}R101 signal mid 110k
R102 mid sense 110k
R103 sense 0 20k
R104 sense output 910k
R105 output vlogic 10k
C101 sense 0 1n
R106 vlogic reference 100k
R107 reference 0 17.8k
{'R108 reference 0 7.15k' if logic else '* Industrial reference: threshold shunt open'}
Xcomp sense reference vbat 0 output LM2901
.control
set wr_singlescale
set wr_vecnames
tran .5u 12m
wrdata ../../reports/spice/{name}.txt v(signal) v(sense) v(reference) v(output)
quit
.endc
.end
'''
 (SPICE/(name+'.cir')).write_text(net)
 run=subprocess.run(['ngspice','-D','ngbehavior=ps','-b',name+'.cir'],cwd=SPICE,text=True,capture_output=True)
 log=run.stdout+run.stderr;(OUT/(name+'.log')).write_text(log)
 assert run.returncode==0 and 'Error' not in log and 'Warning' not in log,log
 data=np.loadtxt(OUT/(name+'.txt'),skiprows=1);t=data[:,0];signal=data[:,1];output=data[:,4]
 assert output[t<.001].max()<.8
 assert output[(t>.004)&(t<.007)].min()>2.4
 latency=[];fall_latency=[];one_trace=None
 for phase in np.linspace(0,.00099,100):
  samples=np.arange(0,.012,.001)+phase;raw=np.interp(samples,t,output)>1.65
  state=Inputs();lib.sc_inputs_init(ct.byref(state),int(raw[0]),0,2,0)
  stable=[]
  for i,bit in enumerate(raw):lib.sc_inputs_update(ct.byref(state),int(bit),i);stable.append(state.stable&1)
  stable=np.array(stable);rises=np.flatnonzero(np.diff(stable.astype(int))==1)+1;falls=np.flatnonzero(np.diff(stable.astype(int))==-1)+1
  assert len(rises)==len(falls)==1 and state.rising[0]==1,(name,phase,stable)
  assert stable[samples<.003].max()==0
  latency.append((samples[rises[0]]-.003001)*1000)
  fall_latency.append((samples[falls[0]]-.008001)*1000)
  if one_trace is None:one_trace=(samples,stable)
 results[name]={'supply_V':vbat,'signal_high_nominal_V':level,'kind':kind,'off_leakage_A':leak,'sampling_phases':100,'glitch_width_us':49,'glitch_accepted':False,'rising_count':1,'valid_rise_latency_ms':[min(latency),max(latency)],'valid_fall_latency_ms':[min(fall_latency),max(fall_latency)],'debounce_ms':2,'sample_period_ms':1,'scope':'Typical comparator SPICE model plus compiled production debounce C. Does not establish guaranteed timing or EMC immunity.'}
 ax.plot(t*1000,signal/level,label='Signal / nominal high',lw=1)
 ax.plot(t*1000,output/3.3,label='Comparator / 3.3 V',lw=1)
 ax.step(one_trace[0]*1000,one_trace[1],where='post',label='Firmware logical state',lw=1.6)
 ax.set(title=name.replace('_',' '),xlabel='Time (ms)',ylabel='Normalized level',ylim=(-.08,1.15));ax.grid(alpha=.25)
axes.flat[-1].axis('off');axes.flat[-1].legend(*axes.flat[0].get_legend_handles_labels(),loc='center')
fig.suptitle('Input filtering and 2 ms firmware debounce — simulated, not bench measured')
fig.savefig(OUT/'input_filtering.png',dpi=180);fig.savefig(OUT/'input_filtering.pdf');plt.close(fig)
(OUT/'input_results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
