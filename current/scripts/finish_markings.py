"""Apply Rev H top-side wiring legends and the sugarCANe bottom artwork.

Replaces board text and the bottom artwork. Footprint markings and the RGB
light-duct circle stay intact. Front labels occupy the connector gaps.
"""
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];fn=R/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(fn))
for t in list(b.GetDrawings()):
 if isinstance(t,p.PCB_TEXT):b.RemoveNative(t)
def text(value,x,y,size=1,back=False,angle=0):
 t=p.PCB_TEXT(b);t.SetText(value);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetTextSize(p.VECTOR2I(p.FromMM(size),p.FromMM(size)));t.SetTextThickness(p.FromMM(.12 if size<1.5 else .2));t.SetLayer(p.B_SilkS if back else p.F_SilkS);t.SetMirrored(back);t.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));b.Add(t)
text('VIN',5.2,10.3,.9)
for x,label in [(9.5,'GND'),(13,'+')]:text(label,x,11.1,.8)
# Matching pair spacing; the slight left offset clears D20's exposed top pad.
for x,label in [(35.2,'L(G)'),(39,'H(Y)'),(44.7,'L(G)'),(48.5,'H(Y)')]:text(label,x,10.8,.8)
text('CAN',42,6,.8,angle=90)
text('TERM',16.3,5.2,.8,angle=90)
text('DEBUG',25.3,9.55,.8)
text('SC12 REV H',25,.7,.8)
text('RGB',48,41.3,.8)
for ch,x in enumerate([5,21,37],1):
 # Below the shifted header/cap envelope; the bias components are underneath.
 text('5V',x+1.3,58,.8);text('12V',x+4.1,58,.8)
 for xx,label in [(x+1.5,f'V{ch}'),(x+5,'GND'),(x+8.5,f'IN{ch}')]:text(label,xx+(.5 if ch==3 and label=='GND' else 0),59.3,.8)
from apply_bottom_artwork import apply_bottom_artwork
apply_bottom_artwork(b)
p.SaveBoard(str(fn),b)
