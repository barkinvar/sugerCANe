"""Check retained front artwork and clearances after the drilling/stack revision."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import pcbnew as p
from apply_compact_easteregg import ROOT, PIXEL, WORD_PIXEL, payload, rectangles, wordmark_rectangles

BASELINE = '156d7dd'
board_path = ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'
current = board_path.read_text()
art = payload()
assert current.count(art) == 1
before = subprocess.check_output(
    ['git', 'show', BASELINE + ':current/hardware/FRC_Sensor_CAN.kicad_pcb'], cwd=ROOT)
assert before.decode().count(art)==1,'Artwork differs from the reviewed pixel-cane revision'
fabrication=json.loads((ROOT/'reports/manufacturing/fabrication_options.json').read_text())
assert fabrication['board_sha256']==hashlib.sha256(board_path.read_bytes()).hexdigest()
assert fabrication['result']=='PASS limited fabrication change and DC allowances'
board = p.LoadBoard(str(board_path))


def bounds(item):
    bb = item.GetBoundingBox()
    x, y = p.ToMM(bb.GetPosition())
    w, h = p.ToMM(bb.GetSize())
    return x, y, x + w, y + h


def distance(a, b):
    return math.hypot(max(a[0] - b[2], b[0] - a[2], 0),
                      max(a[1] - b[3], b[1] - a[3], 0))


obstacles = []
for via in board.GetTracks():
    if isinstance(via, p.PCB_VIA):
        # Keep ink off via annuli too, even when mask-tented. A tent is not a
        # filled/planarized hole and can leave a visible pit in the wordmark.
        x, y = p.ToMM(via.GetPosition())
        radius = p.ToMM(via.GetWidth(p.F_Cu))/2
        obstacles.append(('via ' + via.m_Uuid.AsString(), (x-radius, y-radius, x+radius, y+radius)))
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        if pad.IsOnLayer(p.F_Mask) or any(pad.GetDrillSize()):
            # Bounding boxes conservatively include rounded corners. Expand
            # by the actual board/footprint/pad solder-mask opening margin.
            margin = max(0, p.ToMM(pad.GetSolderMaskExpansion(p.F_Mask)))
            x0, y0, x1, y1 = bounds(pad)
            obstacles.append((ref + '.' + pad.GetNumber() + ' mask/drill',
                              (x0-margin, y0-margin, x1+margin, y1+margin)))
    if fp.IsFlipped():
        continue
    for g in fp.GraphicalItems():
        if g.GetLayer() in (p.F_CrtYd, p.F_SilkS):
            obstacles.append((ref + ' ' + g.GetLayerName(), bounds(g)))
    for g in (fp.Reference(), fp.Value()):
        if g.IsVisible() and g.GetLayer() == p.F_SilkS:
            obstacles.append((ref + ' text', bounds(g)))
for g in board.GetDrawings():
    if g.GetLayer() == p.F_SilkS and g.m_Uuid.AsString() not in art:
        obstacles.append(('existing front marking', bounds(g)))
    elif g.GetLayer() == p.Edge_Cuts:
        obstacles.append(('board edge', bounds(g)))
all_rectangles = rectangles() + wordmark_rectangles()
art_to_wordmark = min(distance(a, b) for a in rectangles() for b in wordmark_rectangles())
assert art_to_wordmark >= .20, 'Wordmark overlaps the cane illustration'
nearest = sorted((min(distance(rect, bb) for rect in all_rectangles), label)
                 for label, bb in obstacles)
assert nearest[0][0] >= .20, ('Artwork clearance below 0.20 mm', nearest[0])
unchanged_fabrication = {}
for path in sorted((ROOT/'output/fabrication').iterdir()):
    if path.suffix not in ('.gtp', '.gbp', '.gts', '.gbs', '.gbo', '.gto', '.gm1'):
        continue
    relative = str(path.relative_to(ROOT))
    original = subprocess.check_output(['git', 'show', BASELINE + ':current/' + relative], cwd=ROOT)
    def geometry(data):
        return b'\n'.join(line for line in data.splitlines() if not line.startswith((b'%TF.CreationDate,',b'G04 Created by KiCad')))
    assert geometry(path.read_bytes()) == geometry(original), ('Mask/paste/silk/outline geometry changed', relative)
    unchanged_fabrication[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
report = dict(result='PASS', baseline_commit=BASELINE,
              board_sha256=hashlib.sha256(board_path.read_bytes()).hexdigest(),
              baseline_board_sha256=hashlib.sha256(before).hexdigest(),
              artwork_unchanged=True,non_artwork_change_review='reports/manufacturing/fabrication_options.json',
              layer='F.Silkscreen', pixel_mm=PIXEL, rectangles=len(rectangles()),
              wordmark=dict(text='sugarCANe', rotation_degrees=90, pixel_mm=WORD_PIXEL,
                            location='Left of C1; reads bottom to top', rectangles=len(wordmark_rectangles()),
                            bounds_mm=[min(a[0] for a in wordmark_rectangles()), min(a[1] for a in wordmark_rectangles()),
                                       max(a[2] for a in wordmark_rectangles()), max(a[3] for a in wordmark_rectangles())]),
              artwork_bounds_mm=[min(a[0] for a in rectangles()), min(a[1] for a in rectangles()),
                                 max(a[2] for a in rectangles()), max(a[3] for a in rectangles())],
              minimum_required_clearance_mm=.20,
              illustration_to_wordmark_clearance_mm=art_to_wordmark,
              unchanged_fabrication_files=unchanged_fabrication,
              closest_obstacles=[dict(clearance_mm=d, item=label) for d, label in nearest[:12]],
              scope='Conservative native bounding-box artwork clearance. Native copper and artwork retained under the fabrication-options audit; exported mask/paste/silk/outline retained except timestamps. Refilled Gerber zone outlines may differ in numerical rounding. Drill diameters and nominal stack changed under the separate fabrication-options audit.',
              input_hashes={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in [Path(__file__), ROOT/'scripts/apply_compact_easteregg.py',
                                         ROOT/'hardware/artwork/compact-pixel-cane.svg',ROOT/'reports/manufacturing/fabrication_options.json']})
(ROOT/'reports/compact/easteregg.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS retained pixel-cane artwork; nearest clearance', nearest[0], '; separate drill/stack audit verified')
