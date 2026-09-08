"""Use a 3.31 mm circumscribed 48-gon, keeping at least 3.3029 mm radius clear."""
from pathlib import Path
import math,sexpdata as s
R=Path(__file__).resolve().parents[1];p=R/'hardware/FRC_Sensor_CAN.kicad_pcb';b=s.loads(p.read_text())
for z in b:
 if not isinstance(z,list) or not z or str(z[0])!='zone':continue
 if not any(isinstance(t,list) and t and str(t[0])=='keepout' for t in z):continue
 poly=next(t for t in z if isinstance(t,list) and t and str(t[0])=='polygon')
 pts=poly[1]
 if len(pts)!=49:continue
 cx=sum(float(p[1]) for p in pts[1:])/48;cy=sum(float(p[2]) for p in pts[1:])/48
 cx=round(cx,1);cy=round(cy,1)
 assert (cx,cy) in ((3.5,4.0),(48.5,34.5))
 pts[1:]=[[s.Symbol('xy'),round(cx+3.31*math.cos(i*math.tau/48),6),round(cy+3.31*math.sin(i*math.tau/48),6)] for i in range(48)]
p.write_text(s.dumps(b)+'\n')
