from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parents[1];out=R/'output/documentation';out.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Drawing','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
c=canvas.Canvas(str(out/'Mechanical_RevB2_1to1.pdf'),pagesize=A4);c.setTitle('Rev B-2 1:1 mounting template');c.setFont('Drawing',18);c.drawString(22*mm,274*mm,'Sensor CAN — Rev B-2 mounting template');c.setFont('Drawing',10);c.drawString(22*mm,265*mm,'60 × 68 mm PCB  |  4 × Ø3.2 mm nonplated mounting holes')
x0,y0=65*mm,145*mm;c.setLineWidth(.3*mm);c.rect(x0,y0,60*mm,68*mm)
for x,y in [(3.5,3.5),(56.5,3.5),(3.5,64.5),(56.5,64.5)]:
 px,py=x0+x*mm,y0+(68-y)*mm;c.circle(px,py,1.6*mm);c.setLineWidth(.1*mm);c.line(px-2.5*mm,py,px+2.5*mm,py);c.line(px,py-2.5*mm,px,py+2.5*mm);c.setLineWidth(.3*mm)
c.setFont('Drawing',10);c.drawCentredString(x0+30*mm,y0+72*mm,'60.00 mm');c.drawCentredString(x0+30*mm,y0-7*mm,'Mount centers: 53.00 × 61.00 mm');c.drawCentredString(x0+30*mm,y0+35*mm,'TOP VIEW');c.drawCentredString(x0+30*mm,y0+29*mm,'68.00 mm high')
c.setFont('Drawing',10)
for i,s in enumerate(['Centers from top-left: (3.5,3.5), (56.5,3.5), (3.5,64.5), (56.5,64.5) mm.', 'Nominal PCB thickness: 1.6 mm. Terminal bodies rise 8.5 mm.', 'Reserve 60 x 76.1 mm for connectors/actuators, plus cable/service space.', 'Print at 100% / actual size. Verify the 50 mm bar below before drilling.']):c.drawString(22*mm,(122-i*7)*mm,s)
c.setLineWidth(.3*mm);c.line(65*mm,70*mm,115*mm,70*mm);c.line(65*mm,68*mm,65*mm,72*mm);c.line(115*mm,68*mm,115*mm,72*mm);c.drawCentredString(90*mm,64*mm,'50.00 mm scale check')
c.setFont('Drawing',8);c.drawString(22*mm,25*mm,'Nominal design geometry. Physical prototype, cable alignment and enclosure fit remain unverified.');c.save()
fig,ax=plt.subplots(figsize=(9,5.2));ax.add_patch(Rectangle((0,0),96,96,fc='#e8ecf0',ec='#71808d',lw=2));ax.add_patch(Rectangle((113,0),60,68,fc='#2f7184',ec='#163e4a',lw=2));ax.text(48,48,'Rev A\n96 × 96 mm',ha='center',va='center',fontsize=14,color='#374955');ax.text(143,34,'Rev B-2\n60 × 68 mm\n3 sensors',ha='center',va='center',fontsize=14,color='white');ax.set(xlim=(-7,182),ylim=(-7,105),aspect='equal');ax.axis('off');fig.suptitle('55.7% less PCB area',fontsize=20,color='#163e4a');fig.tight_layout();fig.savefig(R/'output/review/size_comparison.png',dpi=180,facecolor='white');plt.close(fig)
