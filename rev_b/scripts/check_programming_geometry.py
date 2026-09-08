"""Check the native contact pattern, paste exclusion and actual trace clearance."""
from pathlib import Path
import json,math
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'hardware/FRC_Sensor_CAN.kicad_pcb'));j=b.FindFootprintByReference('J8')
def segdist(q,a,c):
 dx,dy=c[0]-a[0],c[1]-a[1];den=dx*dx+dy*dy
 u=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den)) if den else 0
 return math.hypot(q[0]-a[0]-u*dx,q[1]-a[1]-u*dy)
expected={'1':(31.77,8.29),'2':(31.77,7.02),'3':(31.77,5.75),'4':(31.77,4.48),'5':(31.77,3.21),'6':(30.5,3.21),'7':(30.5,4.48),'8':(30.5,5.75),'9':(30.5,7.02),'10':(30.5,8.29)}
minimum=math.inf;holes=[]
for z in j.Pads():
 if not z.GetNumber():
  assert z.GetAttribute()==p.PAD_ATTRIB_NPTH;holes.append([*p.ToMM(z.GetPosition()),p.ToMM(z.GetDrillSize().x)]);continue
 pos=p.ToMM(z.GetPosition());assert math.dist(pos,expected[z.GetNumber()])<.00001
 assert abs(p.ToMM(z.GetSize().x)-.7874)<.00001
 assert not z.IsOnLayer(p.F_Paste) and z.GetAttribute()==p.PAD_ATTRIB_CONN
 for t in b.GetTracks():
  if t.GetNetname()==z.GetNetname():continue
  if isinstance(t,p.PCB_VIA):d=math.dist(pos,p.ToMM(t.GetPosition()))-p.ToMM(t.GetWidth(p.F_Cu))/2
  elif t.GetLayer()==p.F_Cu:d=segdist(pos,p.ToMM(t.GetStart()),p.ToMM(t.GetEnd()))-p.ToMM(t.GetWidth())/2
  else:continue
  minimum=min(minimum,d-.7874/2)
assert minimum>=.508-1e-5,minimum
assert len(holes)==3
assert all(abs(q[2]-.9906)<1e-5 for q in holes)
report={'result':'PASS','contact_count':10,'pitch_mm':1.27,'contact_diameter_mm':.7874,'minimum_contact_to_foreign_track_or_via_clearance_mm':minimum,'alignment_holes_mm':holes,'paste_on_contacts':False,'source':'https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2050-IDC-NL_Datasheet_8.pdf','notes':'Standard mechanical pattern, custom electrical mapping. Native footprint rule area excludes tracks/vias between pad rows. Added front copper-pour exclusion and native custom 0.508 mm contact-to-track rule. Cable body envelope is approximately 12.446 x 6.731 mm; test actual cable/retaining clip before production.'}
(R/'reports/programming_geometry.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
