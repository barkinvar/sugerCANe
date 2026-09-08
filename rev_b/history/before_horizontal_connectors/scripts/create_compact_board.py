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
 'J1':(13,9,180),'J2':(43,9,180),'J3':(53,9,180),
 'F1':(5,15,90),'Q1':(16,17,0),'D3':(19,12,90),'R3':(17,10,90),'D2':(24,18,90),'C1':(26,8,0),
 'U1':(10,25,180),'C2':(9,20,0),'C3':(13.3,25,270),'L1':(20,25,0),'C4':(26,22.5,0),'C5':(26,26,0),'C13':(26,29.5,0),'C6':(10,29,0),'R1':(5,22,0),'R2':(5,25,180),
 'U8':(14.5,34,0),'L2':(8,34,0),'D4':(16,30,0),'C15':(20,34,0),'C16':(20,37.5,0),'C17':(14.5,38,0),
 'U2':(27,35,0),'C7':(24,34.5,90),'C8':(31,34.5,90),'R4':(29,39,0),
 'U3':(7,42,0),'R5':(7,46,0),'R6':(12,41,90),'R7':(3,37,90),'R8':(3,42,90),'R9':(12,45,90),'C9':(7,38,0),'C10':(14,48,0),'C14':(7,49,0),'R14':(13,51,0),
 'U4':(20,44,0),'R10':(19,48,0),'R11':(24,42,90),'R12':(16,41,90),'R13':(18,40,0),'C11':(20,40,0),'C12':(25,46,90),'R15':(24,50,0),
 'U5':(41,28,0),'Y1':(30,27,180),'R20':(35,28,180),'C25':(34,24,90),'C26':(28,31,270),
 'C20':(39,21,0),'C21':(34,31,90),'C22':(48.5,31,90),'C23':(34,35,0),'C24':(44,35,0),'R21':(39,35,0),'C27':(38,38,0),'R22':(36,20,0),
 'R23':(47,38,0),'R24':(51,38,0),'C28':(47,41,90),'R25':(53,33,90),'R26':(57,33,90),'C29':(55,37,0),
 'U6':(45,17,0),'D20':(47,12,0),'R40':(37,17,90),'R41':(53,23,0),'C40':(39,17,90),'C41':(51,17,90),'C42':(55,17,90),'R42':(57,12,90),'JP2':(56,21,0),
 'D10':(32,17,0),'D11':(32,20,0),'R30':(29,17,90),'R31':(29,21,90),
 'U7':(39,43,90),'C50':(39,38,0),
 'J8':(53,26,0),'TP1':(3,28,0),'TP2':(3,18,0),'TP3':(17,37,0),'TP4':(31,38,0),'TP5':(28,48,0),'TP6':(10,52,0),
}
# Bottom sensor bank. Header bodies and release buttons remain accessible.
for ch,cx in enumerate([12,30,48],1):
 z=ch*100
 P.update({f'J{ch+3}':(cx-3.5,59,0),f'JP{z+1}':(cx-5,53,90),f'JP{z+2}':(cx+2,51,90),f'JP{z+3}':(cx+2,54,90),
 f'D{z+1}':(cx,57,0),f'D{z+2}':(cx+5,47,90),f'D{z+3}':(cx+5,43,90),
 f'R{z+1}':(cx-5,48,0),f'R{z+2}':(cx-5,45,0),f'R{z+3}':(cx-5,42,0),f'R{z+4}':(cx-1,45,90),
 f'R{z+5}':(cx-1,41,0),f'R{z+6}':(cx-4,38,0),f'R{z+7}':(cx,38,0),f'R{z+8}':(cx+4,38,0),
 f'R{z+9}':(cx+7,51,90),f'R{z+10}':(cx-3,50,0),f'R{z+11}':(cx+3,45,0),f'C{z+1}':(cx,48,0),
 f'D{11+ch}':(cx-7,57,90),f'R{31+ch}':(cx-7,54,90),f'TP{6+ch}':(cx+6,41,0)})
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
 b.Add(fp)
W,H=60,68
for a,z in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
 sh=p.PCB_SHAPE();sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(v(*a));sh.SetEnd(v(*z));sh.SetLayer(p.Edge_Cuts);sh.SetWidth(p.FromMM(.05));b.Add(sh)
for i,(x,y) in enumerate([(3.5,3.5),(56.5,3.5),(3.5,64.5),(56.5,64.5)],1):
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
