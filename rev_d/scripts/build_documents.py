"""Printable BOM, mechanical/service maps and prototype factory packet."""
from pathlib import Path
import csv,json,zipfile,hashlib
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer
from reportlab.lib.units import mm
R=Path(__file__).resolve().parents[1]
for d in ('output/documentation','output/mechanical','order'):(R/d).mkdir(parents=True,exist_ok=True)
styles=getSampleStyleSheet();styles['Normal'].fontSize=8;styles['Normal'].leading=11
P=lambda s:Paragraph(escape(str(s)),styles['Normal'])
rows=list(csv.DictReader((R/'bom/BOM_grouped.csv').open()))
story=[Paragraph('SC12 - Revision D purchasing BOM',styles['Title']),P('104 fitted parts / 48 MPNs / dated qty-one estimate $54.89. Unbuilt prototype. Reprice before ordering; PCB, assembly, attrition, freight and tax excluded.'),Spacer(1,12)]
data=[[P(t) for t in ['Qty','MPN / DigiKey','References','Value / package','USD ext.']]]
for row in rows:data.append([P(row['Quantity']),P(row['MPN']+' / '+row['DigiKey_SKU']),P(row['References']),P(row['Value']+' / '+row['Footprint'].split(':')[-1]),P(row['Extended_USD_qty1'])])
t=Table(data,colWidths=[28,145,175,165,52],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcebf0')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f6f7')]),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t)
SimpleDocTemplate(str(R/'output/documentation/BOM_RevD_SC12.pdf'),pagesize=A4,leftMargin=15,rightMargin=15).build(story)

manifest=json.loads((R/'reports/manufacturing/board_manifest.json').read_text());fps={c['reference']:c for c in manifest['components']}
c=canvas.Canvas(str(R/'output/mechanical/mechanical_drawing.pdf'),pagesize=A4)
def heading(title,sub):
 c.setFont('Helvetica-Bold',17);c.drawString(40,795,title);c.setFont('Helvetica',9);c.drawString(40,777,sub)
heading('SC12 - nominal mechanical drawing','Rev D / component-side view / 1:1 at 100% print / dimensions in mm')
ox,oy=180,560
def xy(x,y):return ox+x*mm,oy-y*mm
c.setLineWidth(.6);c.rect(*xy(0,64),52*mm,64*mm)
for ref in ['J1','J2','J3','J4','J5','J6']:
 f=fps[ref];n=2 if ref in ['J1','J2','J3'] else 3
 xs=[p['x_mm'] for p in f['pads']];ys=[-p['y_mm'] for p in f['pads']]
 left=min(xs)-2.1;top=min(ys)-6.05 if n==2 else min(ys)-1.7
 c.setStrokeColor(colors.grey);c.rect(*xy(left,top+14.75),((n-1)*3.5+4.2)*mm,14.75*mm)
 c.setStrokeColor(colors.black);c.setFont('Helvetica',7);c.drawCentredString(*xy((min(xs)+max(xs))/2,top+5),ref)
 for p in f['pads']:c.circle(*xy(p['x_mm'],-p['y_mm']),.55*mm)
for ref in ('H1','H2'):
 f=fps[ref];x,y=f['x_mm'],-f['y_mm'];c.circle(*xy(x,y),1.6*mm);c.setFont('Helvetica',7);c.drawString(*xy(x+4,y),ref)
for x in (0,52):
 c.line(*xy(x,0),*xy(x,-9))
