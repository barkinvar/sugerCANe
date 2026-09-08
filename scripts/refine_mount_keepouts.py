"""Guarantee a 3.5 mm radial copper clearance with polygonal mounting keepouts."""
from pathlib import Path
import math
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(path))
count=0
for zone in b.Zones():
    if not zone.GetIsRuleArea():continue
    outline=zone.Outline()
    xs=[];ys=[]
    for i in range(outline.TotalVertices()):
        pt=outline.CVertex(i);xs.append(p.ToMM(pt.x));ys.append(p.ToMM(pt.y))
    x=(min(xs)+max(xs))/2;y=(min(ys)+max(ys))/2
    if (round(x),round(y)) not in [(4,4),(92,4),(4,92),(92,92)]:continue
    outline.RemoveAllContours();outline.NewOutline()
    for i in range(48):
        a=2*math.pi*i/48
        outline.Append(p.VECTOR2I(p.FromMM(x+3.52*math.cos(a)),p.FromMM(y+3.52*math.sin(a))))
    count+=1
assert count==4,count
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
print('Updated four mounting keepouts; nominal vertex radius 3.52 mm, minimum radial clearance 3.512 mm.')
