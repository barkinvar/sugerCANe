from pathlib import Path
import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
R=Path(__file__).resolve().parents[1];g=json.loads((R/'hardware/design/placement_geometry.json').read_text())
fig,ax=plt.subplots(figsize=(10,11));ax.add_patch(Rectangle((0,0),60,68,fc='#0e3333',ec='black'))
for c in g:
 x1,y1,x2,y2=c['bbox'];r=c['ref'];color='#2d7070' if r.startswith('J') else '#404044'
 ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,fc=color,ec='#7ca19b',lw=.4));ax.text((x1+x2)/2,(y1+y2)/2,r,ha='center',va='center',color='white',fontsize=6)
 for a in c['pads']:
  x,y=a['xy'];ax.add_patch(Circle((x,y),.32,fc='#d1ad63',ec='none'))
ax.set(xlim=(-2,62),ylim=(70,-2),aspect='equal',title='Rev B placement - 60 x 68 mm');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(R/'output/placement.png',dpi=180)
