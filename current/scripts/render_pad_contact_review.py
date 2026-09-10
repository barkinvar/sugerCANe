"""Record the full-board contact sweep and render the additional Q1 repair."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolygonPatch
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from check_routing import pad_contact_audit

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'
BASELINE = '4f238f9856be0e8ce036d0285594219fe225b4d0'
sha = lambda data: hashlib.sha256(data).hexdigest()


def geometry(path):
    return json.loads(subprocess.check_output(
        ['kicad-python', str(ROOT / 'scripts/export_routing_geometry.py'), str(path)]))


baseline = subprocess.check_output(['git', 'show', BASELINE + ':current/hardware/FRC_Sensor_CAN.kicad_pcb'], cwd=ROOT)
with tempfile.NamedTemporaryFile(suffix='.kicad_pcb') as before:
    before.write(baseline); before.flush()
    old, new = geometry(before.name), geometry(BOARD)
before_audit, after_audit = pad_contact_audit(old), pad_contact_audit(new)
assert len(before_audit['incidental_contacts']) == 2
assert {(p['reference'], p['pad']) for p in before_audit['incidental_contacts']} == {('Q1', '2')}
assert not after_audit['incidental_contacts']
assert old['pads'] == new['pads'] and old['vias'] == new['vias']
old_tracks = {t['id']:t for t in old['tracks']}
new_tracks = {t['id']:t for t in new['tracks']}
assert set(old_tracks) == set(new_tracks)
changes = [dict(before=old_tracks[uid], after=t) for uid,t in new_tracks.items() if t != old_tracks[uid]]
assert {c['after']['id'] for c in changes} == {'51587d46-cccf-47f3-ae44-edc0c1ff0629', 'cc4fb95b-8cda-4333-9ea0-7ba3260f8dcb'}
assert all(c[side]['net'] == 'VIN_PROT' and c[side]['width'] == .8 and c[side]['layer'] == 2
           for c in changes for side in ('before', 'after'))

fig, axes = plt.subplots(1, 2, figsize=(12, 7))
area = box(24.6, 3.8, 29.0, 8.1)
for ax, data, title in zip(axes, (old, new), ('Before: branch grazes Q1 pin 2', 'After: branch enters pin 3 directly')):
    def draw(poly, color):
        ax.add_patch(PolygonPatch([(x,-y) for x,y in poly.exterior.coords], facecolor=color, edgecolor='none'))
    for pad in data['pads']:
        if pad['layer'] == 2:
            for points in pad['polygons']:
                poly = Polygon(points)
                if poly.intersects(area):
                    draw(poly, '#b2b7ba')
    for t in data['tracks']:
        if t['layer'] == 2:
            poly = LineString([t['a'],t['b']]).buffer(t['width']/2, quad_segs=64)
            if poly.intersects(area):
                draw(poly, '#d77b00' if t['net'] == 'VIN_PROT' else '#728c9b')
    for v in data['vias']:
        if Point(v['at']).intersects(area):
            draw(Point(v['at']).buffer(v['width']/2), '#d77b00' if v['net'] == 'VIN_PROT' else '#728c9b')
    for pad in data['pads']:
        if pad['layer'] == 2 and pad['ref'] == 'Q1' and area.contains(Point(pad['at'])):
            ax.text(pad['at'][0],-pad['at'][1], 'Q1.'+pad['number'], ha='center',va='center',fontsize=10,weight='bold')
    ax.set(xlim=(29,24.6),ylim=(-8.1,-3.8),xlabel='Board X (mm)',ylabel='Gerber Y (mm)',title=title)
    ax.set_aspect('equal'); ax.grid(alpha=.2)
fig.suptitle('Full-board pad-contact sweep | Q1 bottom copper repair', fontsize=16, weight='bold')
fig.text(.5,.04,'Orange: VIN_PROT. Gray: other copper. Zones, mask and drill holes omitted.',ha='center',fontsize=9)
fig.text(.5,.018,'Both modified segments retain 0.80 mm width. All four copper layers pass the contact scan.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.06,1,.94))
output = ROOT / 'output/review/pad_contact_sweep.png'
fig.savefig(output,dpi=200); plt.close(fig)

pin2 = union_all([Polygon(q) for p in new['pads'] if p['ref']=='Q1' and p['number']=='2' and p['layer']==2 for q in p['polygons']])
gap = min(LineString([c['after']['a'],c['after']['b']]).buffer(.4,quad_segs=64).distance(pin2) for c in changes)
assert gap >= .2
sources = ['hardware/FRC_Sensor_CAN.kicad_pcb','scripts/check_routing.py','scripts/export_routing_geometry.py','scripts/render_pad_contact_review.py']
report = dict(result='PASS',baseline_commit=BASELINE,baseline_board_sha256=sha(baseline),
              board_sha256=sha(BOARD.read_bytes()),before=before_audit,after=after_audit,
              changed_tracks=changes,pads_and_vias_unchanged=True,all_other_tracks_unchanged=True,
              corrected_locations=[dict(reference='Q1',pad='2',layer='B.Cu',gerber_xy_mm=[27.36,-5.5],incidental_contacts_removed=2)],
              repaired_branch_to_q1_pin2_clearance_mm=gap,
              input_hashes={p:sha((ROOT/p).read_bytes()) for p in sources},
              output=str(output.relative_to(ROOT)),output_sha256=sha(output.read_bytes()),
              limitations='Native pad/track geometry screen. Connected approach bends are intentional; native DRC, exported copper checks, DC analysis and physical qualification remain separate.')
(ROOT/'reports/compact/pad_contact_sweep.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS full-board contact sweep:',after_audit['pad_layer_shapes_checked'],'pad/layer shapes;',
      after_audit['same_net_contact_pairs_checked'],'same-net contact pairs; zero incidental contacts')
