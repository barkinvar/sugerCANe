from pathlib import Path
import json,sys,uuid,xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
M=json.loads((HW/'design/circuit.json').read_text())['parts'];nt=ET.parse(HW/'design/schematic.net.xml').getroot()
b=p.BOARD();b.SetFileName(str(HW/'FRC_Sensor_CAN.kicad_pcb'))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
s=b.GetDesignSettings();s.SetCopperLayerCount(4);s.m_TrackMinWidth=p.FromMM(.18);s.m_MinClearance=p.FromMM(.2);s.m_ViasMinSize=p.FromMM(.6);s.m_MinThroughDrill=p.FromMM(.3);s.m_ViasMinAnnularWidth=p.FromMM(.15);s.m_CopperEdgeClearance=p.FromMM(.3);s.m_HoleToHoleMin=p.FromMM(.25);s.m_SolderMaskMinWidth=p.FromMM(.08);s.m_MinSilkTextHeight=p.FromMM(.8);s.m_MinSilkTextThickness=p.FromMM(.12)
nets={};pn={}
for n in nt.find('nets'):
 name=n.get('name');nn=p.NETINFO_ITEM(b,name);b.Add(nn);nets[name]=nn
 for node in n.findall('node'):pn[node.get('ref'),node.get('pin')]=name
# Final preferred positions include the regulated 12 V power stage.
P=json.loads((HW/'design/compact_placement.json').read_text())
assert set(P)==set(M),(set(M)-set(P),set(P)-set(M))
# An optional collision-free optimized placement overrides initial positions.
(HW/'design/placement_preferred.json').write_text(json.dumps(P,indent=2)+'\n')
if (HW/'design/compact_placement.json').exists():P.update(json.loads((HW/'design/compact_placement.json').read_text()))
components={c.get('ref'):c for c in nt.find('components')};ns=uuid.UUID('1358f0c9-f8c1-4e34-9e77-f77f53fd04d3')
for ref,c in M.items():
 fp=p.FootprintLoad(str(HW/'library/FRC_Sensor_CAN.pretty'),c['footprint'].split(':')[1]);assert fp
 fp.SetReference(ref);fp.SetValue(c['value']);fp.SetFPIDAsString(c['footprint']);x,y,a=P[ref];fp.SetPosition(v(x,y));fp.SetOrientationDegrees(a)
 for pad in fp.Pads():
  name=pn.get((ref,pad.GetNumber()))
  if name:pad.SetNet(nets[name])
 comp=components[ref];stamp=comp.find('tstamps').text.split()[0];spath=comp.find('sheetpath').get('tstamps')
 fp.SetPath(p.KIID_PATH('/'+str(uuid.uuid5(ns,'root'))+spath+stamp));fp.SetSheetname(comp.find('sheetpath').get('names'));fp.SetSheetfile(c['sheet']+'.kicad_sch')
 fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
 if c.get('exclude_bom'):fp.SetAttributes(fp.GetAttributes()|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
 fp.SetField('MPN',c.get('mpn',''));fp.GetField('MPN').SetVisible(False)
 b.Add(fp)
W,H=52,64
for a,z in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
 sh=p.PCB_SHAPE();sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(v(*a));sh.SetEnd(v(*z));sh.SetLayer(p.Edge_Cuts);sh.SetWidth(p.FromMM(.05));b.Add(sh)
for i,(x,y) in enumerate([(3.5,4),(48.5,42.5)],1):
 f=p.FOOTPRINT(b);f.SetReference('H'+str(i));f.SetValue('M3 NPTH');f.SetPosition(v(x,y));f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
 pad=p.PAD(f);pad.SetAttribute(p.PAD_ATTRIB_NPTH);pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetSize(v(3.2,3.2));pad.SetDrillSize(v(3.2,3.2));pad.SetLayerSet(p.LSET.AllCuMask());f.Add(pad)
 sh=p.PCB_SHAPE(f);sh.SetShape(p.SHAPE_T_CIRCLE);sh.SetCenter(v(x,y));sh.SetEnd(v(x+3.2,y));sh.SetLayer(p.F_CrtYd);sh.SetWidth(p.FromMM(.05));f.Add(sh);b.Add(f)
# Board side and package bounds for the placement optimizer.
b.BuildConnectivity();p.SaveBoard(str(HW/'placed.kicad_pcb'),b)
records=[]
for fp in b.GetFootprints():
 pts=[]
 for gi in fp.GraphicalItems():
  if gi.GetLayer()==p.F_CrtYd:
   bb=gi.GetBoundingBox();pts.extend([(p.ToMM(bb.GetX()),p.ToMM(bb.GetY())),(p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()))])
 if not pts:
  for pad in fp.Pads():
   bb=pad.GetBoundingBox();pts.extend([(p.ToMM(bb.GetX())-.3,p.ToMM(bb.GetY())-.3),(p.ToMM(bb.GetRight())+.3,p.ToMM(bb.GetBottom())+.3)])
 x,y=p.ToMM(fp.GetPosition());bb=[min(q[0] for q in pts),min(q[1] for q in pts),max(q[0] for q in pts),max(q[1] for q in pts)]
 records.append(dict(ref=fp.GetReference(),xy=[x,y],angle=fp.GetOrientationDegrees(),bbox=bb,pads=[dict(pin=a.GetNumber(),net=a.GetNetname(),xy=list(p.ToMM(a.GetPosition()))) for a in fp.Pads()]))
(HW/'design/placement_geometry.json').write_text(json.dumps(records,indent=2)+'\n')
(HW/'design/placement_initial.json').write_text(json.dumps(P,indent=2)+'\n')
pro=json.loads((HW/'FRC_Sensor_CAN.kicad_pro').read_text())
pro['net_settings']={'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.65,'via_drill':.3,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25},{'name':'Power','clearance':.2,'track_width':.5,'via_diameter':.8,'via_drill':.4,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}], 'netclass_patterns':[{'netclass':'Power','pattern':n} for n in ['VIN_RAW','VIN_FUSED','VIN_PROT','V4P2','V5_INTERNAL','SENSOR_5V','SENSOR_12V','V12_RAW','VPORT*']]}
for n in ['placed','FRC_Sensor_CAN']:(HW/(n+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
print('Created compact placement',W,H,len(M),'components')