c.line(*xy(0,-7),*xy(52,-7));c.setFont('Helvetica',9);c.drawCentredString(*xy(26,-9),'52.00')
c.line(*xy(52,0),*xy(61,0));c.line(*xy(52,64),*xy(61,64));c.line(*xy(59,0),*xy(59,64));c.drawString(*xy(61,29),'64.00')
lines=['PCB: 52 x 64 x 1.6 mm. Four layers, nominal 1 oz copper.',
 'Mounts: H1 (3.5, 4.0), H2 (48.5, 42.5); diameter 3.2 NPTH.',
 'Keep hardware contact diameter <=6.4 mm; use insulating supports as needed.',
 'Conservative terminal envelope: 52 x 72.1 mm, before wires/button clearance.',
 'Terminal height: 8.5 above mounting face; pin tips 3.5 below that face.',
 'On a 1.6 mm PCB, pin tips project nominally 1.9 mm beyond the bottom.',
 'Housing geometry is manufacturer nominal CAD. Physical fit untested.',
 'Origin: top-left PCB corner. X right; Y down in this drawing.']
for i,s in enumerate(lines):c.setFont('Helvetica',9);c.drawString(40,325-i*17,s)
c.showPage();heading('Service contacts and solder selectors','Component-side view / enlarged, not 1:1 / no stencil paste on these contacts')
ox,oy=95,640;scale=18
f=fps['J8'];c.setFont('Helvetica-Bold',11);c.drawString(40,730,'J8: custom TC2050-IDC-NL mapping; use a mapped adapter')
for p in f['pads']:
 if not p['number']:continue
 x=95+(p['x_mm']-21.46)*scale;y=665-(-p['y_mm']-5.115)*scale
 c.setFillColor(colors.HexColor('#dbad34'));c.circle(x,y,.3937*scale,stroke=1,fill=1)
 c.setFillColor(colors.black);c.setFont('Helvetica',7);c.drawCentredString(x,y-2,p['number'])
mapping=['1 NRST','2 UART RX','3 UART TX','4 SWCLK','5 SWDIO','6 +3V3 VTref sense only','7 GND','8 GND','9 BOOT0','10 GND']
for i,s in enumerate(mapping):c.setFont('Helvetica',10);c.drawString(310,692-i*17,s)
c.setFont('Helvetica',9);c.drawString(40,495,'Power through J1; adapter/probe power disconnected. Lower row 1-5; upper row 10-6.')
for ch in range(1,4):
 y=435-(ch-1)*75
 for x,ref in [(110,f'JP{ch}01'),(340,f'JP{ch}03')]:
  c.setFont('Helvetica-Bold',11);c.drawCentredString(x+24,y+24,ref+(' POWER' if ref.endswith('01') else ' BIAS'))
  for n in (1,2,3):
   c.setFillColor(colors.HexColor('#dbad34'));c.rect(x+(n-1)*24-8,y-10,16,20,fill=1);c.setFillColor(colors.black);c.drawCentredString(x+(n-1)*24,y-3,str(n))
 c.setFont('Helvetica',9);c.drawString(60,y-26,'1-2 = 5V; 2-3 = 12V; open = off');c.drawString(290,y-26,'1-2 = NPN; 2-3 = PNP; open = push-pull')
c.setFont('Helvetica-Bold',10);c.drawString(40,160,'ONE BRIDGE PER SELECTOR. Both power bridges short 12V to 5V.')
c.setFont('Helvetica',9);c.drawString(40,140,'JP2: bridge for 120 ohm CAN end termination; open at intermediate nodes.')
c.drawString(40,120,'All selectors open by default. Change settings only with input power disconnected.')
c.save()

dest=R/'order/RevD_SC12_Factory_Upload.zip'
files=[]
for pat in ['output/fabrication/*','output/assembly/*','output/mechanical/*','output/documentation/BOM_RevD_SC12.pdf','bom/Factory_BOM.csv','bom/BOM_per_reference.csv','docs/FACTORY_ORDER.md','docs/ASSEMBLY.md','docs/WIRING.md','docs/VALIDATION.md','firmware/build/sensor_can.hex']:
 files.extend(p for p in R.glob(pat) if p.is_file())
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(set(files)):z.write(p,p.relative_to(R))
(dest.with_suffix('.zip.sha256')).write_text(hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name+'\n')
print('Built BOM PDF, mechanical/service drawing and factory upload ZIP.')
