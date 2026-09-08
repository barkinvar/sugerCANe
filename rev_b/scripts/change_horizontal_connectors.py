"""One-time native PCB conversion of the six /135 connectors to /90.

Retain rear pin row to protect existing critical routes; move front row 2 mm outward.
Subsequent DRC/routing review remains required. Refuse a repeated conversion.
"""
from pathlib import Path
import sexpdata as s
import uuid
import math
import json

R = Path(__file__).resolve().parents[1]
path = R / 'hardware/FRC_Sensor_CAN.kicad_pcb'
board = s.loads(path.read_text())
def tag(a): return str(a[0]) if isinstance(a, list) and a else ''
def child(a, key): return next(v for v in a if tag(v) == key)
changes = []
for fp in board[:]:
    if tag(fp) != 'footprint': continue
    ref = next(v[2] for v in fp if tag(v) == 'property' and v[1] == 'Reference')
    if ref not in ['J1', 'J2', 'J3', 'J4', 'J5', 'J6']: continue
    assert 'Weidmuller_LSF_135_' in fp[1], (ref, fp[1])
    count = 2 if ref in ['J1', 'J2', 'J3'] else 3
    fp[1] = f'FRC_Sensor_CAN:Weidmuller_LSF_90_{count}P'
    at = child(fp, 'at'); old_origin = at[1:3]
    angle = at[3] if len(at) > 3 else 0
    delta = -2 if angle == 180 else 2
    for prop in fp:
        if tag(prop) != 'property': continue
        if prop[1] == 'MPN': prop[2] = '1824420000' if count == 2 else '1824430000'
        if prop[1] == 'Notes': prop[2] = 'Horizontal /90 push-in; 8 mm strip, 7 mm pin-row spacing, two solder pins per pole.'
    for item in fp:
        if tag(item) == 'fp_rect':
            layer = child(item, 'layer')[1]
            child(item, 'start')[2] = -1.95 if layer == 'F.CrtYd' else -1.7
            child(item, 'end')[2] = 13.30 if layer == 'F.CrtYd' else 13.05
        if tag(item) == 'model': item[1] = item[1].replace('_135_', '_90_')
        if tag(item) != 'pad': continue
        pa = child(item, 'at')
        if pa[2] == 0: continue
        assert pa[2] == 5
        pa[2] = 7
        xx = old_origin[0] + (pa[1] if angle == 0 else -pa[1])
        yy = old_origin[1] + (5 if angle == 0 else -5)
        net = child(item, 'net')[1]
        # Reconnect original front-pad trace endpoints to moved copper.
        for layer in ['F.Cu', 'B.Cu']:
            board.append(s.loads(f'(segment (start {xx} {yy}) (end {xx} {yy+delta}) (width 0.5) (layer "{layer}") (net "{net}") (uuid "{uuid.uuid4()}"))'))
    changes.append({'ref': ref, 'old_origin': old_origin, 'new_origin': at[1:3],
                    'orientation_degrees': angle, 'rear_row_retained': True})
assert len(changes) == 6
path.write_text(s.dumps(board) + '\n')
(R / 'reports/horizontal_connector_conversion.json').write_text(json.dumps(changes, indent=2) + '\n')
print('Converted', len(changes), 'connectors; native DRC and routing review required.')
