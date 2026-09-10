"""Enforce straight 45-degree routing and reject redundant or awkward geometry.

Connectivity/clearance remain separate native DRC and exported-Gerber gates.
Pad/via copper permits short escapes and arbitrary branch angles at the contact;
free-space branches require explicit endpoints and chamfered three-way geometry.
Ordinary free-space bends and tiny zigzags receive no per-net exemptions.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, subprocess
from shapely import STRtree, union_all
from shapely.geometry import LineString, Point, Polygon

R = Path(__file__).resolve().parents[1]
TOL = .00002  # 20 nm: native integer rounding only, not a routing angle allowance.
MIN_FREE_SEGMENT = .10


def pad_contact_audit(data):
    """Find stray pad contacts while allowing connected bends into that pad.

    A track's round end can overlap a pad just before the next segment enters
    it. That is an ordinary approach. A passing track touching the same pad
    elsewhere needs its own local centerline connection; global net connectivity
    must not hide an incidental corner contact or a redundant loop.
    """
    tracks = data['tracks']
    lines = [LineString([t['a'], t['b']]) for t in tracks]
    tree = STRtree(lines)
    largest_radius = max((t['width']/2 for t in tracks), default=0)
    incidental = []; approaches = []; pairs = 0
    for pad in data['pads']:
        copper = union_all([Polygon(q) for q in pad['polygons']])
        inside = copper.buffer(-.005)  # 5 um interior avoids boundary-only entries.
        nearby = [int(i) for i in tree.query(copper.buffer(largest_radius + TOL))
                  if (tracks[i]['net'], tracks[i]['layer']) == (pad['net'], pad['layer'])]
        contacts = [i for i in nearby if lines[i].buffer(tracks[i]['width']/2, quad_segs=64)
                    .intersection(copper).area > 1e-7]
        pairs += len(contacts)
        grazing = [i for i in contacts if not lines[i].intersects(inside)]
        if not grazing:
            continue
        # Only centerline joins within one local track radius of the pad count.
        # A remote connection through another pad cannot excuse this contact.
        neighborhood = copper.buffer(max(tracks[i]['width']/2 for i in nearby) + .005)
        clipped = {i:lines[i].intersection(neighborhood) for i in nearby}
        joined = collections.defaultdict(set)
        for a in nearby:
            for b in nearby:
                if b > a and clipped[a].distance(clipped[b]) <= TOL:
                    joined[a].add(b); joined[b].add(a)
        entries = {i for i in nearby if lines[i].intersects(inside)}
        for i in grazing:
            reached = {i}; pending = [i]
            while pending:
                for neighbor in joined[pending.pop()] - reached:
                    reached.add(neighbor); pending.append(neighbor)
            local_entries = entries & reached
            row = dict(reference=pad.get('ref'), pad=pad.get('number'),
                       pad_at_mm=pad.get('at'), net=pad['net'], layer=pad['layer'],
                       track=tracks[i]['id'],
                       connected_entry_tracks=sorted(tracks[j]['id'] for j in local_entries))
            (approaches if local_entries else incidental).append(row)
    return dict(pad_layer_shapes_checked=len(data['pads']), same_net_contact_pairs_checked=pairs,
                incidental_contacts=incidental, connected_approach_contacts=approaches,
                scope='All native pad/track copper layers. Positive same-net overlaps require a '
                      'local centerline entry into that pad; connected approach bends are allowed. '
                      'Different-net clearance, via contacts and fabrication geometry have separate gates.')


def branch_junctions(data):
    """Node centerline intersections as well as endpoints; distinguish real rays.

    Segmentation is not connectivity: a tap into a segment interior is a node
    even when KiCad stores the through route as one object.
    """
    tracks=data['tracks'];lines=[LineString([t['a'],t['b']]) for t in tracks]
    tree=STRtree(lines);nodes=collections.defaultdict(set)
    for i,t in enumerate(tracks):
        for end in ('a','b'):
            nodes[(t['net'],t['layer'],*[round(v,5) for v in t[end]])].add(i)
        for j in tree.query(lines[i].buffer(TOL)):
            j=int(j)
            if j<=i or (t['net'],t['layer'])!=(tracks[j]['net'],tracks[j]['layer']):continue
            cross=lines[i].intersection(lines[j])
            if cross.geom_type=='Point':
                nodes[(t['net'],t['layer'],*[round(v,5) for v in cross.coords[0]])].update((i,j))
    result=[]
    for key,ids in nodes.items():
        node=Point(key[2:])
        ids.update(int(i) for i in tree.query(node.buffer(TOL))
                   if (tracks[int(i)]['net'],tracks[int(i)]['layer'])==key[:2]
                   and lines[int(i)].distance(node)<=TOL)
        rays=set();interior=[]
        for i in ids:
            t=tracks[i]
            if min(math.dist(key[2:],t[e]) for e in ('a','b'))>TOL:interior.append(i)
            for end in ('a','b'):
                dx,dy=[t[end][k]-key[k+2] for k in (0,1)]
                if math.hypot(dx,dy)>TOL:rays.add(round(math.degrees(math.atan2(dy,dx)))%360)
        if len(rays)<3:continue
        rays=sorted(rays);sectors=[(b-a)%360 for a,b in zip(rays,rays[1:]+rays[:1])]
        result.append(dict(net=key[0],layer=key[1],at_mm=list(key[2:]),indices=sorted(ids),
                           interior_indices=sorted(interior),rays_deg=rays,sectors_deg=sectors))
    return result


def inspect(data, width_policy=None):
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
    max_width = max((v['width'] for v in tracks), default=0)
    adjacency = collections.defaultdict(list)
    seen = {}
    contact_segments = 0
    zone_entries = 0

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
        # Only centerlines actually inside contact copper get an exception.
        # Growing contacts by half the track width hid pad overshoots and hooks.
        at_contact = contact is not None and contact.buffer(TOL).covers(lines[i])
        if lines[i].length < MIN_FREE_SEGMENT-TOL:
            if at_contact:
                contact_segments += 1
            else:
                record('short_free_segments', i, length_mm=lines[i].length, start_mm=t['a'], end_mm=t['b'])
        for j in tree.query(lines[i].buffer(t['width']/2 + max_width/2)):
            j = int(j)
            if j <= i or (t['net'], t['layer']) != (tracks[j]['net'], tracks[j]['layer']):
                continue
            overlap = lines[i].intersection(lines[j])
            if overlap.length > TOL and (contact is None or not contact.buffer(TOL).covers(overlap)):
                record('collinear_overlap', i, j, overlap_mm=overlap.length)
            elif lines[i].length > TOL and lines[j].length > TOL:
                # Offset parallel tracks may overlap in copper without their
                # centerlines intersecting. Ignore ordinary short junction caps.
                unit = [(t['b'][k]-t['a'][k])/lines[i].length for k in (0,1)]
                other = [(tracks[j]['b'][k]-tracks[j]['a'][k])/lines[j].length for k in (0,1)]
                offset = abs((tracks[j]['a'][0]-t['a'][0])*unit[1] -
                             (tracks[j]['a'][1]-t['a'][1])*unit[0])
                if abs(unit[0]*other[1]-unit[1]*other[0]) <= .0001 and offset < (t['width']+tracks[j]['width'])/2-TOL:
                    projection = sorted(sum((tracks[j][e][k]-t['a'][k])*unit[k] for k in (0,1)) for e in ('a','b'))
                    lo, hi = max(0, projection[0]), min(lines[i].length, projection[1])
                    if hi-lo > max(t['width'], tracks[j]['width'], MIN_FREE_SEGMENT):
                        run = LineString([[t['a'][k]+s*unit[k] for k in (0,1)] for s in (lo,hi)])
                        if contact is None or not contact.buffer(TOL).covers(run):
                            record('parallel_copper_overlap', i, j, overlap_mm=hi-lo, offset_mm=offset)
        # Full-board exports include native filled-zone endpoint evidence.
        # Partial geometry fixtures can omit it when testing individual bends.
        if 'endpoint_zone_contacts' in data:
            for end in ('a', 'b'):
                node = Point(t[end])
                if contact is not None and contact.buffer(TOL).covers(node):
                    continue
                if any(int(j) != i and (tracks[int(j)]['net'], tracks[int(j)]['layer']) == (t['net'], t['layer'])
                       and lines[int(j)].distance(node) <= TOL for j in tree.query(node.buffer(TOL))):
                    continue
                if end in data['endpoint_zone_contacts'].get(t['id'], []):
                    zone_entries += 1
                else:
                    record('unjoined_endpoints', i, at_mm=t[end])

    for key, pair in adjacency.items():
        if len(pair) != 2:
            continue  # Branch geometry is checked separately below.
        (i, a), (j, b) = pair
        node = Point(key[2:])
        contact = contacts.get(key[:2])
        if contact is not None and contact.buffer(TOL).covers(node):
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
    branches=[]
    for junction in branch_junctions(data):
        ids=junction['indices'];contact=contacts.get((junction['net'],junction['layer']))
        w=max(tracks[i]['width'] for i in ids)
        if contact is not None and contact.buffer(TOL).covers(Point(junction['at_mm'])):continue
        branches.append(junction)
        if junction['interior_indices']:
            record('implicit_free_junctions',*ids,at_mm=junction['at_mm'])
        sectors=sorted(junction['sectors_deg'])
        if sectors not in ([90,135,135],[90,90,90,90]):
            record('unchamfered_free_branches',*ids,at_mm=junction['at_mm'],sectors_deg=junction['sectors_deg'])
    # Widths are checked per segment, and free width-change junctions need a
    # location-specific engineering reason. Pad/via contact changes are normal.
    widths = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0.0]))
    transitions = []
    approvals = (width_policy or {}).get('free_transitions', [])
    used_approvals = set()
    for i, t in enumerate(tracks):
        row = widths[t['net']][t['width']]
        row[0] += 1
        row[1] += lines[i].length
        if width_policy is not None:
            spec = width_policy['nets'].get(t['net'], width_policy['default'])
            allowed = spec.get('layers', {}).get(str(t['layer']), spec['widths_mm'])
            if not any(abs(t['width']-w) <= TOL for w in allowed):
                record('unreviewed_track_width', i, width_mm=t['width'], allowed_mm=allowed)
    for key, group in sorted(adjacency.items()):
        ids = sorted({i for i, _ in group})
        ww = sorted({tracks[i]['width'] for i in ids})
        if len(ww) < 2:
            continue
        node = Point(key[2:]); contact = contacts.get(key[:2])
        local = contact is not None and contact.buffer(max(ww)/2+TOL).covers(node)
        reason = 'Pad/via contact between separately sized branches.' if local else None
        for number, approval in enumerate(approvals):
            if (approval['net'], approval['layer']) == key[:2] and math.dist(approval['at_mm'], key[2:]) <= TOL and approval['widths_mm'] == ww:
                reason = approval['reason']; used_approvals.add(number)
        if width_policy is not None and not local and not reason:
            record('unreviewed_width_transition', *ids, at_mm=list(key[2:]), widths_mm=ww)
        transitions.append(dict(net=key[0], layer=key[1], at_mm=list(key[2:]), widths_mm=ww,
                                tracks=[tracks[i]['id'] for i in ids], at_contact=local, reason=reason))
    for number, approval in enumerate(approvals):
        if number not in used_approvals:
            issues['stale_width_approval'].append(approval)
    inventory = []
    for net, rows in sorted(widths.items()):
        spec = (width_policy or {}).get('nets', {}).get(net, (width_policy or {}).get('default', {}))
        inventory.append(dict(net=net, widths=[dict(width_mm=w, segments=v[0], length_mm=v[1]) for w,v in sorted(rows.items())],
                              reason=spec.get('reason', 'Width policy not supplied.')))
    pad_contacts = pad_contact_audit(data)
    if pad_contacts['incidental_contacts']:
        issues['incidental_pad_contacts'].extend(pad_contacts['incidental_contacts'])
    return dict(result='FAIL' if issues else 'PASS', segments=len(tracks), vias=len(data['vias']),
                rules=dict(direction_tolerance_mm=TOL, minimum_free_segment_mm=MIN_FREE_SEGMENT,
                           minimum_free_bend_included_angle_deg=135, curved_tracks_allowed=False,
                           free_three_way_branch_sectors_deg=[90,135,135],explicit_free_junction_endpoints=True),
                free_branch_junctions=len(branches),
                endpoint_gate_enforced='endpoint_zone_contacts' in data,
                filled_zone_entries=zone_entries,
                short_contact_segments=contact_segments, findings=dict(issues),
                pad_contact_audit=pad_contacts,
                width_audit=dict(policy_enforced=width_policy is not None, routed_nets=len(widths),
                                 segments_checked=len(tracks), nets=inventory, transitions=transitions,
                                 free_transitions=sum(not t['at_contact'] for t in transitions),
                                 scope='All segment widths and shared-endpoint width transitions. Different widths at pad/via contacts are intentional branch sizing; net reasons cover routes on different layers. Electrical load and copper-drop limits are checked separately.'),
                scope='Routing geometry only. Copper round end caps are normal; no curved centerlines. '
                      'Pad/via contacts allow local transitions; free branches require explicit nodes and chamfered geometry. '
                      'Native DRC and independent Gerber connectivity/clearance must also pass.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', type=Path, default=R/'hardware/FRC_Sensor_CAN.kicad_pcb')
    parser.add_argument('--output', type=Path, default=R/'reports/routing_rules.json')
    args = parser.parse_args()
    raw = subprocess.check_output(['kicad-python', str(R/'scripts/export_routing_geometry.py'), str(args.board)], text=True)
    policy_path = R/'hardware/design/routing_widths.json'
    report = inspect(json.loads(raw), json.loads(policy_path.read_text()))
    report['board_sha256'] = hashlib.sha256(args.board.read_bytes()).hexdigest()
    report['source_hashes'] = {p: hashlib.sha256((R/p).read_bytes()).hexdigest()
                              for p in ['scripts/check_routing.py', 'scripts/export_routing_geometry.py',
                                        'hardware/design/routing_widths.json']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], 'routing rules:', {k:len(v) for k,v in report['findings'].items()},
          f"({report['segments']} segments, {report['vias']} vias)")
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
