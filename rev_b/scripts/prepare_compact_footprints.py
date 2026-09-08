from pathlib import Path
import json,shutil,re,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'hardware/design'))
from circuit import PARTS
base=Path('/home/neuro/.local/share/candi-tools/kicad/AppDir/share/kicad');out=ROOT/'hardware/library/FRC_Sensor_CAN.pretty'
for c in PARTS.values():
 lib,name=c['source_footprint'].split(':')
 if lib=='FRC_Sensor_CAN' or (out/(name+'.kicad_mod')).exists():continue
 t=(base/'footprints'/(lib+'.pretty')/(name+'.kicad_mod')).read_text()
 for old in re.findall(r'\$\{KICAD10_3DMODEL_DIR\}/([^"\n]+)',t):
  src=base/'3dmodels'/old
  if src.exists():shutil.copyfile(src,ROOT/'hardware/library/3d'/src.name);t=t.replace('${KICAD10_3DMODEL_DIR}/'+old,'${KIPRJMOD}/library/3d/'+src.name)
 (out/(name+'.kicad_mod')).write_text(t)
def start(name,attr='smd'):
 return f'(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr {attr})\n(fp_text reference "REF**" (at 0 -4) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))\n'
def rect(x1,y1,x2,y2,layer):return f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width .05) (type solid)) (fill none) (layer "{layer}"))\n'
for n in [2,3]:
 name=f'Weidmuller_LSF_135_{n}P';t=start(name,'through_hole');x2=(n-1)*3.5+2.1
 t+=rect(-2.1,-4.6,x2,8.1,'F.Fab')+rect(-2.35,-4.85,x2+.25,8.35,'F.CrtYd')
 for i in range(n):
  for y in [0,5]:t+=f'(pad "{i+1}" thru_hole {"rect" if i==0 else "circle"} (at {i*3.5} {y}) (size 2.1 2.1) (drill 1.1) (layers "*.Cu" "*.Mask"))\n'
 t+=')\n';(out/(name+'.kicad_mod')).write_text(t)
name='Pogo_2x5_1.27mm';t=start(name);t+=rect(-2.75,-1,4.02,6.08,'F.CrtYd')
for row in range(5):
 for col in range(2):t+=f'(pad "{row*2+col+1}" smd circle (at {col*1.27} {row*1.27}) (size .85 .85) (layers "F.Cu" "F.Mask") (solder_mask_margin .05))\n'
# Two 1 mm alignment holes, asymmetric in Y to orient the fixture.
for x,y in [(-2,0),(3.27,5.08)]:t+=f'(pad "" np_thru_hole circle (at {x} {y}) (size 1 1) (drill 1) (layers "*.Cu" "*.Mask"))\n'
t+=')\n';(out/(name+'.kicad_mod')).write_text(t)
name='Bourns_SRP4020TA';t=start(name);t+=rect(-2.225,-2.03,2.225,2.03,'F.Fab')+rect(-2.85,-2.4,2.85,2.4,'F.CrtYd')
for pin,x in [(1,-1.85),(2,1.85)]:t+=f'(pad "{pin}" smd rect (at {x} 0) (size 1.5 2.4) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
t+=')\n';(out/(name+'.kicad_mod')).write_text(t)
print('Prepared compact footprints; manufacturer geometry and pogo dimensions need independent review.')
