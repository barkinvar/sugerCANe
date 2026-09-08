from pathlib import Path
import json,sys,uuid,xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware'
M=json.loads((HW/'design/circuit.json').read_text())['parts'];nt=ET.parse(HW/'design/schematic.net.xml').getroot()
b=p.BOARD();b.SetFileName(str(HW/'FRC_Sensor_CAN.kicad_pcb'))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
s=b.GetDesignSettings();s.SetCopperLayerCount(2);s.m_TrackMinWidth=p.FromMM(.18);s.m_MinClearance=p.FromMM(.2);s.m_ViasMinSize=p.FromMM(.6);s.m_MinThroughDrill=p.FromMM(.3);s.m_ViasMinAnnularWidth=p.FromMM(.15);s.m_CopperEdgeClearance=p.FromMM(.3);s.m_HoleToHoleMin=p.FromMM(.25);s.m_SolderMaskMinWidth=p.FromMM(.08);s.m_MinSilkTextHeight=p.FromMM(.8);s.m_MinSilkTextThickness=p.FromMM(.12)
nets={};pn={}
for n in nt.find('nets'):
 name=n.get('name');nn=p.NETINFO_ITEM(b,name);b.Add(nn);nets[name]=nn
 for node in n.findall('node'):pn[node.get('ref'),node.get('pin')]=name
P={
 'J1':(13,9,180),'J2':(39,9,180),'J3':(48.5,9,180),'J8':(24,5.75,0),
 'F1':(7,14,0),'Q1':(13,16,0),'D3':(12,12.5,0),'R3':(17,12.5,90),'D2':(22,17,90),'C1':(4.5,23,0),
 'U1':(13,23,180),'C2':(11.5,19,0),'C3':(16.5,22,270),'L1':(22,24,0),
 'C4':(28,22,0),'C5':(28,25.5,0),'C13':(28,29,0),'C6':(13,27,0),'R1':(8,22,0),'R2':(8,25,180),
 'U2':(30,32,0),'C7':(26.5,32,90),'C8':(34,31,90),'R4':(33,34.5,0),
 'U3':(9,33,0),'R5':(5,33,90),'C9':(9,29,0),'C10':(9,37,0),'C14':(5,37,0),
 'U4':(19,34,0),'R10':(17.5,38,0),'C11':(18,30,0),'C12':(23,35,90),
 'U5':(39.5,25,0),'Y1':(30.5,18,180),'R20':(34,21,180),'C25':(32,13.5,90),'C26':(27,17.5,90),
 'C20':(37.5,18.5,0),'C21':(33.5,28.5,90),'C22':(46,29,90),'C23':(37,32,0),'C24':(41,32,0),'R21':(44,34,0),'C27':(47.5,33.5,90),'R22':(36.5,14.5,0),
 'U6':(43.5,14.5,0),'D20':(43,10.5,0),'R40':(48.5,22,90),'R41':(48.5,18,90),'C40':(39.5,13.5,90),'C41':(48.5,14,90),'R42':(33,10,90),'JP2':(32,5,90),
 'D10':(19,9,0),'R30':(17,7,90),'U7':(35,38,90),'C50':(30,36,0),'R50':(42,37,0),'R51':(46,37,0),'C51':(50,37,90),
 'TP1':(2,12,0),'TP2':(3,16,0),'TP3':(25,30,0),'TP4':(34,33,0),'TP5':(24,38,0),'TP6':(12,39,0),
}
for ch,cx in enumerate([10,26,42],1):
 z=ch*100
 P.update({f'J{ch+3}':(cx-3.5,47,0),f'JP{z+1}':(cx-2.5,40.5,0),f'JP{z+3}':(cx+3,40.5,0),
 f'D{z+1}':(cx,44,0),f'D{z+2}':(cx+5,38,90),f'R{z+1}':(cx-4,37,0),f'R{z+3}':(cx-2,34.5,0),f'R{z+4}':(cx+2,34,0),f'R{z+5}':(cx+3,31,0),
 f'R{z+9}':(cx+5,43,90),f'R{z+10}':(cx-3,39,0),f'C{z+1}':(cx+1,37,0),f'TP{ch+6}':(cx+5,35,0)})
P={r:q for r,q in P.items() if r in M}
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
W,H=52,56
for a,z in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
 sh=p.PCB_SHAPE();sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(v(*a));sh.SetEnd(v(*z));sh.SetLayer(p.Edge_Cuts);sh.SetWidth(p.FromMM(.05));b.Add(sh)
for i,(x,y) in enumerate([(3.5,4),(48.5,34.5)],1):
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
pro['net_settings']={'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.65,'via_drill':.3,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25},{'name':'Power','clearance':.2,'track_width':.5,'via_diameter':.8,'via_drill':.4,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}], 'netclass_patterns':[{'netclass':'Power','pattern':n} for n in ['VIN_RAW','VIN_FUSED','VIN_PROT','V4P2','V5_INTERNAL','SENSOR_5V','SENSOR_VBAT','VPORT*']]}
for n in ['placed','FRC_Sensor_CAN']:(HW/(n+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
print('Created compact placement',W,H,len(M),'components')
