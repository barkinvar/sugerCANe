#!/usr/bin/env python3
"""TI RYQ0021B land/stencil pattern, drawing 4228792/A, pages 35–37.

Coordinates are TOP VIEW, pin 1 upper left. No guessed exposed center pad:
the five long strips are electrical pins 7–11, with pin 9 the only PGND strip.
Manufacturer suggested stencil divides each long strip into three 1 mm slots.
"""
from pathlib import Path
import json,shutil,os
import cadquery as cq
R=Path(__file__).resolve().parents[1];D=R/'hardware/library';F=D/'FRC_Sensor_CAN.pretty';G=D/'3d'
K=Path(os.environ['CANDI_TOOLS_ROOT'])/'kicad/AppDir/share/kicad'
for lib,name in [('Capacitor_SMD','C_0402_1005Metric'),('Inductor_SMD','L_Bourns_SRP5030T'),('NetTie','NetTie-2_SMD_Pad0.5mm')]:
 dest=name.replace('NetTie-','NetTie_')
 s=(K/f'footprints/{lib}.pretty/{name}.kicad_mod').read_text().replace(name,dest)
 s=s.replace('${KICAD10_3DMODEL_DIR}/'+lib+'.3dshapes/','${KIPRJMOD}/library/3d/')
 (F/(dest+'.kicad_mod')).write_text(s)
 model=K/f'3dmodels/{lib}.3dshapes/{name}.step'
 if model.exists():shutil.copyfile(model,G/(dest+'.step'))
name='TI_RYQ0021B_VQFN_HR_5x3mm'
s=[f'(footprint "{name}" (version 20260206) (generator "pcbnew") (layer "F.Cu")',
 '(descr "TI RYQ0021B; 4228792/A land and segmented stencil; top view, pin 1 upper left") (attr smd)',
 '(property "Reference" "REF**" (at 0 -2.6 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
 f'(property "Value" "{name}" (at 0 2.6 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
 '(fp_rect (start -2.85 -1.95) (end 2.85 1.95) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
 '(fp_rect (start -2.5 -1.5) (end 2.5 1.5) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))',
 '(fp_line (start -2.5 -1) (end -2 -1.5) (stroke (width 0.1) (type default)) (layer "F.Fab"))',
 '(fp_line (start -2.8 -1.15) (end -2.8 -1.75) (stroke (width 0.12) (type default)) (layer "F.SilkS"))',
 '(fp_line (start -2.8 -1.75) (end -2.35 -1.75) (stroke (width 0.12) (type default)) (layer "F.SilkS"))']
pads={}
for n in range(1,5):pads[n]=(-2.4,-.75+(n-1)*.5,.6,.25)
for n in range(14,18):pads[n]=(2.4,.75-(n-14)*.5,.6,.25)
for n,x,y,h in [(5,-2.04,1.375,.65),(6,-1.54,1.4,.6),(12,1.54,1.4,.6),(13,2.04,1.375,.65),(18,2.04,-1.375,.65),(19,1.54,-1.4,.6),(20,-1.54,-1.4,.6),(21,-2.04,-1.375,.65)]:pads[n]=(x,y,.25,h)
for n,x,w in [(7,-1.04,.25),(8,-.54,.25),(9,0,.33),(10,.54,.25),(11,1.04,.25)]:pads[n]=(x,0,w,3.4)
for n,(x,y,w,h) in sorted(pads.items()):
 layers='"F.Cu" "F.Mask"'+(' "F.Paste"' if n not in range(7,12) else '')
 s.append(f'(pad "{n}" smd roundrect (at {x} {y}) (size {w} {h}) (layers {layers}) (roundrect_rratio {min(.05/min(w,h),.25)}) (solder_mask_margin 0.035))')
 if n in range(7,12):
  for cy in [-1.2,0,1.2]:s.append(f'(pad "" smd roundrect (at {x} {cy}) (size 0.25 1.0) (layers "F.Paste") (roundrect_rratio 0.2))')
s.append(f'(model "${{KIPRJMOD}}/library/3d/{name}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0))))')
(F/(name+'.kicad_mod')).write_text('\n'.join(s)+'\n')
# Parametric package envelope from TI drawing, not a vendor photorealistic asset.
assembly=cq.Assembly(name=name)
assembly.add(cq.Workplane('XY').box(5,3,.9,centered=(True,True,False)).translate((0,0,.1)),name='mold',color=cq.Color(.12,.12,.12))
for n,(x,y,w,h) in pads.items():
 w=min(w,.4);h=min(h,3)
 assembly.add(cq.Workplane('XY').box(w,h,.1,centered=(True,True,False)).translate((x,-y,0)),name=f'pin_{n}',color=cq.Color(.72,.72,.72))
assembly.add(cq.Workplane('XY').circle(.15).extrude(.008).translate((-2,1,.995)),name='pin1mark',color=cq.Color(.8,.8,.8))
assembly.save(str(G/(name+'.step')))
(D/'converter_package.json').write_text(json.dumps(dict(drawing='TI 4228792/A 07/2022, RYQ0021B',source='https://www.ti.com/lit/ds/symlink/tps552872-q1.pdf',orientation='Top view; pin 1 left at y=-0.75 mm',pads={str(n):dict(x=x,y=y,w=w,h=h) for n,(x,y,w,h) in pads.items()},long_pad_paste='Three 0.25 by 1.0 mm apertures centered at y=-1.2,0,1.2; all five long pins',mask_expansion_mm=.035,model='Parametric package envelope and leads from manufacturer drawing; connector models remain official vendor STEP.'),indent=2)+'\n')
print('Converter and companion footprints/models generated.')

# A standard two-terminal 1206 resistor on separate load/sense copper branches.
# Pads 3/4 are PCB sense taps, not additional physical resistor terminals.
# Net-tie groups preserve distinct sense nets during routing and join each pair
# only underneath its respective termination. Only the main lands get paste.
name='R_1206_Kelvin_Sense_Taps'
s=[f'(footprint "{name}" (version 20260206) (generator "pcbnew") (layer "F.Cu") (attr smd)',
 '(descr "1206 two-terminal resistor with Kelvin PCB branches: physical left terminal 1+3, right terminal 2+4")',
 '(net_tie_pad_groups "1,3" "2,4")',
 '(property "Reference" "REF**" (at 0 -1.8 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
 '(property "Value" "0.1" (at 0 1.8 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
 '(fp_rect (start -2.35 -1.25) (end 2.35 1.25) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
 '(fp_rect (start -1.55 -0.8) (end 1.55 0.8) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))']
for n,x in [(1,-1.52),(2,1.52)]:s.append(f'(pad "{n}" smd roundrect (at {x} 0) (size 1.1 1.9) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))')
for n,x in [(3,-1.02),(4,1.02)]:s.append(f'(pad "{n}" smd rect (at {x} -0.8) (size 0.4 0.3) (layers "F.Cu" "F.Mask"))')
s.append('(model "${KIPRJMOD}/library/3d/R_1206_3216Metric.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0))))')
(F/(name+'.kicad_mod')).write_text('\n'.join(s)+'\n')
