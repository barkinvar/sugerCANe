"""Create horizontal LSF-SMT /90 footprints and restore aligned manufacturer CAD.

Manufacturer pages 2/7: 3.5 mm pole pitch, 7 mm row spacing, 1.1 mm holes,
3.5 mm pins, 8.5 mm seated height. The tabulated depth is 14.75 mm whereas
the generic drawing says max 14 mm. Reserve the larger tabulated envelope.
Origin is the rear pin of pole 1; wire entry is toward PCB local +Y.
"""
from pathlib import Path
import json
import runpy

R = Path(__file__).resolve().parents[1]
library = R / 'hardware/library/FRC_Sensor_CAN.pretty'
models = R / 'hardware/library/3d'
records = []

for count, mpn in [(2, '1824420000'), (3, '1824430000')]:
    name = f'Weidmuller_LSF_90_{count}P'
    width = (count - 1) * 3.5 + 4.2
    xmax = (count - 1) * 3.5 + 2.1
    text = f'''(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu")
 (descr "Weidmuller {mpn}; horizontal wire entry +Y; 7mm pin-row spacing; 14.75mm reserved depth")
 (attr through_hole)
 (fp_text reference "REF**" (at 0 -3) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))
 (fp_rect (start -2.1 -1.7) (end {xmax} 13.05) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))
 (fp_rect (start -2.35 -1.95) (end {xmax+.25} 13.30) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd"))
'''
    for pole in range(count):
        for yy in [0, 7]:
            text += f'(pad "{pole+1}" thru_hole {"rect" if pole == 0 else "circle"} (at {pole*3.5} {yy}) (size 2.1 2.1) (drill 1.1) (layers "*.Cu" "*.Mask"))\n'
    text += f'(model "${{KIPRJMOD}}/library/3d/{name}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n)\n'
    (library / (name + '.kicad_mod')).write_text(text)
    records.append({'mpn': mpn, 'footprint': name, 'pole_pitch_mm': 3.5,
                    'row_spacing_mm': 7, 'hole_mm': 1.1, 'pin_length_mm': 3.5,
                    'width_mm': width, 'reserved_depth_mm': 14.75,
                    'seated_height_mm': 8.5, 'wire_entry': 'parallel to PCB, local +Y',
                    'source': f'https://datasheet.weidmueller.com/pdf/en/{mpn}/scope/1/',
                    'note': 'Drawing body 11.7 mm, rear pin offset 1.7 mm, front pin to front body 3 mm. Larger tabulated 14.75 mm total depth reserved. The model uses vendor STEP; see vendor_connectors.json for source and alignment.'})
(models / 'horizontal_connectors.json').write_text(json.dumps(records, indent=2) + '\n')
print('Created horizontal footprints for', [r['mpn'] for r in records])

runpy.run_path(str(R / 'scripts/import_connector_models.py'))
