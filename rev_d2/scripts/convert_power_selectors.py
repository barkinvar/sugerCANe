"""One-time D -> D-2 local footprint conversion; does not reroute the board.

Use on the copied D board only. The reviewed saved D-2 board is authoritative.
Changed track endpoints follow the same numbered pad; native DRC and independent
exported-copper checks must pass after any local clearance repairs.
"""
from pathlib import Path
import pcbnew as p

R = Path(__file__).resolve().parents[1]
path = R / 'hardware/FRC_Sensor_CAN.kicad_pcb'
b = p.LoadBoard(str(path))
template = p.FootprintLoad(str(R / 'hardware/library/FRC_Sensor_CAN.pretty'),
                           'PinHeader_1x03_P2.00mm_Vertical')
keepalive = [template]
for ch in range(1, 4):
    ref = f'JP{ch}01'
    old = b.FindFootprintByReference(ref)
    assert old.GetFPIDAsString() == 'FRC_Sensor_CAN:SolderSelector_3', ref
    oldpads = {d.GetNumber(): d for d in old.Pads()}
    center = oldpads['2'].GetPosition()
    f = p.Cast_to_FOOTPRINT(template.Duplicate(False))
    keepalive.extend([old, oldpads, f])
    f.SetFPIDAsString('FRC_Sensor_CAN:PinHeader_1x03_P2.00mm_Vertical')
    f.SetReference(ref)
    f.SetValue('5V / 12V')
    f.SetPath(old.GetPath())
    f.SetOrientationDegrees(90)
    f.SetPosition(p.VECTOR2I(center.x - p.FromMM(2), center.y))
    f.Reference().SetPosition(old.Reference().GetPosition())
    f.Reference().SetTextSize(old.Reference().GetTextSize())
    f.Reference().SetTextThickness(old.Reference().GetTextThickness())
    f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T))
    f.Value().SetVisible(False)
    for pad in f.Pads():
        source = oldpads[pad.GetNumber()]
        pad.SetNet(source.GetNet())
        for track in b.GetTracks():
            if isinstance(track, p.PCB_VIA):
                continue
            if track.GetNetCode() != source.GetNetCode():
                continue
            if track.GetStart() == source.GetPosition():
                track.SetStart(pad.GetPosition())
            if track.GetEnd() == source.GetPosition():
                track.SetEnd(pad.GetPosition())
    b.Remove(old)
    b.Add(f)
    f.thisown = False
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(path), b)
print('Converted three power selectors to 2 mm through-hole headers.')
