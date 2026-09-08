"""Review actual Y1 copper against Abracon's recommended land pattern."""
from pathlib import Path
import hashlib
import json
import sexpdata as s
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

root=Path(__file__).resolve().parents[1]
pcb=root/'hardware/FRC_Sensor_CAN.kicad_pcb'
key=lambda x:str(x[0]) if isinstance(x,list) and x else ''
child=lambda x,k:next(v for v in x if key(v)==k)
board=s.loads(pcb.read_text())
f=next(f for f in board if key(f)=='footprint' and any(key(v)=='property' and v[1:3]==['Reference','Y1'] for v in f))
pads=[v for v in f if key(v)=='pad']
fig,ax=plt.subplots(figsize=(8,5.6))
ax.set_aspect('equal');ax.set_xlim(-3.65,3.65);ax.set_ylim(2.55,-2.55)
for pad in pads:
    x,y=child(pad,'at')[1:3];w,h=child(pad,'size')[1:3]
    assert abs(abs(x)-2)<1e-6 and abs(abs(y)-1.2)<1e-6
    assert abs(w-1.8)<1e-6 and abs(h-1.2)<1e-6
    ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#cf922d',edgecolor='#75450d',lw=1.4))
    n=pad[1];label='GND' if n in ('2','4') else 'crystal'
    ax.text(x,y,f'{n}\n{label}',ha='center',va='center',fontsize=12,fontweight='bold')
ax.add_patch(Rectangle((-2.5,-1.6),5,3.2,facecolor='none',edgecolor='#243f50',ls='--',lw=1.6))
ax.add_patch(Rectangle((-3.15,-2.05),6.3,4.1,facecolor='none',edgecolor='#697780',ls=':',lw=1))
ax.text(0,0,'Nominal 5.0 × 3.2 mm body\norientation shown in footprint coordinates',ha='center',va='center',fontsize=10)
ax.set_xlabel('Footprint X (mm)');ax.set_ylabel('Footprint Y (mm)')
ax.set_title('Y1 · Abracon ABM3B recommended lands',fontweight='bold',pad=12)
fig.text(.5,.045,'Copper: 1.8 × 1.2 mm pads · center spacing 4.0 × 2.4 mm\n'
         'Dashed: nominal body · dotted: courtyard · PCB placement rotates this footprint 180°',
         ha='center',fontsize=9)
fig.subplots_adjust(bottom=.2,top=.9,left=.11,right=.97)
out=root/'output/assembly';out.mkdir(exist_ok=True)
fig.savefig(out/'crystal_land_review.png',dpi=180)
fig.savefig(out/'crystal_land_review.pdf')
plt.close(fig)
report={'result':'PASS','scope':'Actual native Y1 pad sizes/centers compared with Abracon ABM3B recommended lands, datasheet page 3; nominal drawing, not measured assembly yield.',
        'source_url':'https://abracon.com/Resonators/abm3b.pdf',
        'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
        'footprint':f[1],'pad_size_mm':[1.8,1.2],'center_spacing_mm':[4.0,2.4],
        'nominal_body_mm':[5.0,3.2],'nominal_copper_extension_beyond_body_mm':{'x':.4,'y':.2}}
(root/'reports/manufacturing/crystal_land_review.json').write_text(json.dumps(report,indent=2)+'\n')
print('Y1 recommended lands match; generated nominal assembly review drawing.')
