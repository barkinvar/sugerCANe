#!/usr/bin/env python3
from pathlib import Path
import os,sys,re,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware/design'))
from circuit import PARTS,ROOT
base=Path(os.environ.get('CANDI_TOOLS_ROOT',Path.home()/'.local/share/candi-tools'))/'kicad/AppDir/share/kicad'
lib=ROOT/'hardware/library/FRC_Sensor_CAN.pretty'; lib.mkdir(parents=True,exist_ok=True)
models=ROOT/'hardware/library/3d'; models.mkdir(exist_ok=True)
manifest=[]
for src in sorted({p['source_footprint'] for p in PARTS.values()}):
    name,fp=src.split(':')
    if name=='FRC_Sensor_CAN':continue
    path=base/'footprints'/(name+'.pretty')/(fp+'.kicad_mod')
    txt=path.read_text()
    for match in re.findall(r'\$\{KICAD10_3DMODEL_DIR\}/([^"\n]+)',txt):
        model=base/'3dmodels'/match
        if model.is_file():
            dst=models/model.name; dst.write_bytes(model.read_bytes())
            txt=txt.replace('${KICAD10_3DMODEL_DIR}/'+match,'${KIPRJMOD}/library/3d/'+model.name)
        else:print('Missing optional model:',model)
    (lib/(fp+'.kicad_mod')).write_text(txt)
    manifest.append({'library_id':src,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'modification':'3D model path made project-relative only.'})

def header(name,descr,attr='smd'):
    return f'''(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu")
 (descr "{descr}") (attr {attr})
 (fp_text reference "REF**" (at 0 -4) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))
'''.rstrip()+''
# The header helper ends its reference text, not the footprint.
def hdr(name,descr,attr='smd'):
    return f'''(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu")
 (descr "{descr}") (attr {attr})
 (fp_text reference "REF**" (at 0 -4) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'''
# Remove only the footprint-closing parenthesis from this template.
def start(name,descr,attr='smd'):
    return hdr(name,descr,attr)+'\n'
def rectangle(x1,y1,x2,y2,layer,w=.15):
    return f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (fill none) (layer "{layer}"))\n'
for n in [2,3]:
    name=f'Wuerth_69113771000{n}'
    # Manufacturer drawing: pitch5.00, hole1.30, body depth7.50, pin3.50 from wire face.
    t=start(name,'Wuerth WR-TBL1377, 5mm pitch, 1.3mm holes, wire entry toward +Y','through_hole')
    t+=rectangle(-2.5,-4,(n-1)*5+2.5,3.5,'F.Fab',.1)
    t+=rectangle(-2.65,-4.15,(n-1)*5+2.65,3.65,'F.SilkS')
    t+=rectangle(-3,-4.5,(n-1)*5+3,4,'F.CrtYd',.05)
    t+='(fp_line (start -2.5 2.2) (end '+str((n-1)*5+2.5)+' 2.2) (stroke (width .15) (type solid)) (layer "F.SilkS"))\n'
    for i in range(n):
        t+=f'(pad "{i+1}" thru_hole {"rect" if i==0 else "circle"} (at {i*5} 0) (size 2.8 2.8) (drill 1.3) (layers "*.Cu" "*.Mask"))\n'
    t+=')\n';(lib/(name+'.kicad_mod')).write_text(t)
    manifest.append({'library_id':'FRC_Sensor_CAN:'+name,'source':'https://www.we-online.com/components/products/datasheet/691137710003.pdf','basis':'1.30mm drill, 5.00mm pitch, body7.50mm deep, pad2.80mm added for hand soldering.'})

name='TI_DGN0008K_HVSSOP8_EP'
t=start(name,'TI DGN0008K-C01 4232899/A04/2026; copper2x3, exposed1.57x1.89; segmented paste')
t+=rectangle(-1.5,-1.5,1.5,1.5,'F.Fab',.1)
t+=rectangle(-3.15,-1.85,3.15,1.85,'F.CrtYd',.05)
for yy in [-1.7,1.7]:t+=f'(fp_line (start -1.5 {yy}) (end 1.5 {yy}) (stroke (width .15) (type solid)) (layer "F.SilkS"))\n'
t+='(fp_circle (center -2.3 -1.7) (end -2.1 -1.7) (stroke (width .15) (type solid)) (fill solid) (layer "F.SilkS"))\n'
for i in range(4):
    for pin,x,y in [(i+1,-2.2,-.975+i*.65),(8-i,2.2,-.975+i*.65)]:
        t+=f'(pad "{pin}" smd roundrect (at {x} {y:.3f}) (size 1.4 .45) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio .111111))\n'
t+='(pad "9" smd rect (at 0 0) (size 2 3) (layers "F.Cu") (zone_connect 2))\n'
t+='(pad "" smd rect (at 0 0) (size 1.57 1.89) (layers "F.Mask"))\n'
for x in [-.4,.4]:
    for y in [-.5,.5]:
        t+=f'(pad "" smd roundrect (at {x} {y}) (size .65 .8) (layers "F.Paste") (roundrect_rratio .1))\n'
# Four tented0.3mm thermal drills are outside the exposed mask/paste window.
for x in [-.55,.55]:
    for y in [-1.25,1.25]:
        t+=f'(pad "9" thru_hole circle (at {x} {y}) (size .6 .6) (drill .3) (layers "*.Cu") (zone_connect 2))\n'
t+=')\n';(lib/(name+'.kicad_mod')).write_text(t)
manifest.append({'library_id':'FRC_Sensor_CAN:'+name,'source':'https://www.ti.com/lit/ds/symlink/tps1h200a-q1.pdf','basis':'DGN0008K-C01 recommended lead land1.4x0.45 at4.4 row spacing; copper2x3, mask1.57x1.89. Hand-reflow adaptation: ~70% segmented paste and four0.3mm drills outside paste; verify wetting on prototype.'})
(ROOT/'hardware/library/footprint_provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ROOT/'hardware/library/README.md').write_text('''Project footprints and 3D assets copied from KiCad10.0.6 libraries retain the KiCad library license (CC-BY-SA4.0 with the KiCad exception). Source: https://www.kicad.org/libraries/license/ . Existing asset changes are limited to project-relative 3D model paths. Custom Wuerth and TI footprints are original geometry based on the linked manufacturer package drawings; see footprint_provenance.json. Print at1:1 and check against purchased components before ordering boards.\n''')
print('Prepared',len(manifest),'local footprints and',len(list(models.iterdir())),'3D models.')
