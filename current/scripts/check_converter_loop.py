"""Sensitivity screen for the cascaded boost, not a validated TPS61085 SPICE model.

Current-mode averaged boost plant, Type-II compensator and full-cycle delay.
The datasheet does NOT guarantee modulator gain. An explicit 3..10 A/V gain
allowance brackets a nominal 6.9 A/V inferred from its compensation rule.
Measured loop gain and transient testing remain release-to-production gates.
"""
from pathlib import Path
import itertools,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];out=R/'reports/electrical';out.mkdir(parents=True,exist_ok=True)
m=json.loads((R/'hardware/design/circuit.json').read_text())['parts']
assert m['U8']['mpn']=='TPS61085DGKR'
assert m['R63']['value']=='13k' and m['C69']['value']=='33nF'
e=json.loads((out/'electrical_checks.json').read_text())
f=np.logspace(1,6.5,5000);s=2j*np.pi*f;rows=[];worst=None
for vin,load,C,L,gm,gcs,fsw,rt,ct in itertools.product((e['power']['boost_min_input_V'],5.3),(.1,.31),(e['regulated12']['output_cap_bank']['budgeted_each_uF']*3e-6,25e-6),(2.64e-6,3.96e-6),(107e-6*.8,107e-6*1.2),(3.,10.),(.9e6,1.5e6),(.9825,1.0175),(.7,1.3)):
 V=12.003;d=1-vin/V;rl=V/load;rc=13000*rt;cc=33e-9*ct
 wp=2/(rl*C);wrhp=rl*(1-d)**2/L
 gps=rl*(1-d)*gcs/2*(1-s/wrhp)/(1+s/wp)
 gc=gm*(rc+1/(s*cc))*1.238/V
 loop=gps*gc*np.exp(-s/fsw)
 mag=20*np.log10(abs(loop));phase=np.unwrap(np.angle(loop))*180/np.pi
 crossings=np.where((mag[:-1]>=0)&(mag[1:]<0))[0];assert len(crossings)==1
 k=crossings[0];fc=float(f[k]);pm=float(180+phase[k]);rh=wrhp/(2*np.pi)
 phasecross=np.where((phase[:-1]>-180)&(phase[1:]<=-180))[0]
 gm_db=float(-mag[phasecross[0]]) if len(phasecross) else 99.
 row=dict(vin_V=vin,load_A=load,Cout_uF=C*1e6,L_uH=L*1e6,gm_uS=gm*1e6,assumed_modulator_A_per_V=gcs,fsw_Hz=fsw,Rcomp_ohm=rc,Ccomp_nF=cc*1e9,crossover_Hz=fc,phase_margin_deg=pm,gain_margin_dB=gm_db,RHP_zero_Hz=rh)
 assert fc<min(fsw/10,rh/5),row
 assert pm>45 and gm_db>10,row
 rows.append(row)
 if worst is None or pm<worst[0]:worst=(pm,row,mag,phase)
fig,(ax,bx)=plt.subplots(2,1,figsize=(9,6),sharex=True)
ax.semilogx(f,worst[2]);ax.axhline(0,color='black',lw=.7);ax.set_ylabel('Loop gain (dB)');ax.grid(True,which='both',alpha=.2)
bx.semilogx(f,worst[3]);bx.axhline(-180,color='black',lw=.7);bx.set_ylabel('Phase (degrees)');bx.set_xlabel('Frequency (Hz)');bx.set_ylim(-270,0);bx.grid(True,which='both',alpha=.2)
ax.set_xlim(10,3e5);ax.set_title('Rev F averaged boost sensitivity screen\nAssumed modulator gain; not measured or vendor-model validation')
fig.tight_layout();fig.savefig(out/'converter_loop.png',dpi=180);plt.close(fig)
report=dict(result='PASS analytical screening only',source='https://www.ti.com/lit/ds/symlink/tps61085.pdf',model='Averaged CCM current-mode plant, ideal Type-II amplifier, full-cycle delay. gm +/-20%, modulator 3..10 A/V and compensator capacitor +/-30% are engineering sensitivity ranges, not guaranteed silicon bounds.',corners=len(rows),minimum_phase_margin_deg=min(q['phase_margin_deg'] for q in rows),minimum_gain_margin_dB=min(q['gain_margin_dB'] for q in rows),crossover_range_Hz=[min(q['crossover_Hz'] for q in rows),max(q['crossover_Hz'] for q in rows)],worst_phase_corner=worst[1],scope='Does not prove stability of actual TPS61085, DCM, cascaded buck interaction, startup or current limiting. Bench Bode/load-step tests and thermal/short tests are mandatory before production.')
(out/'converter_loop.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
