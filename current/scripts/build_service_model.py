"""Nominal XFCN PM254V-12-10P-H85 socket envelope; not a vendor fit model.

Dimensions follow the linked drawing in status_service_models.md. Recesses and
contact interiors are illustrative. Local pin numbering stays in the PCB;
model Y has the opposite sign to footprint Y, as required by KiCad.
"""
from pathlib import Path
import cadquery as cq

R = Path(__file__).resolve().parents[1]
body = cq.Workplane('XY').box(5, 13.1, 8.5, centered=(True, True, False)).translate((1.27, -5.08, 0))
assembly = cq.Assembly(name='PM254V_12_10P_H85')
for row in range(5):
    for col in range(2):
        x, y = col * 2.54, -row * 2.54
        opening = cq.Workplane('XY').box(1.2, 1.2, 6.6, centered=(True, True, False)).translate((x, y, 2))
        body = body.cut(opening)
        tail = cq.Workplane('XY').box(.64, .40, 4, centered=(True, True, False)).translate((x, y, -3.2))
        assembly.add(tail, name=f'tail_{row}_{col}', color=cq.Color(.72, .72, .70))
assembly.add(body, name='insulator', color=cq.Color(.065, .065, .07))
assembly.export(str(R / 'hardware/library/3d/Service_2x05_P2.54mm.step'))
