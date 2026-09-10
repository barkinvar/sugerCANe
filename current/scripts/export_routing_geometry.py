"""Export saved native routing geometry for the independent routing-style gate."""
from pathlib import Path
import argparse, json
import pcbnew as p

R = Path(__file__).resolve().parents[1]


def export(board_path):
    board = p.LoadBoard(str(board_path))
    result = {'tracks': [], 'pads': [], 'vias': [], 'endpoint_zone_contacts': {}}
    for item in board.GetTracks():
        common = dict(id=item.m_Uuid.AsString(), net=item.GetNetname())
        if isinstance(item, p.PCB_VIA):
            result['vias'].append(dict(**common, at=list(p.ToMM(item.GetPosition())),
                width=p.ToMM(item.GetWidth(p.F_Cu)), layers=list(item.GetLayerSet().Seq())))
        else:
            result['tracks'].append(dict(**common, kind='arc' if isinstance(item, p.PCB_ARC) else 'line',
                a=list(p.ToMM(item.GetStart())), b=list(p.ToMM(item.GetEnd())),
                width=p.ToMM(item.GetWidth()), layer=item.GetLayer()))
            # A ground-pour entry can intentionally end away from pads/tracks.
            # Use saved filled copper, not the zone outline or a net-name exemption.
            ends = [end for end, point in [('a', item.GetStart()), ('b', item.GetEnd())]
                    if any(z.GetNetCode() == item.GetNetCode() and z.IsOnLayer(item.GetLayer())
                           and z.HitTestFilledArea(item.GetLayer(), point) for z in board.Zones())]
            if ends:
                result['endpoint_zone_contacts'][common['id']] = ends
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            for layer in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu):
                if not pad.IsOnLayer(layer):
                    continue
                poly = p.SHAPE_POLY_SET()
                pad.TransformShapeToPolygon(poly, layer, 0, 500, p.ERROR_OUTSIDE)
                result['pads'].append(dict(ref=footprint.GetReference(), number=pad.GetNumber(),
                    net=pad.GetNetname(), layer=layer, at=list(p.ToMM(pad.GetPosition())),
                    polygons=[[[*p.ToMM(poly.COutline(i).CPoint(j))]
                               for j in range(poly.COutline(i).PointCount())]
                              for i in range(poly.OutlineCount())]))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', nargs='?', type=Path, default=R/'hardware/FRC_Sensor_CAN.kicad_pcb')
    args = parser.parse_args()
    print(json.dumps(export(args.board)))
