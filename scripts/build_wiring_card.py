"""Produce bench wiring and mounting drawings from the reviewed PCB pad positions."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/documentation'
manifest = ROOT / 'reports/manufacturing/board_manifest.json'
parts = {c['reference']: c for c in json.loads(manifest.read_text())['components']}
ink, blue, orange, green = '#173348', '#156e97', '#b85016', '#147653'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})

def pad_xy(ref, number):
    p = next(p for p in parts[ref]['pads'] if p['number'] == str(number))
    return p['x_mm'], -p['y_mm']

# The textual left/right instructions must follow the actual saved board.
for ref in ('J1', 'J2', 'J3'):
    assert pad_xy(ref, 2)[0] < pad_xy(ref, 1)[0]
for ref in ('J4', 'J5', 'J6', 'J7'):
    assert pad_xy(ref, 1)[0] < pad_xy(ref, 2)[0] < pad_xy(ref, 3)[0]
for ref in ('JP101', 'JP201', 'JP301', 'JP401'):
    assert [p['net'] for p in sorted(parts[ref]['pads'], key=lambda p:int(p['number']))] == ['SENSOR_5V', 'VPORT'+ref[2], 'SENSOR_VBAT']

def dot(ax, x, y, number, color=blue, radius=.65, fontsize=5.5):
    shape = Rectangle((x-radius, y-radius), 2*radius, 2*radius) if number == '1' else Circle((x, y), radius)
    shape.set(facecolor=color, edgecolor='white', linewidth=.25)
    ax.add_patch(shape)
    ax.text(x, y, number, color='white', fontsize=fontsize, ha='center', va='center', fontweight='bold')

def heading(fig, title, subtitle):
    fig.text(.04, .95, title, fontsize=20, fontweight='bold', color=ink)
    fig.text(.04, .915, subtitle, fontsize=9, color=ink)
    fig.text(.04, .035, 'REV A PROTOTYPE  |  Unbuilt; follow the handbook and qualification procedure.', fontsize=8, color=ink)

def paragraph(ax, y, title, lines):
    ax.text(0, y, title, color=blue, fontsize=11, fontweight='bold', va='top')
    ax.text(0, y-.045, '\n'.join(lines), color=ink, fontsize=9, linespacing=1.5, va='top')

with PdfPages(OUT / 'wiring_card.pdf') as pdf:
    fig = plt.figure(figsize=(11.69, 8.27))
    heading(fig, 'Bench connector map', 'TOP view · input/CAN edge at top · sensor edge at bottom · pad positions taken from the PCB')
    ax = fig.add_axes([.04, .10, .51, .79]); ax.set_aspect('equal')
    ax.set(xlim=(-3, 99), ylim=(99, -3)); ax.axis('off')
    ax.add_patch(Rectangle((0, 0), 96, 96, facecolor='#f0f5f4', edgecolor=ink, linewidth=1.1))
    for ref in ('H1', 'H2', 'H3', 'H4'):
        p = parts[ref]['pads'][0]
        ax.add_patch(Circle((p['x_mm'], -p['y_mm']), 1.6, facecolor='white', edgecolor=ink, linewidth=.5))
    for ref in ('U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'F1', 'L1'):
        c=parts[ref]; x,y=c['x_mm'],-c['y_mm']
        ax.add_patch(Rectangle((x-2, y-1.4),4,2.8,facecolor='#d2dddf',edgecolor='none'))
        ax.text(x,y,ref,fontsize=6,ha='center',va='center',color='#496170')
    for ref,c in parts.items():
        if not ref.startswith('J'): continue
        xy=[(p['x_mm'],-p['y_mm']) for p in c['pads']]
        xs,ys=zip(*xy)
        if not ref.startswith('JP') and ref!='J8':
            ax.add_patch(Rectangle((min(xs)-2.1,min(ys)-2.2),max(xs)-min(xs)+4.2,4.4,
                                   facecolor='#cfe4d9',edgecolor=green,linewidth=.6))
        else:
            ax.add_patch(Rectangle((min(xs)-1.2,min(ys)-1.2),max(xs)-min(xs)+2.4,max(ys)-min(ys)+2.4,
                                   facecolor='#dce9ef',edgecolor=blue,linewidth=.4))
        ax.text((min(xs)+max(xs))/2,min(ys)-2.7,ref,fontsize=6,ha='center',color=ink,fontweight='bold')
        for p,(x,y) in zip(c['pads'],xy):
            color=ink if p['net']=='GND' else orange if p['net'].startswith(('VIN','VPORT','SENSOR_')) else blue
            dot(ax,x,y,p['number'],color,.80 if ref in ('J1','J2','J3','J4','J5','J6','J7') else .68)
    for ref,c in parts.items():
        if ref.startswith('TP'):
            x,y=c['x_mm'],-c['y_mm']
            ax.add_patch(Circle((x,y),.75,facecolor='#dbb73d',edgecolor=ink,linewidth=.3))
            ax.text(x,y-1.8,ref,fontsize=5.5,ha='center',color=ink)
    ax.text(58,44,'FRC SENSOR CAN\n96 × 96 mm',ha='center',va='center',fontsize=11,color='#6b858e')
    ax.text(48,97.7,'Square pad = pin 1. Drawing omits most components and all traces.',fontsize=6.6,ha='center',color=ink)
    info=fig.add_axes([.59,.095,.38,.79]);info.axis('off')
    paragraph(info,.985,'J1 · board input', ['Pin 1 = +6–18 V target; pin 2 = GND.', 'In this top view, + is RIGHT and GND is LEFT.', 'Use one protected robot distribution branch.'])
    paragraph(info,.82,'J2 / J3 · CAN trunk', ['Pin 1 = CAN H; pin 2 = CAN L.', 'In this top view, H is RIGHT and L is LEFT.', 'JP2 adds 120 Ω. Leave open at an intermediate node.', 'JP1 shorts RESET to GND; normally leave open.'])
    paragraph(info,.62,'J4 / J5 / J6 / J7 · channels 1 / 2 / 3 / 4', ['LEFT → RIGHT: 1 POWER · 2 GND · 3 SIGNAL.', 'POWER is selected 5 V or protected battery.', '300 mA target per shared rail, not per connector.', 'External sensor supply: leave POWER disconnected.'])
    paragraph(info,.415,'J8 · custom service header, 2.54 mm pitch', ['Top row:     1 VTref OUT    |  2 SWDIO', '                     3 GND              |  4 SWCLK', '                     5 GND              |  6 UART TX', '                     7 BOOT0          |  8 UART RX', 'Bottom row: 9 GND              | 10 RESET', 'Use mapped individual leads; not a Cortex ribbon.', '3.3 V UART only. Leave adapter power disconnected.'])
    paragraph(info,.135,'Test points', ['TP1 GND · TP2 protected input · TP3 internal 5 V', 'TP4 3V3 · TP5 switched 5 V · TP6 switched battery', 'TP7 / TP8 / TP9 / TP10 = conditioned inputs 1–4'])
    pdf.savefig(fig); fig.savefig(OUT/'connector_map.png',dpi=190);plt.close(fig)

    fig=plt.figure(figsize=(11.69,8.27))
    heading(fig,'Jumper examples · channel 1','Disconnect board and sensor power before changing shunts. These drawings keep the TOP-view pin orientation.')
    examples=[
        ('Industrial NPN', (2,3),False,(1,2),'Battery-capable sensor; selected-port pull-up.'),
        ('Industrial PNP', (2,3),False,(5,6),'Battery-capable sensor; signal pull-down.'),
        ('5 V push-pull', (1,2),True,None,'5 V supply; externally driven 3.3/5 V signal.'),
        ('3.3 V open-drain signal', (1,2),True,(3,4),'Only if the sensor supply accepts 5 V.'),
        ('Dry contact to ground',None,True,(3,4),'Contact between SIGNAL and GND; POWER unused.'),
        ('Externally powered 24 V PNP',None,False,(5,6),'Common GND and SIGNAL only; POWER unused.'),
    ]
    for idx,(name,power,logic,bias,note) in enumerate(examples):
        col,row=idx%2,idx//2
        ax=fig.add_axes([.04+col*.49,.65-row*.27,.46,.235]);ax.set(xlim=(0,100),ylim=(39,0));ax.axis('off')
        ax.add_patch(FancyBboxPatch((.5,.5),99,38,boxstyle='round,pad=.0,rounding_size=2',facecolor='#f1f6f7',edgecolor='#b9cfd5',linewidth=.6))
        ax.text(4,5,name,fontsize=12,fontweight='bold',color=ink)
        for ref,xoff,label in [('JP101',12,'POWER'),('JP102',43,'THRESHOLD'),('JP103',77,'BIAS')]:
            ps=parts[ref]['pads']; minx=min(p['x_mm'] for p in ps);miny=min(-p['y_mm'] for p in ps)
            positions={int(p['number']):(xoff+(p['x_mm']-minx)*2,15+(-p['y_mm']-miny)*2) for p in ps}
            selected=power if ref=='JP101' else (1,2) if ref=='JP102' and logic else bias if ref=='JP103' else None
            if selected:
                xs,ys=zip(*(positions[n] for n in selected))
                ax.plot(xs,ys,color=orange,linewidth=9,solid_capstyle='round',zorder=1)
            for n,(x,y) in positions.items():dot(ax,x,y,str(n),blue,1.4,7)
            ax.text(xoff-5,10.5,ref+' '+label,fontsize=7,color=ink)
            setting='OPEN' if selected is None else f'{selected[0]}–{selected[1]}'
            ax.text(xoff+11,20,setting,fontsize=8,fontweight='bold',color=orange)
        ax.text(4,35,note,fontsize=8,color=ink)
    fig.text(.04,.095,'Repeat JP1xx settings at JP2xx / JP3xx / JP4xx for channels 2 / 3 / 4. Fit at most ONE power shunt and ONE bias shunt per channel.',fontsize=8.2,color=ink)
    fig.text(.04,.068,'Threshold OPEN = industrial; FITTED = logic. Verify actual sensor LOW/HIGH/leakage limits and inversion. Firmware defaults to sensor rails OFF.',fontsize=8.2,color=ink)
    pdf.savefig(fig);fig.savefig(OUT/'jumper_examples.png',dpi=190);plt.close(fig)

# Independent physical-scale mounting print. Draw directly in PDF points.
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
c=Canvas(str(OUT/'mounting_template.pdf'),pagesize=A4)
c.setTitle('FRC Sensor CAN Rev A — 1:1 mounting template')
c.setFont('Helvetica-Bold',17);c.drawString(20*mm,278*mm,'FRC Sensor CAN · mounting template')
c.setFont('Helvetica',10);c.drawString(20*mm,269*mm,'Print at 100% / actual size. Verify the 50 mm ruler before drilling.')
x0,y0=57*mm,130*mm
c.setLineWidth(.6);c.rect(x0,y0,96*mm,96*mm)
for ref in ('H1','H2','H3','H4'):
    p=parts[ref]['pads'][0];x=x0+p['x_mm']*mm;y=y0+(96+p['y_mm'])*mm
    c.circle(x,y,1.6*mm);c.setDash(2,2);c.circle(x,y,3.5*mm);c.setDash()
    c.line(x-3*mm,y,x+3*mm,y);c.line(x,y-3*mm,x,y+3*mm)
    c.drawString(x+4*mm,y+2*mm,ref)
c.setFont('Helvetica',10);c.drawCentredString(x0+48*mm,y0+51*mm,'TOP VIEW — input/CAN edge above')
c.drawCentredString(x0+48*mm,y0+43*mm,'96 x 96 mm PCB; 88 x 88 mm hole centers')
c.drawCentredString(x0+48*mm,y0+35*mm,'4 x 3.2 mm NPTH; centers 4 mm from edges')
c.setLineWidth(1);c.line(80*mm,109*mm,130*mm,109*mm)
for i in range(6):c.line((80+10*i)*mm,107*mm,(80+10*i)*mm,111*mm)
c.drawCentredString(105*mm,102*mm,'This line must measure 50 mm')
for y,text in [(87,'Use M3 nylon hardware and at least 10 mm standoffs.'),
               (80,'Dashed circles show 3.5 mm nominal copper-clearance radius.'),
               (73,'Allow room beyond the board for terminal wiring and screwdriver access.'),
               (66,'Check the actual PCB, hardware and enclosure before making final holes.'),
               (52,'Revision A prototype. Nominal geometry; not a measured or certified part.')]:
    c.drawString(20*mm,y*mm,text)
c.save()
report={'result':'GENERATED','source_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
        'method':'Connector/pin positions and mounting centers read from PCB manifest; jumper examples use native top-view orientation.',
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'wiring_card.pdf',OUT/'mounting_template.pdf')}}
(ROOT/'reports/manufacturing/wiring_card.json').write_text(json.dumps(report,indent=2)+'\n')
print('Generated two-page wiring card, preview PNGs and true-scale mounting template.')
