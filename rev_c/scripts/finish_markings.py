"""Add wiring legends and product identification; dimensions are board coordinates in mm."""
from pathlib import Path
import pcbnew as p
import subprocess, os
R=Path(__file__).resolve().parents[1];fn=R/'hardware/FRC_Sensor_CAN.kicad_pcb'
env=dict(os.environ)
env.pop('PYTHONHOME',None); env.pop('PYTHONPATH',None)
subprocess.run(['python',str(R/'scripts/prune_markings.py')],check=True,env=env)
b=p.LoadBoard(str(fn))
def text(value,x,y,size=1,back=False):
 t=p.PCB_TEXT(b);t.SetText(value);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetTextSize(p.VECTOR2I(p.FromMM(size),p.FromMM(size)));t.SetTextThickness(p.FromMM(.12 if size<1.5 else .2));t.SetLayer(p.B_SilkS if back else p.F_SilkS);t.SetMirrored(back);b.Add(t)
text('SC LITE',24,1.05,1.2)
for x,label in [(9.5,'G'),(13,'+'),(35.5,'L'),(39,'H'),(45,'L'),(48.5,'H')]:text(label,x,10.85 if label=='+' else 10.65 if x==35.5 else 11.1,.8)
for value,y,size in [('SC LITE',17,2.7),('REV C - 3 DIGITAL INPUTS',21,1.2),('6-22V IN | 5V / BAT OUT',24,1.1),('300mA TOTAL PER RAIL',26.5,1.0),('POWER: 1-2=5V / 2-3=BAT',30,.95),('BIAS: 1-2=NPN / 2-3=PNP',32.5,.95),('BIAS OPEN = PUSH-PULL',35,.95),('ONE BRIDGE PER SELECTOR',37.5,1.0),('CYCLE POWER TO RESET OVERLOAD',40,.85),('INPUTS ONLY - NO ACTUATORS',42,.85)]:text(value,26,y,size,True)
for x,l in [(13,'V+'),(9.5,'GND'),(39,'H'),(35.5,'L'),(48.5,'H'),(45,'L')]:text(l,x,5.5,.95,True)
for ch,cx in enumerate([10,26,42],1):
 for dx,l in [(-3.5,'P'),(0,'G'),(3.5,'S')]:text(l,cx+dx,50.5,1.1,True)
 text('INPUT '+str(ch),cx,48.75,.8,True)
text('TERM 120R',17,4,.8,True)
p.SaveBoard(str(fn),b)
