"""Apply the compact board's underside brand and service legends."""
from pathlib import Path
import pcbnew as p
from layout_contract import CONTRACT

def apply_bottom_artwork(board):
    removed=[]
    for item in list(board.GetDrawings()):
        if item.GetLayer()==p.B_SilkS:
            board.RemoveNative(item);removed.append(item)
    def label(value,xy):
        item=p.PCB_TEXT(board);item.SetText(value);item.SetLayer(p.B_SilkS)
        item.SetMirrored(True);item.SetPosition(p.VECTOR2I(*[p.FromMM(v) for v in xy]))
        item.SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)))
        item.SetTextThickness(p.FromMM(.08));board.Add(item)
    label('sugarCANe',(18.4,.65))
    x,y=CONTRACT['placements']['JP2']['at_mm'];label('TERM',(x-3.8,y))
    x,y=CONTRACT['placements']['TP1']['at_mm'];label('GND',(x,y-1.65))

if __name__=='__main__':
    path=(Path(__file__).resolve().parents[1]/'hardware/FRC_Sensor_CAN.kicad_pcb').resolve()
    pro=str(path.with_suffix('.kicad_pro'));sm=p.GetSettingsManager();sm.LoadProject(pro)
    board=p.LoadBoard(str(path));board.SetProject(sm.GetProject(pro))
    apply_bottom_artwork(board);p.SaveBoard(str(path),board)
