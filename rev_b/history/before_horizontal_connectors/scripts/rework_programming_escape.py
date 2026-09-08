from pathlib import Path
import json,sexpdata as s
from shapely.geometry import LineString,Point,box
R=Path(__file__).resolve().parents[1];f=R/'hardware/FRC_Sensor_CAN.kicad_pcb';a=s.loads(f.read_text());area=box(28,0,34.6,11.5)
def prop(z,t):return next((v for v in z if isinstance(v,list) and v and str(v[0])==t),None)
removed=[];targets={};pn={'NRST','UART_RX','UART_TX','SWCLK','SWDIO','BOOT0','+3V3','GND'}
for z in a[:]:
 if not isinstance(z,list) or str(z[0]) not in ['segment','via']:continue
 net=prop(z,'net')[1]
 if net not in pn:continue
 if str(z[0])=='via':
  q=prop(z,'at')[1:3]
  if net!='GND' and area.contains(Point(*q)):
   targets[net]=[1,*q];a.remove(z);removed.append(z)
 elif prop(z,'layer')[1]=='F.Cu':
  st=prop(z,'start')[1:3];en=prop(z,'end')[1:3]
  if LineString([st,en]).buffer(float(prop(z,'width')[1])/2).intersects(area):
   for q in [st,en]:
    if not area.contains(Point(*q)) and net not in targets:targets[net]=[0,*q]
   a.remove(z);removed.append(z)
f.write_text(s.dumps(a));(R/'hardware/design/pogo_escape_targets.json').write_text(json.dumps(targets,indent=2)+'\n');print('removed',len(removed),'targets',targets)
