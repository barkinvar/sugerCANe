"""Print U5's actual native pad orientation for manual LQFP installation."""
from pathlib import Path
import hashlib,json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'reports/manufacturing/board_manifest.json').read_text())
fp={x['reference']:x for x in manifest['components']}
u=fp['U5'];pads={p['number']:p for p in u['pads']}
assert len(pads)==32 and u['value']=='STM32F042K6T6'
out=R/'output/documentation/MCU_hand_solder_map.pdf'
c=canvas.Canvas(str(out),pagesize=A4)
c.setTitle('sugarCANe Rev H - manual MCU orientation')
c.setFont('Helvetica-Bold',20);c.drawString(40,798,'U5: hand-solder the original MCU')
c.setFont('Helvetica',11);c.drawString(40,776,'STM32F042K6T6 / LQFP32 / DigiKey 497-14647-ND')
c.drawString(40,757,'Component-side view. Board top edge is up. Do not mirror this diagram.')

# The native manifest uses +X right, negative Y down from PCB top-left.
scale=27;cx,cy=300,488
def xy(x,y):return cx+(x-u['x_mm'])*scale,cy+(y-u['y_mm'])*scale
c.setStrokeColor(colors.HexColor('#176b4e'));c.setFillColor(colors.HexColor('#edf7f0'))
c.rect(cx-7/2*scale,cy-7/2*scale,7*scale,7*scale,fill=1)
c.setFont('Helvetica-Bold',12);c.setFillColor(colors.black);c.drawCentredString(cx,cy+8,'U5')
c.setFont('Helvetica',10);c.drawCentredString(cx,cy-10,'7 x 7 mm body')
for number,p in pads.items():
    x,y=xy(p['x_mm'],p['y_mm'])
    horizontal=abs(p['x_mm']-u['x_mm'])>abs(p['y_mm']-u['y_mm'])
    w,h=(1.45*scale,.45*scale) if horizontal else (.45*scale,1.45*scale)
    c.setFillColor(colors.HexColor('#e98b2d') if number=='1' else colors.HexColor('#c9b78c'))
    c.rect(x-w/2,y-h/2,w,h,fill=1)
    c.setFillColor(colors.black);c.setFont('Helvetica',8)
    if horizontal:
        if x<cx:c.drawRightString(x-w/2-7,y-3,number)
        else:c.drawString(x+w/2+7,y-3,number)
    else:c.drawCentredString(x,y+(h/2+7 if y>cy else -h/2-12),number)
p=pads['1'];x,y=xy(p['x_mm'],p['y_mm']);c.setStrokeColor(colors.HexColor('#ce5e13'))
c.setLineWidth(2);c.line(55,685,x-12,y+10)
c.setFillColor(colors.HexColor('#ce5e13'));c.setFont('Helvetica-Bold',13);c.drawString(45,706,'PIN 1 - match the package pin-one mark')
c.setFillColor(colors.black);c.setFont('Helvetica',10)
lines=[
    '1. Leave the board unpowered. Install U5 before tall terminals and headers.',
    '2. Align the pin-one mark and all four rows. Tack two opposite corner leads.',
    '3. Recheck alignment, add flux and solder the remaining leads with an iron.',
    '4. Wick bridges, clean as specified for the flux, and inspect all 32 leads.',
    '5. Check supply shorts and adjacent leads against the schematic before power.',
    'No central exposed pad: all solder joints are on visible perimeter leads.',
    'Factory U5 pads must arrive unpasted. A QFN / K6U6TR will not fit.',
    'Use the full ordering guide for current-limited bring-up and SWD programming.',
]
for i,line in enumerate(lines):c.drawString(40,286-i*20,line)
c.setFont('Helvetica',8)
c.drawString(40,90,f"U5 center: X={u['x_mm']:g}, Y={-u['y_mm']:g} mm from board top-left.")
c.drawString(40,76,f"Pad 1 center: X={p['x_mm']:g}, Y={-p['y_mm']:g} mm from board top-left.")
c.drawString(40,52,'Pad centers and numbering from the native board manifest; drawing is enlarged, not 1:1.')
c.save()
print(out)
