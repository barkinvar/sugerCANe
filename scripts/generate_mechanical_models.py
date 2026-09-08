#!/usr/bin/env python3
"""Original simplified package models from manufacturer outline dimensions.

These aid clearance/assembly review, not tooling or supplier dimensional inspection.
Pin and screw details are illustrative. Nominal dimensions; allow drawing tolerances.
"""
from pathlib import Path
import json
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "hardware/library/3d"
DEST.mkdir(parents=True, exist_ok=True)
METAL, BLACK = cq.Color(0.72, 0.73, 0.75), cq.Color(0.10, 0.11, 0.12)
manifest = []


def box(x, y, z, center):
    return cq.Workplane("XY").box(x, y, z).translate(center)


def save(assembly, name, dimensions, source, notes=""):
    assembly.export(str(DEST / f"{name}.step"))
    manifest.append(dict(name=name, dimensions_mm=dimensions, source=source,
                         type="Original simplified mechanical envelope", notes=notes))


for n in (2, 3):
    name = f"Wuerth_69113771000{n}"
    a = cq.Assembly(name=name)
    # KiCad model Y is opposite PCB Y; wire entry is toward PCB +Y.
    body = box(5*n, 7.5, 11.5, ((n-1)*2.5, 0.25, 5.75))
    for i in range(n):
        body = body.cut(box(3.3, 2.0, 4.0, (5*i, -3.1, 4.5)))
        body = body.cut(cq.Workplane("XY").center(5*i, 0).circle(1.65).extrude(2).translate((0,0,9.6)))
    a.add(body, color=cq.Color(0.12, 0.48, 0.24), name="insulator")
    for i in range(n):
        a.add(box(0.7, 1.0, 3.6, (5*i, 0, -1.8)), color=METAL, name=f"pin_{i+1}")
        screw = cq.Workplane("XY").center(5*i, 0).circle(1.4).extrude(0.6).translate((0,0,9.8))
        screw = screw.cut(box(3.0, 0.4, 0.3, (5*i,0,10.3)))
        a.add(screw, color=METAL, name=f"screw_{i+1}")
    save(a, name, [5*n, 7.5, 11.5],
         f"https://www.we-online.com/components/products/datasheet/69113771000{n}.pdf",
         "Body height tolerance +0.1 mm; leads extend 3.6 mm below seating plane. Wire-entry/screw details illustrative.")

name = "TI_DGN0008K_HVSSOP8_EP"
a = cq.Assembly(name=name)
a.add(box(3,3,0.9,(0,0,0.55)), color=BLACK, name="body")
for i in range(4):
    for side in (-1,1):
        a.add(box(1.0,0.28,0.15,(side*1.95,0.975-i*0.65,0.075)), color=METAL,
              name=f"lead_{side}_{i}")
a.add(box(1.57,1.89,0.1,(0,0,0.05)), color=METAL, name="exposed_pad")
a.add(cq.Workplane("XY").center(-1,1).circle(.16).extrude(.01).translate((0,0,1.0)),
      color=cq.Color(.8,.8,.7), name="pin_one_dot")
save(a,name,[4.9,3.0,1.1],"https://www.ti.com/lit/ds/symlink/tps1h200a-q1.pdf",
     "Simplified gull-wing leads. DGN0008K package outline; footprint land pattern is separately audited.")

name = "Crystal_SMD_5032-4Pin_5.0x3.2mm"
a = cq.Assembly(name=name)
a.add(box(5,3.2,.85,(0,0,.475)),color=cq.Color(.80,.79,.72),name="ceramic")
a.add(box(4.7,2.9,.2,(0,0,1.0)),color=METAL,name="lid")
for i,(x,y) in enumerate([(-1.8,-1.1),(1.8,-1.1),(1.8,1.1),(-1.8,1.1)]):
    a.add(box(1.2,.9,.1,(x,y,.05)),color=cq.Color(.80,.65,.15),name=f"pad_{i+1}")
save(a,name,[5.0,3.2,1.1],"https://abracon.com/Resonators/abm3b.pdf",
     "Nominal body envelope from ABM3B; illustrative underside metallization.")

name = "Fuse_Littelfuse-NANO2-451_453"
a = cq.Assembly(name=name)
a.add(box(6.1,2.69,2.69,(0,0,1.345)),color=cq.Color(.9,.88,.78),name="ceramic")
for i,side in enumerate((-1,1)):
    a.add(box(1.0,2.71,2.71,(side*2.55,0,1.345)),color=cq.Color(.80,.65,.15),name=f"cap_{i}")
save(a,name,[6.1,2.69,2.69],"https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1",
     "Maximum body length 6.3 mm; width/height 2.94 mm. Decorative cap detail illustrative.")

name = "L_Bourns_SRP7028A_7.3x6.6mm"
a = cq.Assembly(name=name)
body = box(7.3,6.6,2.6,(0,0,1.5)).edges("|Z").chamfer(.35)
a.add(body,color=cq.Color(.23,.24,.24),name="shielded_core")
for i,side in enumerate((-1,1)):
    a.add(box(1.8,3.0,.2,(side*2.65,0,.1)),color=METAL,name=f"terminal_{i}")
save(a,name,[7.3,6.6,2.8],"https://www.bourns.com/docs/product-datasheets/srp7028a.pdf",
     "Nominal body; add 0.3 mm X/Y and 0.2 mm height tolerance for enclosure clearance.")

(DEST / "original_models.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(f"Exported {len(manifest)} original simplified STEP models")
