"""Apply the Rev H wiring legends to the final native board, in mm.

Replaces board text only. Footprint markings and the RGB light-duct circle stay
intact. Front labels occupy the gaps outside the fitted connector housings.
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
 text('5V',x+{1:0,2:0,3:.5}[ch],61.95,.8);text('12V',x+4+(.8 if ch==1 else 0),61.95,.8)
 for xx,label in [(x+1.5,f'V{ch}'),(x+5,'GND'),(x+8.5,f'IN{ch}')]:text(label,xx+(.5 if ch==3 and label=='GND' else 0),62.95,.8)
for value,y,size in [('SC12',17,2.7),('REV H - 3 DIGITAL INPUTS',21,1.2),('6-22V IN | 5V / 12V OUT',24,1.1),('300mA TOTAL PER RAIL',26.5,1.0),('POWER: 1-2=5V / 2-3=12V',30,.95),('INPUT MODE: CAN SOFTWARE',32.5,.95),('NPN / PNP / PUSH-PULL',35,.95),('ONE CAP PER POWER HEADER',37.5,.95),('FAULT RESET: CAN SERVICE',40,.85),('INPUTS ONLY - NO ACTUATORS',42,.85),('DEBUG: CUSTOM 2x5 PINOUT',46,.95),('1 RST / 2 RX / 3 TX / 4 CLK / 5 DIO',48.5,.85),('6 3V3 / 7 GND / 8 GND / 9 BOOT / 10 GND',51,.85),('3V3 = TARGET REFERENCE ONLY',53.5,.85),('POWER OFF TO MOVE CAPS',56,.9)]:text(value,26,y,size,True)
for x,l in [(13,'VIN+'),(9.5,'GND'),(39,'H(Y)'),(35.5,'L(G)'),(48.5,'H(Y)'),(45,'L(G)')]:text(l,x,5.5,.85,True)
text('POWER IN',11.25,11.2,.85,True)
text('CAN A',37.25,11.2,.85,True);text('CAN B',46.75,11.2,.85,True)
for ch,cx in enumerate([10,26,42],1):
 for dx,l in [(-3.5,f'V{ch}'),(0,'GND'),(3.5,f'IN{ch}')]:text(l,cx+dx,68.5,.85,True)
 text('INPUT '+str(ch),cx,63.25,.8,True)
 for dx,l in [(-5,'5V'),(-1,'12V')]:text(l,cx+dx,58.6,.8,True)
text('TERM 120R',18,12.5,.8,True)
text('1',17.3,8,.8,True)
p.SaveBoard(str(fn),b)
