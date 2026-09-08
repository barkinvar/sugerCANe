"""Set the nominal fabrication stack and title; do not change copper geometry.

The dielectric entries are an order target, not an approved vendor stackup or
measured material property. Native thickness includes nominal solder masks.
"""
from pathlib import Path
import sexpdata as sx
R=Path(__file__).resolve().parents[1];p=R/'hardware/FRC_Sensor_CAN.kicad_pcb';tree=sx.loads(p.read_text())
def tag(x):return str(x[0]) if isinstance(x,list) and x else ''
setup=next(x for x in tree if tag(x)=='setup');setup[:]=[x for x in setup if tag(x)!='stackup']
setup.insert(1,sx.loads('''(stackup
 (layer "F.Silkscreen" (type "Top Silk Screen") (color "White"))
 (layer "F.Paste" (type "Top Solder Paste"))
 (layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "prepreg") (thickness 0.2) (material "FR4"))
 (layer "In1.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 2" (type "core") (thickness 1.04) (material "FR4"))
 (layer "In2.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 3" (type "prepreg") (thickness 0.2) (material "FR4"))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
 (layer "B.Paste" (type "Bottom Solder Paste"))
 (layer "B.Silkscreen" (type "Bottom Silk Screen") (color "White"))
 (copper_finish "ENIG") (dielectric_constraints no))'''))
tree[:]=[x for x in tree if tag(x)!='title_block']
tree.insert(5,sx.loads('''(title_block (title "SC12 regulated sensor-to-CAN")
 (date "2026-09-08") (rev "D") (company "FRC Sensor CAN project")
 (comment 1 "Engineering prototype - physical qualification pending")
 (comment 2 "52 x 64 mm; 4-layer; nominal 1.6 mm; supplier stackup review required"))'''))
p.write_text(sx.dumps(tree)+'\n')
print('Nominal 4-layer 1.6 mm ENIG stack and Rev D identity saved.')
