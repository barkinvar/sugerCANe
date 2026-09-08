from pathlib import Path
import re,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];p=R/'simulation/boost_corner.raw'
with p.open('rb') as f:
 header=b''
 while not header.endswith(b'Binary:\n'):header+=f.readline()
 offset=f.tell()
count=int(re.search(rb'No. Points:\s+(\d+)',header)[1]);nvar=int(re.search(rb'No. Variables:\s+(\d+)',header)[1]);assert nvar==4
a=np.memmap(p,dtype='<f8',mode='r',offset=offset,shape=(count,nvar));assert 0<=a[-1,0]<=.00401
ts=np.linspace(0,.004,4001);idx=np.searchsorted(a[:,0],ts).clip(0,count-1);small=np.array(a[idx])
np.savetxt(R/'simulation/boost_corner_sampled.csv',small,delimiter=',',header='time_s,boost_input_V,output_V,inductor_A',comments='')
fig,ax=plt.subplots(3,1,figsize=(9,9),layout='constrained')
ax[0].plot(small[:,0]*1e3,small[:,1],label='Boost input after source resistance');ax[0].plot(small[:,0]*1e3,small[:,2],label='5 V output');ax[0].set(ylabel='Voltage (V)',xlabel='Time (ms)',title='TI TPS613222A model: lower input, approximately 462 mA load');ax[0].legend()
lo=np.searchsorted(a[:,0],.00395);hi=np.searchsorted(a[:,0],.004);segment=np.array(a[lo:hi:20]);time=(segment[:,0]-.00395)*1e6
ax[1].plot(time,segment[:,2]);ax[1].set(ylabel='Output (V)',xlabel='Time within final 50 µs (µs)')
ax[2].plot(time,segment[:,3]);ax[2].set(ylabel='Inductor current (A)',xlabel='Time within final 50 µs (µs)')
for q in ax:q.grid(alpha=.25)
fig.savefig(R/'output/boost_simulation.png',dpi=180);fig.savefig(R/'output/boost_simulation.pdf')
results={}
for name,filename in [('nominal','boost_spice_run.log'),('lower_input_heavier_load','boost_corner.log')]:
 text=(R/'reports'/filename).read_text();results[name]={k:float(re.search(r'(?m)^'+k+r'\s*=\s*([\deE.+-]+)',text)[1]) for k in ['vavg','vmin','vmax','ilmax']}
results['scope']='Typical vendor boost model only; upstream buck represented by finite-resistance source. No temperature, physical PCB parasitics or full cascaded-loop qualification.'
(R/'reports/boost_simulation.json').write_text(json.dumps(results,indent=2)+'\n')
print(results)
