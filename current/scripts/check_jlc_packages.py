"""Bind the manufacturer package review to native pads, BOM and both-side CPL.

Run with kicad-python. This checks reviewed geometry, not factory process approval.
The normalized pad records in the review were compared with manufacturer drawings.
"""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import itertools
import json
import math
import pcbnew as p

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--board', type=Path, default=R/'hardware/FRC_Sensor_CAN.kicad_pcb')
ap.add_argument('--output', type=Path, default=R/'reports/manufacturing/jlc_packages.json')
args = ap.parse_args()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
review = json.loads((R/'bom/jlc_package_review.json').read_text())
plan = json.loads((R/'bom/assembly_plan.json').read_text())
model = json.loads((R/'hardware/design/circuit.json').read_text())['parts']
assert sha(args.board) == review['board_sha256'], 'Changed PCB needs a renewed package/spacing review'
assert sha(R/review['drawing_bundle']) == review['drawing_bundle_sha256']
assert plan['factory_service'] == 'JLCPCB Standard PCBA, both sides'
bom = list(csv.DictReader((R/'bom/BOM_JLCPCB.csv').open()))
cpl = list(csv.DictReader((R/'output/assembly/CPL_JLCPCB.csv').open()))
assert len(bom) == len(review['parts']) == 54
expected = {ref: row for row in review['parts'] for ref in row['references']}
assert len(expected) == sum(len(row['references']) for row in review['parts']) == 129
assert len(cpl) == len({row['Designator'] for row in cpl}) == 129
assert {row['Designator'] for row in cpl} == set(expected)
assert not set(expected) & set(plan['hand_solder_references'])
for row in bom:
    refs = [ref.strip() for ref in row['Designator'].split(',')]
    reviewed = expected[refs[0]]
    assert set(refs) == set(reviewed['references'])
    assert row['Comment'] == reviewed['mpn']
    assert row['LCSC Part #'] == reviewed['lcsc']

b = p.LoadBoard(str(args.board))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
placements = {row['Designator']: row for row in cpl}
sides = collections.Counter()
envelopes = {}
minimum_pad_gap = None
for ref, row in expected.items():
    fp = fps[ref]
    package = str(fp.GetFPID().GetLibItemName())
    assert package == row['footprint']
    assert model[ref]['mpn'] == row['mpn']
    assert model[ref]['footprint'].split(':')[-1] == package
    x, y = p.ToMM(fp.GetPosition().x), p.ToMM(fp.GetPosition().y)
    angle = fp.GetOrientationDegrees()
    side = 'Bottom' if fp.IsFlipped() else 'Top'
    sides[side] += 1
    pos = placements[ref]
    assert pos['Layer'] == side
    assert abs(float(pos['Mid X'].removesuffix('mm'))-x) < 1e-5
    assert abs(float(pos['Mid Y'].removesuffix('mm'))-(-y)) < 1e-5
    assert abs((float(pos['Rotation'])-angle+180) % 360-180) < 1e-5
    assert abs(angle/90-round(angle/90)) < 1e-6
    definition = review['reviewed_footprints'][package]
    sx, sy = definition['screen_envelope_xy_mm']
    if round(angle/90) % 2:
        sx, sy = sy, sx
    envelopes[ref] = (side, x-sx/2, y-sy/2, x+sx/2, y+sy/2)
    # Normalize in memory only; never save the altered board.
    if fp.IsFlipped():
        fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(0)
    fp.SetPosition(p.VECTOR2I(0, 0))
    actual = []
    for pad in fp.Pads():
        actual.append(dict(n=pad.GetNumber(),
            xy=[p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)],
            size=[p.ToMM(pad.GetSize().x), p.ToMM(pad.GetSize().y)],
            rot=pad.GetOrientationDegrees(), copper=pad.IsOnLayer(p.F_Cu),
            paste=pad.IsOnLayer(p.F_Paste),
            drill=[p.ToMM(pad.GetDrillSize().x), p.ToMM(pad.GetDrillSize().y)]))
        if pad.GetNumber():
            assert pad.GetNetname() == (model[ref]['pins'][pad.GetNumber()] or ''), ref
    assert actual == definition['pads'], (ref, 'pad geometry changed from drawing review')
    for a, z in itertools.combinations([v for v in actual if v['copper']], 2):
        dx = max(0, abs(a['xy'][0]-z['xy'][0])-(a['size'][0]+z['size'][0])/2)
        dy = max(0, abs(a['xy'][1]-z['xy'][1])-(a['size'][1]+z['size'][1])/2)
        distance = math.hypot(dx, dy)
        record = (distance, ref, a['n'], z['n'])
        if minimum_pad_gap is None or record < minimum_pad_gap:
            minimum_pad_gap = record
assert sides == {'Top': 50, 'Bottom': 79}
gaps = []
for (a, va), (z, vz) in itertools.combinations(envelopes.items(), 2):
    if va[0] != vz[0]:
        continue
    dx = max(va[1]-vz[3], vz[1]-va[3], 0)
    dy = max(va[2]-vz[4], vz[2]-va[4], 0)
    assert dx > 0 or dy > 0, (a, z, 'component envelopes overlap')
    gaps.append((math.hypot(dx, dy), a, z))
edge = sorted((min(v[1], v[2], 44-v[3], 48-v[4]), ref) for ref, v in envelopes.items())
assert edge[0][0] > 0
paths = ['bom/jlc_package_review.json', review['drawing_bundle'], 'bom/assembly_plan.json',
         'bom/BOM_JLCPCB.csv', 'output/assembly/CPL_JLCPCB.csv',
         'hardware/design/circuit.json', 'scripts/check_jlc_packages.py']
result = dict(result='PASS package and placement-file checks; factory process approval pending',
    board_sha256=sha(args.board), exact_mpn_types=54, factory_placements=129,
    footprint_families=len(review['reviewed_footprints']), placements_by_side=dict(sides),
    all_reviewed_pads_match=True, all_native_pin_nets_match_model=True,
    cpl_matches_native_positions_sides_rotations=True,
    closest_same_side_envelopes_mm=sorted(gaps)[:10], closest_edge_envelopes_mm=edge[:10],
    minimum_within_footprint_pad_gap_mm=minimum_pad_gap,
    factory_holds=review['factory_holds'], limitations=review['limitations'],
    input_hashes={name:sha(R/name) for name in paths})
args.output.write_text(json.dumps(result, indent=2)+'\n')
print(result['result'])
print('Closest envelopes:', sorted(gaps)[:3], '; minimum pad gap:', minimum_pad_gap)
