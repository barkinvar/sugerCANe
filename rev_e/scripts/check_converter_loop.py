"""Analytical boost-mode loop screening, not a switching or measured loop model.

TI TPS552872-Q1 equations 19-26, ideal type-II error amplifier, plus a
conservative full-cycle transport delay. PFM and buck/boost transitions need
hardware testing; no simulated result here certifies those operating modes.
"""
from pathlib import Path
import itertools,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];out=R/'reports/electrical';out.mkdir(parents=True,exist_ok=True)
m=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
assert m['R63']['value']=='10k' and m['C69']['value']=='33nF'
e=json.loads((out/'electrical_checks.json').read_text())
f=np.logspace(1,6.5,7000);s=2j*np.pi*f
rows=[];worst=None
for vin,load,C,L,gm,fsw in itertools.product((5.2,6,9,11.8),(.1,.31,.53),(e['regulated12']['output_cap_bank']['budgeted_each_uF']*3e-6,33e-6),(2.64e-6,3.96e-6),(190e-6*.8,190e-6*1.2),(781250*.9,781250*1.1)):
 V=12.01081;d=1-vin/V;rl=V/load;esr=.02;rc=1e4;cc=33e-9
 wp=2/(rl*C);wesr=1/(esr*C);wrhp=rl*(1-d)**2/L
 gps=rl*(1-d)/(.11)*(1+s/wesr)*(1-s/wrhp)/(1+s/wp)
 gc=gm*(rc+1/(s*cc))*1.2/V
 loop=gps*gc*np.exp(-s/fsw)
 mag=20*np.log10(abs(loop));phase=np.unwrap(np.angle(loop))*180/np.pi
 crossings=np.where((mag[:-1]>=0)&(mag[1:]<0))[0];assert len(crossings)
 k=crossings[0];fc=float(f[k]);pm=float(180+phase[k]);rh=wrhp/(2*np.pi)
 phasecross=np.where((phase[:-1]>-180)&(phase[1:]<=-180))[0]
 gm_db=float(-mag[phasecross[0]]) if len(phasecross) else float('inf')
 row=dict(vin_V=vin,load_A=load,Cout_uF=C*1e6,L_uH=L*1e6,gm_uS=gm*1e6,fsw_Hz=fsw,crossover_Hz=fc,phase_margin_deg=pm,gain_margin_dB=gm_db,RHP_zero_Hz=rh)
 assert fc<min(fsw/10,rh/5),row
 assert pm>45 and gm_db>10,row
 rows.append(row)
 if worst is None or pm<worst[0]:worst=(pm,row,mag,phase)
fig,(ax,bx)=plt.subplots(2,1,figsize=(9,6),sharex=True)
ax.semilogx(f,worst[2]);ax.axhline(0,color='black',lw=.7);ax.set_ylabel('Loop gain (dB)');ax.grid(True,which='both',alpha=.2)
bx.semilogx(f,worst[3]);bx.axhline(-180,color='black',lw=.7);bx.set_ylabel('Phase (degrees)');bx.set_xlabel('Frequency (Hz)');bx.set_ylim(-270,0);bx.grid(True,which='both',alpha=.2)
ax.set_xlim(10,3e5);ax.set_title('Rev E analytical CCM boost model — lowest phase-margin corner\nIncludes assumed full-cycle delay; not measured or PFM-qualified')
fig.tight_layout();fig.savefig(out/'converter_loop.png',dpi=180);plt.close(fig)
report=dict(result='PASS analytical screening only',source='https://www.ti.com/lit/ds/symlink/tps552872-q1.pdf',model='Equations 19-26; ideal type-II amplifier and assumed full switching-cycle delay; gm +/-20% engineering allowance, not guaranteed datasheet bounds.',corners=len(rows),minimum_phase_margin_deg=min(q['phase_margin_deg'] for q in rows),minimum_gain_margin_dB=min(q['gain_margin_dB'] for q in rows),crossover_range_Hz=[min(q['crossover_Hz'] for q in rows),max(q['crossover_Hz'] for q in rows)],worst_phase_corner=worst[1],scope='Boost CCM approximation. PFM, current-limit-loop interactions, soft start, parasitic poles, buck/boost transitions and actual sensor loads remain qualification tests.',rows=rows)
(out/'converter_loop.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='rows'})
