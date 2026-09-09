"""Place official Weidmuller STEP geometry at the existing KiCad footprint origin.

The vendor files are retained byte-for-byte. Only a rigid translation and display
colors are applied; no terminal geometry or PCB copper is regenerated here.
"""
from pathlib import Path
import hashlib
import json
import cadquery as cq
import sexpdata as sx

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'hardware/library/3d'
ASSETS = {
    2: ('1824420000', 'dc89a9a9-9b30-4eea-8450-39e1e9e0f36c'),
    3: ('1824430000', '562b68f2-3a3e-486d-a2a8-09d71c1ba66a'),
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records = []
board = sx.loads((ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb').read_text())
def child(node, tag):
    return next((q for q in node if isinstance(q, list) and q and str(q[0]) == tag), None)

for count, (mpn, asset) in ASSETS.items():
    source = MODELS / 'vendor' / (mpn + '.stp')
    solids = cq.importers.importStep(str(source)).solids().vals()
    pins = [s for s in solids if s.BoundingBox().zmin < 0.01]
    assert len(solids) == 1 + count * 3 and len(pins) == count * 2
    centers = [(s.BoundingBox().center.x, s.BoundingBox().center.y) for s in pins]
    xs = sorted(set(round(x, 6) for x, y in centers))
    ys = sorted(set(round(y, 6) for x, y in centers))
    assert len(xs) == count and len(ys) == 2
    assert all(abs(xs[i] - xs[0] - i * 3.5) < 1e-5 for i in range(count))
    assert abs(ys[1] - ys[0] - 7) < 1e-5
    expected_pads = {(str(i + 1), i * 3.5, y, 1.1) for i in range(count) for y in (0, 7)}
    footprint_name = f'Weidmuller_LSF_90_{count}P'
    library = sx.loads((ROOT / 'hardware/library/FRC_Sensor_CAN.pretty' / (footprint_name + '.kicad_mod')).read_text())
    footprints = [library] + [q for q in board if isinstance(q, list) and q and str(q[0]) == 'footprint' and str(q[1]).endswith(':' + footprint_name)]
    assert len(footprints) == 4, 'Expected one library footprint and three placed connectors'
    for footprint in footprints:
        pads = {(str(q[1]), float(child(q, 'at')[1]), float(child(q, 'at')[2]), float(child(q, 'drill')[1]))
                for q in footprint if isinstance(q, list) and q and str(q[0]) == 'pad'}
        assert pads == expected_pads, 'Vendor pin pattern differs from PCB/library footprint'
        model = child(footprint, 'model')
        assert str(model[1]).endswith('/' + footprint_name + '.step')
        assert child(child(model, 'offset'), 'xyz')[1:] == [0, 0, 0]
        assert child(child(model, 'rotate'), 'xyz')[1:] == [0, 0, 0]
        assert child(child(model, 'scale'), 'xyz')[1:] == [1, 1, 1]
    # Vendor Z=0 is pin tip; PCB seating surface is Z=3.5 mm.
    # KiCad model +Y is opposite footprint +Y. Rear pin one becomes (0,0).
    translation = (-xs[0], -ys[1], -3.5)
    assembly = cq.Assembly(name=f'Weidmuller_{mpn}')
    for i, solid in enumerate(solids):
        kind = 'pin' if solid in pins else 'housing' if solid.Volume() > 100 else 'button'
        color = {'pin': (.72, .73, .75), 'housing': (.08, .08, .085),
                 'button': (.89, .89, .85)}[kind]
        assembly.add(solid.translate(translation), name=f'{kind}_{i}', color=cq.Color(*color))
    output = MODELS / f'Weidmuller_LSF_90_{count}P.step'
    assembly.export(str(output))
    transformed = cq.importers.importStep(str(output))
    bounds = transformed.val().BoundingBox()
    assert abs(bounds.zmin + 3.5) < 1e-5 and abs(bounds.zmax - 8.5) < 1e-5
    assert bounds.ymin >= -13.05 and bounds.ymax <= 1.7 + 1e-5
    assert bounds.xmin >= -2.35 and bounds.xmax <= (count - 1) * 3.5 + 2.35
    # Ensure every terminal intersects its intended 1.1 mm drill at PCB surface.
    fit = []
    for pin in pins:
        b = pin.translate(translation).BoundingBox()
        center = [round(b.center.x, 6), round(-b.center.y, 6)]
        radius = ((b.xlen / 2) ** 2 + (b.ylen / 2) ** 2) ** .5
        assert radius < .55
        fit.append({'pcb_local_xy_mm': center, 'pin_half_diagonal_mm': round(radius, 6)})
    records.append({
        'mpn': mpn, 'pole_count': count, 'source_file': str(source.relative_to(ROOT)),
        'source_url': f'https://assets.dam.weidmueller.com/assets/api/{asset}/Original/{mpn}.stp',
        'product_url': f'https://eshop.weidmueller.com/p/{mpn}',
        'retrieved_utc': '2026-09-08', 'vendor_sha256': digest(source),
        'model_file': str(output.relative_to(ROOT)), 'model_sha256': digest(output),
        'translation_mm': list(translation), 'rotation_deg': [0, 0, 0],
        'pole_pitch_mm': 3.5, 'pin_row_spacing_mm': 7, 'drill_mm': 1.1,
        'placed_connectors_checked': 3, 'native_and_library_pad_patterns_match': True,
        'seated_height_mm': 8.5, 'pins': fit,
        'bounds_mm': {v: [round(getattr(bounds, v+'min'), 6), round(getattr(bounds, v+'max'), 6)] for v in 'xyz'},
        'geometry': 'Manufacturer STEP, rigid translation only; original source retained.',
        'colors': 'Project display colors based on manufacturer black housing, white buttons and metal pins.',
        'limitations': 'Nominal CAD fit; vendor molding detail and tolerances may differ. Physical fit remains untested.',
    })
(MODELS / 'vendor_connectors.json').write_text(json.dumps(records, indent=2) + '\n')
print(json.dumps({'result': 'PASS', 'models': len(records), 'pin_centers_verified': sum(len(r['pins']) for r in records)}, indent=2))
