"""Check the front artwork's clearances and exact non-artwork identity."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import pcbnew as p
from apply_compact_easteregg import ROOT, PIXEL, WORD_PIXEL, payload, rectangles, wordmark_rectangles

BASELINE = '69d38a0'
board_path = ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'
current = board_path.read_text()
art = payload()
assert current.count(art) == 1
before = subprocess.check_output(
    ['git', 'show', BASELINE + ':current/hardware/FRC_Sensor_CAN.kicad_pcb'], cwd=ROOT)
assert current.replace(art, '').encode() == before, 'Non-artwork native content changed'
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
    if path.suffix not in ('.gtl', '.gbl', '.g1', '.g2', '.gtp', '.gbp',
                           '.gts', '.gbs', '.gbo', '.gm1', '.drl', '.gbrjob'):
        continue
    relative = str(path.relative_to(ROOT))
    original = subprocess.check_output(['git', 'show', BASELINE + ':current/' + relative], cwd=ROOT)
    assert path.read_bytes() == original, ('Non-front-silkscreen fabrication file changed', relative)
    unchanged_fabrication[relative] = hashlib.sha256(original).hexdigest()
report = dict(result='PASS', baseline_commit=BASELINE,
              board_sha256=hashlib.sha256(board_path.read_bytes()).hexdigest(),
              baseline_board_sha256=hashlib.sha256(before).hexdigest(),
              non_artwork_native_content_byte_identical=True,
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
              scope='Conservative native bounding-box clearance to front courtyards, pad mask openings, holes, via annuli, existing silk and edges. Only added front silk and its locked groups; all original native content is byte-identical, including all four copper layers, zones, pads, vias, net assignments and stack.',
              input_hashes={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in [Path(__file__), ROOT/'scripts/apply_compact_easteregg.py',
                                         ROOT/'hardware/artwork/compact-pixel-cane.svg']})
(ROOT/'reports/compact/easteregg.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS pixel-cane artwork; nearest clearance', nearest[0], '; non-artwork PCB byte-identical')
