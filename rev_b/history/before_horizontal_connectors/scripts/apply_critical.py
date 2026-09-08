from pathlib import Path
import json,shutil,math
import pcbnew as p
R=Path(__file__).resolve().parents[1];HW=R/'hardware';b=p.LoadBoard(str(HW/'placed.kicad_pcb'));nets=b.GetNetsByName();r=json.loads((HW/'design/critical_routes.json').read_text())
def v(xy):return p.VECTOR2I(p.FromMM(xy[0]),p.FromMM(xy[1]))
for q in r['routes']:
 for a,z in zip(q['points'],q['points'][1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(p.FromMM(q['width']));t.SetLayer(p.F_Cu);t.SetNet(nets[q['net']]);t.SetLocked(True);b.Add(t)
for q in r['vias']:
 t=p.PCB_VIA(b);t.SetPosition(v(q['xy']));t.SetWidth(p.FromMM(q['diameter']));t.SetDrill(p.FromMM(q['drill']));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[q['net']]);t.SetLocked(True);b.Add(t)
for cx,cy in [(3.5,3.5),(56.5,3.5),(3.5,64.5),(56.5,64.5)]:
 z=p.ZONE(b);z.SetLayerSet(p.LSET.AllCuMask());z.SetIsRuleArea(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
 poly=z.Outline();poly.NewOutline()
 for i in range(48):a=2*math.pi*i/48;poly.Append(v((cx+3.3*math.cos(a),cy+3.3*math.sin(a))))
 b.Add(z)
b.BuildConnectivity();p.SaveBoard(str(HW/'prerouted.kicad_pcb'),b);shutil.copyfile(HW/'placed.kicad_pro',HW/'prerouted.kicad_pro')
p.ExportSpecctraDSN(b,str(HW/'design/prerouted.dsn'))
print('Saved locked local routes and exported DSN.')
