"""Put the outlined sugarCANe poster on B.Silkscreen only."""
from pathlib import Path
import re,xml.etree.ElementTree as ET
import pcbnew as p

R=Path(__file__).resolve().parents[1]

def apply_bottom_artwork(board):
    for group in list(board.Groups()):
        if group.GetName()=='sugarCANe artwork':board.RemoveNative(group)
    for drawing in list(board.GetDrawings()):
        if drawing.GetLayer()==p.B_SilkS:board.RemoveNative(drawing)
    root=ET.parse(R/'hardware/artwork/sugarCANe.svg').getroot()
    assert root.get('viewBox')=='0 0 52 74'
    group=p.PCB_GROUP(board);group.SetName('sugarCANe artwork');board.Add(group)
    count=0
    for path in root.iter('{http://www.w3.org/2000/svg}path'):
        poly=p.SHAPE_POLY_SET()
        for i,contour in enumerate(re.findall(r'M\s+([^M]+?)\s*Z',path.attrib['d'])):
            points=[tuple(map(float,xy)) for xy in re.findall(r'(-?[\d.]+),(-?[\d.]+)',contour)]
            if i==0:poly.NewOutline();hole=-1
            else:hole=poly.NewHole(0)
            for x,y in points:
                # Artwork is drawn as viewed from the underside; native PCB
                # coordinates are viewed from the top, so mirror exactly once.
                poly.Append(p.FromMM(26+.85*((52-x)-26)),p.FromMM(10+.8*(y-10)),0,hole)
        # KiCad's native cut-contour representation preserves the letter and
        # stalk holes in one filled graphic, without raster seams or fonts.
        poly.Fracture()
        drawing=p.PCB_SHAPE(board);drawing.SetShape(p.SHAPE_T_POLY)
        drawing.SetPolyShape(poly);drawing.SetFilled(True);drawing.SetWidth(0)
        drawing.SetLayer(p.B_SilkS);board.Add(drawing);group.AddItem(drawing);count+=1
    assert count>0
    assert not any(isinstance(d,p.PCB_TEXT) and d.GetLayer()==p.B_SilkS for d in board.GetDrawings())
    print(f'Applied {count} outlined sugarCANe artwork shapes; no bottom text labels')

if __name__=='__main__':
    path=R/'hardware/FRC_Sensor_CAN.kicad_pcb';board=p.LoadBoard(str(path))
    apply_bottom_artwork(board);p.SaveBoard(str(path),board)
