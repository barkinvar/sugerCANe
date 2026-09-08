#!/usr/bin/env python3
"""Passive hot-plug sensitivity sweep; NOT a MOSFET switching/SOA or surge certification."""
from pathlib import Path
import itertools,json,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];SPICE=ROOT/'calculations/spice';OUT=ROOT/'reports/spice'
SPICE.mkdir(parents=True,exist_ok=True)
OUT.mkdir(parents=True,exist_ok=True)
rows=[];worst_data={}
for vin,rsource,lwire,esr in itertools.product((6,12,18),(.02,.1,1),(.1e-6,1e-6,10e-6),(.02,.36)):
 name=f'inrush_{vin}V_{rsource}R_{lwire*1e6:g}uH_{esr}ESR'
 # A pre-enhanced channel provides a conservative fast charging path. It omits
 # gate dynamics, body-diode recovery, active load, and electrothermal effects.
 net=f'''* {name}; fully-on PMOS resistive-path approximation
Vstep source 0 PWL(0 0 10u 0 10.1u {vin} 5m {vin})
Rsource source wire {rsource}
Lwire wire fused_in {lwire}
Rfuse fused_in fused .063
Rmos fused mos_out .020
Rtrace mos_out protected .020
Rbulk protected bulk {esr}
Cbulk bulk 0 56.4u
Rceramic protected ceramic .005
Cceramic ceramic 0 11u
Vsense protected tvsnode 0
BTVS tvsnode 0 I=max(v(protected)-21.05,0)/.39756+min(v(protected)+.8,0)/.01
Rbleed protected 0 1Meg
.control
set wr_singlescale
set wr_vecnames
tran .1u 1.5m
wrdata ../../reports/spice/inrush_work.txt v(protected) i(Vstep) i(Vsense)
quit
.endc
.end
'''
 (SPICE/'inrush_work.cir').write_text(net)
 run=subprocess.run(['ngspice','-b','inrush_work.cir'],cwd=SPICE,text=True,capture_output=True)
 log=run.stdout+run.stderr
 assert run.returncode==0 and 'Error' not in log and 'Warning' not in log,log
 d=np.loadtxt(OUT/'inrush_work.txt',skiprows=1);t=d[:,0];v=d[:,1];i=-d[:,2];tvs=d[:,3]
 row={'vin_V':vin,'source_R_ohm':rsource,'wire_L_uH':lwire*1e6,'bulk_ESR_ohm':esr,'peak_input_A':float(i.max()),'peak_protected_V':float(v.max()),'input_I2t_A2s':float(np.trapezoid(i*i,t)),'TVS_energy_J':float(np.trapezoid(v*tvs,t))}
 rows.append(row)
 for metric in ('input_I2t_A2s','peak_protected_V','peak_input_A'):
  if metric not in worst_data or row[metric]>worst_data[metric][0][metric]:worst_data[metric]=(row,d,net)
report={'scope':'Passive network simulation with PMOS represented by20mohm already on; representative piecewise-linear TVS. Does not verify gate dynamics, reverse-recovery, SOA, actual component tolerances or standardized transient immunity.',
 'sweep_cases':len(rows),'capacitance_upper_values_uF':[56.4,11],
 'fuse_nominal_melting_I2t_A2s':.853,'pulse_design_screen_fraction_of_nominal':.25,
 'pulse_screen_is_not_guarantee':'25% is an engineering screening allowance, not a manufacturer-qualified repetitive-pulse limit.',
 'worst':{k:v[0] for k,v in worst_data.items()},'cases':rows}
assert max(r['input_I2t_A2s'] for r in rows)<.25*.853
assert max(r['peak_protected_V'] for r in rows)<30
fig,axes=plt.subplots(3,1,figsize=(10,9),constrained_layout=True)
for ax,(metric,(row,d,net)) in zip(axes,worst_data.items()):
 (SPICE/(metric+'.cir')).write_text(net.replace('inrush_work.txt',metric+'.txt'))
 np.savetxt(OUT/(metric+'.txt'),d,header='time_s protected_V source_current_A TVS_current_A')
 ax.plot(d[:,0]*1e6,d[:,1],label='Protected voltage (V)')
 ax.plot(d[:,0]*1e6,-d[:,2],label='Input current (A)')
 ax.set(xlim=(0,250),xlabel='Time (µs)',title=f'{metric}: Vin={row["vin_V"]} V, source={row["source_R_ohm"]} Ω, wire={row["wire_L_uH"]:g} µH, ESR={row["bulk_ESR_ohm"]} Ω')
 ax.grid(alpha=.25);ax.legend()
fig.suptitle('Input hot-plug sensitivity — passive approximation, not hardware qualification')
fig.savefig(OUT/'inrush.png',dpi=180);fig.savefig(OUT/'inrush.pdf');plt.close(fig)
(OUT/'inrush_results.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'inrush_work.txt').unlink();(SPICE/'inrush_work.cir').unlink()
print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
