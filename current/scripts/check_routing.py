"""Enforce straight 45-degree routing and reject redundant or awkward geometry.

Connectivity/clearance remain separate native DRC and exported-Gerber gates.
Pad/via copper permits short escapes and arbitrary branch angles at the contact;
ordinary free-space bends and tiny zigzags receive no per-net exemptions.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, subprocess
from shapely import STRtree, union_all
from shapely.geometry import LineString, Point, Polygon

R = Path(__file__).resolve().parents[1]
TOL = .00002  # 20 nm: native integer rounding only, not a routing angle allowance.
MIN_FREE_SEGMENT = .10


def inspect(data):
    tracks = data['tracks']
    issues = collections.defaultdict(list)
    contacts = collections.defaultdict(list)
    for pad in data['pads']:
        contacts[pad['net'], pad['layer']].extend(Polygon(v) for v in pad['polygons'])
    for via in data['vias']:
        for layer in via.get('layers', [0, 2, 4, 6]):
            contacts[via['net'], layer].append(Point(via['at']).buffer(via['width']/2, quad_segs=24))
    contacts = {key: union_all(shapes) for key, shapes in contacts.items()}
    lines = [LineString([t['a'], t['b']]) for t in tracks]
    tree = STRtree(lines)
    adjacency = collections.defaultdict(list)
    seen = {}
    contact_segments = 0

    def record(kind, *indices, **detail):
        issues[kind].append(dict(tracks=[tracks[i]['id'] for i in indices],
                                net=tracks[indices[0]]['net'], layer=tracks[indices[0]]['layer'], **detail))

    for i, t in enumerate(tracks):
        if t.get('kind', 'line') != 'line':
            record('curved_tracks', i)
        dx, dy = [abs(t['a'][k]-t['b'][k]) for k in (0, 1)]
        if lines[i].length <= TOL:
            record('zero_length', i)
        elif min(dx, dy, abs(dx-dy)) > TOL:
            record('non_45_direction', i, start_mm=t['a'], end_mm=t['b'])
        ends = sorted(tuple(round(v, 5) for v in t[k]) for k in ('a', 'b'))
        key = (t['net'], t['layer'], t['width'], *ends)
        if key in seen:
            record('duplicates', seen[key], i)
        else:
            seen[key] = i
        for end, other in [('a', 'b'), ('b', 'a')]:
            adjacency[(t['net'], t['layer'], *[round(v, 5) for v in t[end]])].append((i, t[other]))
        contact = contacts.get((t['net'], t['layer']))
        # A short endpoint may extend half its trace width beyond the pad/via:
        # its copper still intersects the contact. This is a geometric contact
        # allowance, not an exemption for an entire footprint or power net.
        at_contact = contact is not None and contact.buffer(t['width']/2+TOL).covers(lines[i])
        if lines[i].length < MIN_FREE_SEGMENT-TOL:
            if at_contact:
                contact_segments += 1
            else:
                record('short_free_segments', i, length_mm=lines[i].length, start_mm=t['a'], end_mm=t['b'])
        for j in tree.query(lines[i].buffer(TOL)):
            j = int(j)
            if j <= i or (t['net'], t['layer']) != (tracks[j]['net'], tracks[j]['layer']):
                continue
            overlap = lines[i].intersection(lines[j])
            if overlap.length > TOL and (contact is None or not contact.buffer(TOL).covers(overlap)):
                record('collinear_overlap', i, j, overlap_mm=overlap.length)

    for key, pair in adjacency.items():
        if len(pair) != 2:
            continue  # T-junctions and multi-branch power distribution are intentional.
        (i, a), (j, b) = pair
        node = Point(key[2:])
        contact = contacts.get(key[:2])
        if contact is not None and contact.buffer(max(tracks[i]['width'], tracks[j]['width'])/2+TOL).covers(node):
            continue
        # Count a branch that joins the interior of a segment, not just endpoints.
        if any(int(k) not in (i, j) and (tracks[int(k)]['net'], tracks[int(k)]['layer']) == key[:2]
               and lines[int(k)].distance(node) <= TOL for k in tree.query(node.buffer(TOL))):
            continue
        va = [a[k]-key[k+2] for k in (0, 1)]
        vb = [b[k]-key[k+2] for k in (0, 1)]
        denominator = math.hypot(*va)*math.hypot(*vb)
        if denominator <= TOL*TOL:
            continue
        angle = math.degrees(math.acos(max(-1, min(1, sum(v*w for v,w in zip(va,vb))/denominator))))
        if angle < 134.9:
            record('sharp_free_bends', i, j, at_mm=list(key[2:]), included_angle_deg=angle)
        elif angle > 179.99 and tracks[i]['width'] == tracks[j]['width']:
            record('redundant_collinear_joint', i, j, at_mm=list(key[2:]))
    return dict(result='FAIL' if issues else 'PASS', segments=len(tracks), vias=len(data['vias']),
                rules=dict(direction_tolerance_mm=TOL, minimum_free_segment_mm=MIN_FREE_SEGMENT,
                           minimum_free_bend_included_angle_deg=135, curved_tracks_allowed=False),
                short_contact_segments=contact_segments, findings=dict(issues),
                scope='Routing geometry only. Copper round end caps are normal; no curved centerlines. '
                      'Pad/via contacts and true branch junctions allow local transitions. '
                      'Native DRC and independent Gerber connectivity/clearance must also pass.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', type=Path, default=R/'hardware/FRC_Sensor_CAN.kicad_pcb')
    parser.add_argument('--output', type=Path, default=R/'reports/routing_rules.json')
    args = parser.parse_args()
    raw = subprocess.check_output(['kicad-python', str(R/'scripts/export_routing_geometry.py'), str(args.board)], text=True)
    report = inspect(json.loads(raw))
    report['board_sha256'] = hashlib.sha256(args.board.read_bytes()).hexdigest()
    report['source_hashes'] = {p: hashlib.sha256((R/p).read_bytes()).hexdigest()
                              for p in ['scripts/check_routing.py', 'scripts/export_routing_geometry.py']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], 'routing rules:', {k:len(v) for k,v in report['findings'].items()},
          f"({report['segments']} segments, {report['vias']} vias)")
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
