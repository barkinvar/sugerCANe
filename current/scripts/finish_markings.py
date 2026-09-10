"""Apply wiring legends to the current compact placement without moving copper."""
from pathlib import Path
import argparse
import pcbnew as p
from layout_contract import CONTRACT
from apply_bottom_artwork import apply_bottom_artwork
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',type=Path,default=R/'hardware/FRC_Sensor_CAN.kicad_pcb');args=ap.parse_args();fn=args.board.resolve()
pro=str(fn.with_suffix('.kicad_pro'));sm=p.GetSettingsManager();sm.LoadProject(pro)
b=p.LoadBoard(str(fn));b.SetProject(sm.GetProject(pro));removed=[]
for item in list(b.GetDrawings()):
 if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.F_SilkS:b.RemoveNative(item);removed.append(item)
def text(value,x,y):
 item=p.PCB_TEXT(b);item.SetText(value);item.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
 item.SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));item.SetTextThickness(p.FromMM(.08));item.SetLayer(p.F_SilkS);b.Add(item)
text('SC12 H',40.3,27.8)
text('G',9.2,11.25);text('+',12.7,11.25)
for x,label in [(23.5,'L'),(27,'H'),(37.4,'L'),(40.9,'H')]:text(label,x,11.25)
x,y=CONTRACT['status_led_center_mm'];text('RGB',x,y+1.9)
for ch in range(1,4):
 x,y=CONTRACT['placements'][f'JP{ch}01']['at_mm']
 text('5V',x,y+1.5);text('12V',x+4,y+1.5)
 x,y=CONTRACT['placements'][f'J{ch+3}']['at_mm']
 for dx,label in [(0,f'V{ch}'),(3.5,'G'),(7,f'IN{ch}')]:
  text(label,27.85 if label=='IN2' else x+dx,36.7 if label=='IN2' else y-2.1)
apply_bottom_artwork(b);p.SaveBoard(str(fn),b)
