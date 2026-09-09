#!/usr/bin/env python3
"""Attach portable STEP models without changing pads, copper, or component positions."""
from pathlib import Path
import re
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
HW=ROOT/'hardware'
for fpfile in (HW/'library/FRC_Sensor_CAN.pretty').glob('*.kicad_mod'):
    model=HW/'library/3d'/(fpfile.stem+'.step')
    if not model.exists():continue
    text=fpfile.read_text()
    text=re.sub(r'\$\{KICAD10_3DMODEL_DIR\}/[^"\s)]+', '${KIPRJMOD}/library/3d/'+model.name,text)
    if '(model ' not in text and '(model\n' not in text:
        end=text.rfind(')')
        text=text[:end]+f'(model "${{KIPRJMOD}}/library/3d/{model.name}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'+text[end:]
    fpfile.write_text(text)
b=p.LoadBoard(str(HW/'FRC_Sensor_CAN.kicad_pcb'))
updated=[]
for fp in b.GetFootprints():
    name=str(fp.GetFPID().GetLibItemName())
    target=HW/'library/3d'/(name+'.step')
    if not target.exists():continue
    models=fp.Models()
    if len(models):
        for i in range(len(models)):
            model=models[i]
            model.m_Filename='${KIPRJMOD}/library/3d/'+target.name
            models[i]=model
    else:
        model=p.FP_3DMODEL();model.m_Filename='${KIPRJMOD}/library/3d/'+target.name
        models.push_back(model)
    updated.append(fp.GetReference())
p.SaveBoard(str(HW/'FRC_Sensor_CAN.kicad_pcb'),b)
print('Portable 3D models assigned to',len(updated),'footprints')
