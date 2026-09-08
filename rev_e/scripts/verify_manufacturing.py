"""Independent Gerbonara parsing of exported copper, drills and assembly data.

Checks X2 pad identities/nets/coordinates against a separate pcbnew manifest.
This complements KiCad DRC; it is not a fabrication-house CAM approval.
"""
from pathlib import Path
from collections import Counter
import csv
import json
import warnings
import cairosvg
from gerbonara import LayerStack
from gerbonara.graphic_objects import Flash

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'reports/manufacturing/board_manifest.json').read_text())
parts = json.loads((ROOT / 'hardware/design/circuit.json').read_text())['parts']
with warnings.catch_warnings(record=True) as parser_warnings:
    warnings.simplefilter('always')
    stack = LayerStack.open(ROOT / 'output/fabrication')
    # Force lazy parsing while warnings are captured.
    for layer in list(stack.graphic_layers.values()) + list(stack.drill_layers):
        _ = layer.instance.objects
expected_layers = {(side, use) for side in ('top', 'bottom') for use in ('copper', 'mask', 'silk', 'paste')}
expected_layers.update({('mechanical','outline'),('inner_1','copper'),('inner_2','copper')})
assert set(stack.graphic_layers) == expected_layers
outline = stack.outline.instance.objects
assert len(outline) == 4
corners = {(round(o.x1, 6), round(o.y1, 6)) for o in outline}
assert corners == {(0, 0), (52, 0), (52, -70), (0, -70)}

def coord(value):
    return round(float(value), 5)

expected_drills = Counter((coord(d['x_mm']), coord(d['y_mm']), coord(d['diameter_mm']), d['plated'])
                          for d in manifest['drills'])
actual_drills = Counter()
for plated, layer in ((True, stack.drill_pth), (False, stack.drill_npth)):
    assert layer is not None
    for obj in layer.instance.objects:
        assert isinstance(obj, Flash), 'Unexpected routed slot in round-hole board'
        actual_drills[(coord(obj.x), coord(obj.y), coord(obj.aperture.diameter), plated)] += 1
# KiCad's decimal Excellon export quantizes coordinates to 0.001 mm. Match
# within half that unit instead of demanding false sub-micron precision.
unmatched = list(expected_drills.elements())
drill_error = 0.0
diameter_error = 0.0
for got in actual_drills.elements():
    candidates = [(i, exp) for i, exp in enumerate(unmatched)
                  if got[3] == exp[3] and abs(got[2]-exp[2]) <= .000501 and abs(got[0]-exp[0]) <= .000501 and abs(got[1]-exp[1]) <= .000501]
    assert len(candidates) == 1, ('Unmatched/ambiguous drill', got, candidates)
    i, exp = candidates[0]
    drill_error = max(drill_error, abs(got[0]-exp[0]), abs(got[1]-exp[1]))
    diameter_error = max(diameter_error, abs(got[2]-exp[2]))
    unmatched.pop(i)
assert not unmatched
assert sum(n for k, n in actual_drills.items() if not k[-1]) == 5

pad_results = {}
for side in ('top', 'bottom'):
    expected = Counter()
    for c in manifest['components']:
        if c['reference'].startswith('H'):
            continue
        for pad in c['pads']:
            if pad['copper_' + side]:
                expected[(c['reference'], pad['number'], coord(pad['x_mm']), coord(pad['y_mm']), pad['net'])] += 1
    actual = Counter()
    for obj in stack[(side, 'copper')].instance.objects:
        if isinstance(obj, Flash) and '.P' in obj.attrs:
            ref, pin, *_ = obj.attrs['.P']
            net = obj.attrs.get('.N', ('',))[0]
            if net == 'N/C':
                net = ''
            actual[(ref, pin, coord(obj.x), coord(obj.y), net)] += 1
    assert actual == expected, (side, actual - expected, expected - actual)
    pad_results[side] = sum(actual.values())

placed = list(csv.DictReader((ROOT / 'output/assembly/positions_all_top.csv').open()))
by_ref = {c['reference']: c for c in manifest['components']}
purchased = {r['reference'] for r in csv.DictReader((ROOT / 'bom/BOM_per_reference.csv').open())}
assert purchased == {r for r, p in parts.items() if not p.get('exclude_bom')}
assert purchased <= {r['Ref'] for r in placed}
for row in placed:
    c = by_ref[row['Ref']]
    assert row['Val'] == c['value'] and row['Package'] == c['package']
    assert coord(row['PosX']) == coord(c['x_mm']) and coord(row['PosY']) == coord(c['y_mm'])
    assert abs((float(row['Rot']) - c['rotation_deg'] + 180) % 360 - 180) < 1e-5
    assert row['Side'] == 'top'
assert len(stack[('bottom', 'paste')].instance.objects) == 0

# Copper-only previews avoid ambiguous solder-mask polarity and unsupported SVG filters.
for side in ('top', 'bottom'):
    svg = str(stack.to_svg(side_re=f'{side}|mechanical', margin=1,
                          colors={f'{side} copper': '#195c44', 'mechanical outline': '#222222',
                                  'drill pth': '#ffffff', 'drill npth': '#ffffff'}))
    dest = ROOT / f'output/review/gerber_{side}_copper.svg'
    dest.write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(dest.with_suffix('.png')),
                    output_width=1600, background_color='white')
result = dict(result='PASS', parser='Gerbonara 1.6.3', graphic_layers=11,
              board_outline_mm=[52, 70], plated_drills=sum(n for k, n in actual_drills.items() if k[-1]),
              nonplated_drills=5, copper_pad_flashes_verified=pad_results,
              maximum_drill_coordinate_quantization_mm=drill_error,
              maximum_drill_diameter_quantization_mm=diameter_error,
              assembly_rows_verified=len(placed), purchased_references_verified=len(purchased),
              portable_models_verified=manifest['models_resolved'],
              parser_warnings=sorted({str(w.message) for w in parser_warnings}),
              limitations='X2 pad/net/coordinate and drill/placement parity; not a copper connectivity solver or fabrication-house CAM review.')
(ROOT / 'reports/manufacturing/verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'parser_warnings'}, indent=2))
