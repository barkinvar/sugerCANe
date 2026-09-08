"""Color actual exported copper around the buck regulator for layout review."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch,Patch,Circle
from shapely.geometry.polygon import orient
import verify_gerber_connectivity as g

ROOT=Path(__file__).resolve().parents[1]
components={c['reference']:c for c in json.loads((ROOT/'reports/manufacturing/board_manifest.json').read_text())['components']}
colors={'GND':'#d7dedf','VIN_PROT':'#db7c26','BUCK_SW':'#b3263d','BUCK_CB':'#7b48a1','BUCK_FB':'#156e97','V5_INTERNAL':'#16875a'}
fig,axes=plt.subplots(1,2,figsize=(12,6),layout='constrained')
areas={}
for ax,side in zip(axes,['top','bottom']):
    for i,poly in enumerate(g.islands[side]):
        net=next(iter(g.root_nets[g.root(g.offset[side]+i)]))
        color=colors.get(net,'#eceeef')
        if net in ('BUCK_SW','BUCK_CB','BUCK_FB'):
            areas.setdefault(net,{})[side]=areas.setdefault(net,{}).get(side,0)+poly.area
        poly=orient(poly,sign=1);points=[];codes=[]
        for ring in [poly.exterior,*poly.interiors]:
            co=list(ring.coords);points.extend(co);codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(co)-2)+[PlotPath.CLOSEPOLY])
        ax.add_patch(PathPatch(PlotPath(points,codes),facecolor=color,edgecolor='none'))
    for drill in g.drills:
        ax.add_patch(Circle((drill.x,drill.y),drill.aperture.diameter/2,facecolor='white',edgecolor='#52646b',linewidth=.2))
    for ref in ('U1','L1','C1','C2','C3','C4','C5','C6','C13','R1','R2'):
        c=components[ref]
        if side=='top':
            offsets={'C3':(0,3.1),'U1':(0,2),'L1':(0,2),'C6':(0,-2),'R2':(0,-2)}
            dx,dy=offsets.get(ref,(0,2))
            ax.text(c['x_mm']+dx,c['y_mm']+dy,ref,fontsize=8,fontweight='bold',ha='center',va='center',
                    bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})
            if ref=='U1':
                for p in c['pads']:
                    ax.text(p['x_mm'],p['y_mm'],p['number'],fontsize=5.5,ha='center',va='center',color='white',fontweight='bold')
    ax.set(xlim=(8,40),ylim=(-35,-10),xlabel='PCB X (mm)',ylabel='Gerber Y (mm)',title=side.upper()+' copper · both panels viewed from TOP')
    ax.set_aspect('equal');ax.tick_params(labelsize=8)
fig.suptitle('Buck regulator layout review · actual Gerber copper',fontsize=16,fontweight='bold')
fig.legend(handles=[Patch(color=c,label=n) for n,c in colors.items()],loc='lower center',ncol=6,bbox_to_anchor=(.5,.005),fontsize=9)
fig.get_layout_engine().set(rect=(0,.08,1,.95))
for ext in ('png','pdf'):fig.savefig(ROOT/f'output/assembly/power_layout_review.{ext}',dpi=200)
plt.close(fig)
pads={p['number']:p for p in components['U1']['pads']}
c3={p['number']:p for p in components['C3']['pads']}
assert pads['3']['y_mm']==c3['1']['y_mm'] and pads['1']['y_mm']==c3['2']['y_mm']
width=c3['1']['x_mm']-pads['3']['x_mm'];height=abs(pads['1']['y_mm']-pads['3']['y_mm'])
r={'method':'Independent exported-copper reconstruction, colored by connected pad net; top-view coordinates for both layers.',
   'geometric_observations':{'C3_to_U1_pin_center_spacing_mm':width,'C3_U1_rectangular_centerline_loop_area_mm2':width*height,'selected_copper_area_mm2':areas},
   'limits':'Projected pin-center geometry is not package/plane loop inductance, a thermal model or an EMI prediction. The bottom panel is not mirrored: it is an x-ray view from the top.',
   'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'output/fabrication/FRC_Sensor_CAN-F_Cu.gtl',ROOT/'output/fabrication/FRC_Sensor_CAN-B_Cu.gbl')}}
(ROOT/'reports/manufacturing/power_layout_review.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
