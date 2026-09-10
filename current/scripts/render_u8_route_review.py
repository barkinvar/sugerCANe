"""Compare the reviewed U8.5 corner-contact repair with its compact baseline."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolygonPatch
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'
BASELINE = 'fbb77cb4d89d5443efa965c6bbcddf3715804a42'
sha = lambda data: hashlib.sha256(data).hexdigest()


def geometry(path):
    return json.loads(subprocess.check_output(
        ['kicad-python', str(ROOT / 'scripts/export_routing_geometry.py'), str(path)]))


baseline = subprocess.check_output(['git', 'show', BASELINE + ':current/hardware/FRC_Sensor_CAN.kicad_pcb'], cwd=ROOT)
with tempfile.NamedTemporaryFile(suffix='.kicad_pcb') as before:
    before.write(baseline)
    before.flush()
    datasets = [geometry(before.name), geometry(BOARD)]

fig, axes = plt.subplots(1, 2, figsize=(12, 8))
area = box(28.2, 17.5, 34.1, 23.5)
for ax, data, title in zip(axes, datasets, ['Before: incidental pad-corner contact', 'After: centered pad connection']):
    def draw(poly, color):
        ax.add_patch(PolygonPatch([(x, -y) for x, y in poly.exterior.coords],
                                 facecolor=color, edgecolor='none'))
    for pad in data['pads']:
        if pad['layer'] == 2:
            for points in pad['polygons']:
                poly = Polygon(points)
                if poly.intersects(area):
                    draw(poly, '#b2b7ba')
    for track in data['tracks']:
        if track['layer'] != 2:
            continue
        poly = LineString([track['a'], track['b']]).buffer(track['width'] / 2, quad_segs=48)
        if poly.intersects(area):
            draw(poly, '#d77b00' if track['net'] == 'BOOST_SW' else '#728c9b')
    for via in data['vias']:
        if Point(via['at']).intersects(area):
            draw(Point(via['at']).buffer(via['width'] / 2), '#728c9b')
    for pad in data['pads']:
        if pad['layer'] == 2 and pad['ref'] in ('U8', 'D4') and area.contains(Point(pad['at'])):
            ax.text(pad['at'][0], -pad['at'][1], pad['ref'] + '.' + pad['number'],
                    ha='center', va='center', fontsize=8, weight='bold')
    ax.set(xlim=(34.1, 28.2), ylim=(-23.5, -17.5), xlabel='Board X (mm)', ylabel='Gerber Y (mm)', title=title)
    ax.set_aspect('equal')
    ax.grid(alpha=.2)
fig.suptitle('U8 switch-node routing | bottom view', fontsize=17, weight='bold')
fig.text(.5, .045, 'Orange: BOOST_SW. Gray: other pad/track/via copper. Zones, mask and drill holes omitted.', ha='center', fontsize=9)
fig.text(.5, .022, 'Native copper geometry; electrical clearance and exported Gerber checks are separate.', ha='center', fontsize=9)
fig.tight_layout(rect=(0, .065, 1, .95))
output = ROOT / 'output/review/u8_switch_route_fix.png'
fig.savefig(output, dpi=200)
plt.close(fig)

old, new = datasets
switch = [t for t in new['tracks'] if t['net'] == 'BOOST_SW']
foreign = [unary_union([Polygon(q) for q in p['polygons']]) for p in new['pads']
           if p['ref'] == 'U8' and p['net'] != 'BOOST_SW']
minimum = min(LineString([t['a'], t['b']]).buffer(t['width']/2, quad_segs=64).distance(p)
              for t in switch for p in foreign)
assert minimum >= .2 - 1e-6
report = dict(result='PASS', baseline_commit=BASELINE, baseline_board_sha256=sha(baseline),
              board_sha256=sha(BOARD.read_bytes()), location=dict(side='bottom', gerber_xy_mm=[32, -20], pad='U8.5', net='BOOST_SW'),
              change='Centered 0.30 mm pad connection replaces the incidental corner contact and parallel loop; diode leg widened to 0.50 mm; In2 ground-reference guard extended.',
              switch_track_length_before_mm=sum(LineString([t['a'], t['b']]).length for t in old['tracks'] if t['net']=='BOOST_SW'),
              switch_track_length_after_mm=sum(LineString([t['a'], t['b']]).length for t in switch),
              minimum_switch_trace_to_other_u8_pad_clearance_mm=minimum,
              input_hashes={p:sha((ROOT/p).read_bytes()) for p in ['hardware/FRC_Sensor_CAN.kicad_pcb', 'hardware/design/layout_contract.json', 'hardware/design/routing_widths.json', 'scripts/export_routing_geometry.py', 'scripts/render_u8_route_review.py']},
              output=str(output.relative_to(ROOT)), output_sha256=sha(output.read_bytes()),
              limitations='Nominal native copper review; no measured switching, thermal or EMC qualification. All independent release gates remain required.')
(ROOT / 'reports/compact/u8_route_fix.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS U8 repair review; minimum switch-trace clearance to other U8 pads:', round(minimum, 6), 'mm')
