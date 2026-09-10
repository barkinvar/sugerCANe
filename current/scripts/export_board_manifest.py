"""Export the physical board facts for an independent Gerber/BOM check."""
from pathlib import Path
import json
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
board = p.LoadBoard(str(ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'))
components = []
drills = []
for fp in board.GetFootprints():
    pads = []
    for pad in fp.Pads():
        pos = pad.GetPosition()
        drill = pad.GetDrillSize()
        record = dict(number=pad.GetNumber(), net=pad.GetNetname(),
                      x_mm=p.ToMM(pos.x), y_mm=-p.ToMM(pos.y),
                      copper_top=pad.IsOnLayer(p.F_Cu) and pad.GetAttribute()!=p.PAD_ATTRIB_NPTH, copper_bottom=pad.IsOnLayer(p.B_Cu) and pad.GetAttribute()!=p.PAD_ATTRIB_NPTH)
        pads.append(record)
        if drill.x:
            drills.append(dict(x_mm=record['x_mm'], y_mm=record['y_mm'],
                               diameter_mm=p.ToMM(drill.x),
                               plated=pad.GetAttribute() != p.PAD_ATTRIB_NPTH,
                               source=f'{fp.GetReference()}.{pad.GetNumber()}'))
    pos = fp.GetPosition()
    models = [m.m_Filename for m in fp.Models()]
    for name in models:
        assert name.startswith('${KIPRJMOD}/'), name
        assert (ROOT / 'hardware' / name.removeprefix('${KIPRJMOD}/')).is_file(), name
    components.append(dict(reference=fp.GetReference(), value=fp.GetValue(),
                           side='bottom' if fp.IsFlipped() else 'top',
                           package=str(fp.GetFPID().GetLibItemName()),
                           x_mm=p.ToMM(pos.x), y_mm=-p.ToMM(pos.y),
                           rotation_deg=fp.GetOrientationDegrees(), pads=pads, models=models))
for track in board.GetTracks():
    if isinstance(track, p.PCB_VIA):
        pos = track.GetPosition()
        drills.append(dict(x_mm=p.ToMM(pos.x), y_mm=-p.ToMM(pos.y),
                           diameter_mm=p.ToMM(track.GetDrillValue()), plated=True, source='via'))
out = dict(components=components, drills=drills,
           models_resolved=sum(bool(c['models']) for c in components))
dest = ROOT / 'reports/manufacturing'
dest.mkdir(parents=True, exist_ok=True)
(dest / 'board_manifest.json').write_text(json.dumps(out, indent=2) + '\n')
print(f"Exported {len(components)} footprints, {len(drills)} drills, {out['models_resolved']} local-model assignments")
