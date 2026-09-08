"""Render actual exported copper and drill geometry for visual review."""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch,Circle
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry.polygon import orient
import verify_gerber_connectivity as g
ROOT=Path(__file__).resolve().parents[1]
def patch(poly):
    poly=orient(poly,sign=1);vertices=[];codes=[]
    for ring in [poly.exterior,*poly.interiors]:
        coords=list(ring.coords);vertices.extend(coords)
        codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(coords)-2)+[PlotPath.CLOSEPOLY])
    return PathPatch(PlotPath(vertices,codes),facecolor='#995c22',edgecolor='none')
with PdfPages(ROOT/'output/assembly/gerber_copper_review.pdf') as pdf:
    for side in ['top','bottom']:
        fig,ax=plt.subplots(figsize=(8,8.7));fig.patch.set_facecolor('white')
        ax.set_facecolor('#f6f3e8');ax.set_aspect('equal')
        for poly in g.islands[side]:ax.add_patch(patch(poly))
        for d in g.drills+list(g.stack.drill_npth.instance.objects):
            ax.add_patch(Circle((d.x,d.y),d.aperture.diameter/2,facecolor='white',edgecolor='#594b3d',linewidth=.12))
        ax.set(xlim=(0,96) if side=='top' else (96,0),ylim=(-96,0),xlabel='Board X (mm)',ylabel='Gerber Y (mm)')
        ax.tick_params(labelsize=8)
        fig.suptitle('FRC Sensor CAN · Rev A · '+side.upper()+' copper',fontsize=15,fontweight='bold',y=.98)
        ax.set_title('Viewed from '+side+'; exported copper and drills, without solder mask',fontsize=9,pad=10)
        fig.text(.06,.025,'Nominal manufacturing geometry only. Compare to native KiCad, assembly and fabrication files.',fontsize=8)
        fig.tight_layout(rect=(0,.045,1,.955))
        for ext in ['png','svg']:fig.savefig(ROOT/f'output/review/gerber_{side}_copper.{ext}',dpi=200)
        pdf.savefig(fig);plt.close(fig)
report={'method':'Independent Gerbonara/Shapely geometry with actual drill overlays; bottom mirrored for underside view',
        'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'output/fabrication').iterdir()) if p.suffix in ('.gtl','.gbl','.drl')}}
(ROOT/'reports/manufacturing/preview_source.json').write_text(json.dumps(report,indent=2)+'\n')
print('Copper/drill review PNG, SVG and PDF refreshed from final Gerbers.')
