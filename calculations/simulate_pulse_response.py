"""Characterize pulse capture with TI comparator SPICE and production debounce C.

Run after simulate_inputs.py. Uses its generated, reviewed circuit decks and
shared production-code library. No hardware timing guarantee is established.
"""
from pathlib import Path
import ctypes as ct
import hashlib
import json
import re
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
SPICE=ROOT/'calculations/spice'
OUT=ROOT/'reports/spice'
cases=list(json.loads((OUT/'input_results.json').read_text()))
class Inputs(ct.Structure):
    _fields_=[('changed_at',ct.c_uint32*4),('rising',ct.c_uint32*4),
              ('raw',ct.c_uint8),('candidate',ct.c_uint8),('stable',ct.c_uint8),
              ('invert',ct.c_uint8),('debounce_ms',ct.c_uint16),('initialized',ct.c_bool)]
lib=ct.CDLL(str(OUT/'libsensor_core.so'))
lib.sc_inputs_init.argtypes=[ct.POINTER(Inputs),ct.c_uint8,ct.c_uint8,ct.c_uint16,ct.c_uint32]
lib.sc_inputs_update.argtypes=[ct.POINTER(Inputs),ct.c_uint8,ct.c_uint32]
assert ct.sizeof(Inputs)==40
widths=np.round(np.unique(np.r_[np.arange(.25,15.01,.25),np.arange(1.75,3.26,.05)]),5)
widths=np.unique(widths)
starts=[];cursor=.02
for width in widths:
    starts.append(cursor);cursor+=width/1000+.03
starts=np.array(starts);end=cursor+.02
debounces=[1,2,5,10]
result={'method':'TI LM2901 typical macro-model and actual production sensor_core.c, 1ms sample interval, 100 phase offsets at 10us spacing.',
        'limits':'No temperature/process/cable/noise model, physical timing, guaranteed pulse width or encoder capability. Pulse edges are 1us; SPICE maximum step is 5us. The finite phase grid is not a statistical reliability estimate.',
        'widths_ms':widths.tolist(),'debounce_ms':debounces,'phase_count':100,'cases':{},
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'firmware/src/sensor_core.c',ROOT/'sources/models/lm2901_ti/lm2901.lib']}}
matrices={db:[] for db in debounces};labels=[]
for name in cases:
    base=(SPICE/(name+'.cir')).read_text()
    for negative in (False,True):
        label=name+('_low_pulses' if negative else '_high_pulses')
        print('Pulse sweep:',label,flush=True)
        idle,active=(1,0) if negative else (0,1)
        pwl=[(0,idle)]
        for start,width in zip(starts,widths):
            stop=start+width/1000
            pwl.extend([(start,idle),(start+1e-6,active),(stop,active),(stop+1e-6,idle)])
        pwl.append((end,idle))
        stimulus='Vstim stim 0 PWL('+ ' '.join(f'{t:.8f} {v}' for t,v in pwl)+')'
        deck=re.sub(r'^Vstim.*$',stimulus,base,flags=re.M)
        deck=re.sub(r'^tran .*$',f'tran 5u {end:.8f}',deck,flags=re.M)
        deck=re.sub(r'^wrdata .*$',f'wrdata ../../reports/spice/pulse_work.txt v(output)',deck,flags=re.M)
        path=SPICE/(label+'.cir');path.write_text(deck)
        run=subprocess.run(['ngspice','-D','ngbehavior=ps','-b',path.name],cwd=SPICE,text=True,capture_output=True)
        log=run.stdout+run.stderr;(OUT/(label+'.log')).write_text(log)
        assert run.returncode==0 and 'Error' not in log and 'Warning' not in log,log
        data=np.loadtxt(OUT/'pulse_work.txt',skiprows=1);t,voltage=data[:,0],data[:,1]
        found={db:np.zeros(len(widths),dtype=int) for db in debounces}
        for phase in np.arange(100)*.00001:
            samples=np.arange(0,end-.001,.001)+phase
            raw=(np.interp(samples,t,voltage)>1.65).astype(np.uint8)
            for db in debounces:
                state=Inputs();ptr=ct.byref(state)
                lib.sc_inputs_init(ptr,int(raw[0]),int(negative),db,0)
                count=0;seen=np.zeros(len(widths),dtype=bool)
                for tick,bit in enumerate(raw):
                    lib.sc_inputs_update(ptr,int(bit),tick)
                    if state.rising[0]!=count:
                        count=state.rising[0]
                        index=np.searchsorted(starts,samples[tick],side='right')-1
                        assert 0<=index<len(widths),(label,db,'unexpected initial transition')
                        assert samples[tick] < starts[index]+widths[index]/1000+.015,(label,db,index,'delayed extra transition')
                        assert not seen[index],(label,db,index,'double count')
                        seen[index]=True
                assert count==seen.sum()
                found[db]+=seen
        case={}
        for db in debounces:
            complete=np.flatnonzero(found[db]==100)
            first=float(widths[complete[0]]) if len(complete) else None
            if first is not None:
                assert np.all(found[db][complete[0]:]==100),(label,db,'nonmonotonic capture at larger widths')
            case[str(db)]={'captured_phase_counts':found[db].tolist(),'smallest_tested_width_with_all_100_phases_captured_ms':first}
            matrices[db].append(found[db]/100)
        result['cases'][label]=case;labels.append(label.replace('_',' '))
        (OUT/'pulse_work.txt').unlink()

fig,axes=plt.subplots(2,2,figsize=(14,10),layout='constrained',sharex=True,sharey=True)
edges=np.r_[widths[0]-(widths[1]-widths[0])/2,(widths[:-1]+widths[1:])/2,widths[-1]+(widths[-1]-widths[-2])/2]
for ax,db in zip(axes.flat,debounces):
    im=ax.pcolormesh(edges,np.arange(len(labels)+1)-.5,np.array(matrices[db]),vmin=0,vmax=1,cmap='viridis',shading='flat')
    ax.set(title=f'Debounce {db} ms',xlabel='Input pulse width (ms)',yticks=np.arange(len(labels)),yticklabels=labels)
    ax.tick_params(axis='y',labelsize=6.6);ax.set_ylim(len(labels)-.5,-.5)
fig.colorbar(im,ax=axes,shrink=.7,label='Fraction of the 100 tested sample phases capturing one pulse')
fig.suptitle('Simulated pulse capture · 1 kHz sampling · typical analog model, no hardware qualification',fontsize=13)
fig.savefig(OUT/'pulse_response.png',dpi=180);fig.savefig(OUT/'pulse_response.pdf');plt.close(fig)
(OUT/'pulse_response.json').write_text(json.dumps(result,indent=2)+'\n')
print('Completed pulse response characterization:',len(cases)*2,'waveforms,',len(widths),'widths, 4 debounce settings, 100 phases.')
print('2ms debounce: smallest tested width captured at all phases by waveform:')
for name,case in result['cases'].items():print(name,case['2']['smallest_tested_width_with_all_100_phases_captured_ms'])
