#!/usr/bin/env python3
"""Create the placed PCB from the KiCad-exported schematic netlist.
Run with kicad-python. This does not overwrite a routed board: output is placed.kicad_pcb.
"""
from pathlib import Path
import json,sys,uuid,xml.etree.ElementTree as ET
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1]; HW=ROOT/'hardware'
M=json.loads((HW/'design/circuit.json').read_text())['parts']
netlist=ET.parse(HW/'design/schematic.net.xml').getroot()
NS=uuid.UUID('1358f0c9-f8c1-4e34-9e77-f77f53fd04d3')
def uid(s):return str(uuid.uuid5(NS,s))
def pt(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))
b=pcb.BOARD();b.SetFileName(str(HW/'FRC_Sensor_CAN.kicad_pcb'))
settings=b.GetDesignSettings();settings.SetCopperLayerCount(2)
settings.m_TrackMinWidth=pcb.FromMM(.18);settings.m_MinClearance=pcb.FromMM(.2)
settings.m_ViasMinSize=pcb.FromMM(.6);settings.m_MinThroughDrill=pcb.FromMM(.3)
settings.m_ViasMinAnnularWidth=pcb.FromMM(.15);settings.m_CopperEdgeClearance=pcb.FromMM(.3)
settings.m_HoleToHoleMin=pcb.FromMM(.25)
settings.m_SolderMaskMinWidth=pcb.FromMM(.08)
settings.m_MinSilkTextHeight=pcb.FromMM(.8);settings.m_MinSilkTextThickness=pcb.FromMM(.12)
tb=b.GetTitleBlock();tb.SetTitle('FRC Sensor CAN');tb.SetRevision('A PROTOTYPE');tb.SetDate('2026-09-07');tb.SetCompany('Original sensor-to-CAN hardware')

nets={}; pin_nets={}
for n in netlist.find('nets'):
    name=n.get('name');nn=pcb.NETINFO_ITEM(b,name);b.Add(nn);nets[name]=nn
    for node in n.findall('node'):pin_nets[(node.get('ref'),node.get('pin'))]=name

P={
 'J1':(17,7,180),'J2':(71,7,180),'J3':(85,7,180),
 'F1':(12,17,270),'Q1':(18,15.4,180),'D3':(24,11.2,0),'R3':(29.5,10.8,0),'D2':(27,16,0),'C1':(35,14,0),
 'U1':(18,26,180),'C2':(21,20.5,0),'C3':(21.2,25.6,270),'C6':(18,30,0),
 'L1':(27,26,0),'C4':(34,25,0),'C5':(34,30,0),'R1':(13,23,0),'R2':(13,26,180),
 'U2':(40,26,0),'C7':(39,21.5,0),'C8':(44,26,90),'R4':(44,30,90),
 'U3':(20,42,0),'R5':(20,48,0),'R6':(27,39,0),'R7':(11,40,0),'R8':(11,44,0),'R9':(27,43,0),
 'C9':(16,36,0),'C10':(30,48,0),'R14':(33,44,0),
 'U4':(37,40,0),'R10':(35,45,0),'R11':(43,38,0),'R12':(33,37,0),'R13':(30,35,0),
 'C11':(38,35,0),'C12':(42,44,0),'R15':(44,48,0),
 'U5':(58,26,0),'Y1':(47.5,24.5,90),'R20':(50,25.5,90),
 'C20':(51.5,21.5,90),'C21':(51.5,28.5,90),'C22':(65.5,30,90),'C23':(48.5,28.5,90),'C24':(61,34,0),
 'C25':(44.5,21,0),'C26':(44.5,28.5,90),'R21':(51.5,32,0),'C27':(47.5,32,0),'R22':(54,17.5,0),
 'J8':(48,7,0),'JP1':(39,7,0),
 'R23':(54,37,0),'R24':(54,40,0),'C28':(58,37,90),'R25':(59,41,0),'R26':(63,41,0),'C29':(63,44,0),
 'U6':(78,18,0),'D20':(78,11.5,0),'R40':(71,22,0),'R41':(73,25,0),
 'C40':(72.5,18,90),'C41':(83.5,18,90),'C42':(83,22,0),'R42':(89,15,90),'JP2':(89,21,0),
 'D10':(66,38,0),'D11':(72,38,0),'R30':(66,34,90),'R31':(72,34,90),
 'U7':(49,60,0),'C50':(49,67,0),
 'TP1':(27,8,0),'TP2':(23,8,0),'TP3':(39,31,0),'TP4':(44,34,0),
 'TP5':(38,50,0),'TP6':(8,50,0),
 'TP7':(27,60,0),'TP8':(46,70,0),'TP9':(69,60,0),'TP10':(90,60,0)
}
for ch,cx in enumerate([15,37,59,81],1):
    z=ch*100
    P.update({f'J{ch+3}':(cx-5,89,0),f'JP{z+1}':(cx-5,76,0),f'JP{z+2}':(cx-5,70,0),f'JP{z+3}':(cx+3,76,0),
              f'D{z+1}':(cx+5,85,0),f'D{z+2}':(cx+2,72,0),f'D{z+3}':(cx+2,67,0),
              f'R{z+1}':(cx+4,60,0),f'R{z+2}':(cx+4,57,0),f'R{z+3}':(cx-2,57,0),f'R{z+4}':(cx-2,61,0),
              f'R{z+5}':(cx-5,65,0),f'R{z+6}':(cx-4,51,0),f'R{z+7}':(cx,51,0),f'R{z+8}':(cx+4,51,0),
              f'R{z+9}':(cx+8,70,90),f'C{z+1}':(cx,54,0),f'D{11+ch}':(cx,85,0),f'R{31+ch}':(cx,82,0)})
# Clearance corrections from the first placement DRC.
P.update({'C1':(35,15,0),'D2':(26.5,15,0),'C2':(23.5,20,0),'C3':(21.3,26,270),'JP1':(41,6,0),
 'C13':(34,20,0),'C14':(24,46,0),
 'R14':(29,51,0),'TP5':(39,48,0),'TP6':(6,47,0),'TP8':(49.5,73,0),
 'U5':(60,26,0),'Y1':(48,25,180),'R20':(53,26,180),
 'C20':(58,19,0),'C21':(52.7,29,90),'C22':(67.5,30,90),'C23':(50,30,0),'C24':(63,34,0),
 'C25':(52,22,90),'C26':(46,29.5,270),'C8':(44,25,90),'R4':(42.5,31,0),
 'R21':(55,33,0),'C27':(50,33.5,0),'R22':(56,17,0),'D20':(78,13.5,0),'R305':(56,65,0)})
for ch,cx in enumerate([15,37,59,81],1):
 P[f'J{ch+3}']=(cx-5+(.5 if ch==1 else -.5 if ch==4 else 0),90,0)
 P[f'D{ch*100+1}']=(cx+10+(.5 if ch==1 else 0),83,90)
 P[f'JP{ch*100+2}']=(cx-5,69,0)
 P[f'D{11+ch}']=(cx,84,0)
 P[f'R{31+ch}']=(cx-1,80.5,90)
 P[f'R{ch*100+10}']=(cx+10,76,0)
 P[f'R{ch*100+11}']=(cx+2,63.7,0)
assert set(P)==set(M),f'Placement difference: missing {set(M)-set(P)},extra {set(P)-set(M)}'

footprints={}
components={n.get('ref'):n for n in netlist.find('components')}
for ref,c in M.items():
    fpname=c['footprint'].split(':')[1]
    f=pcb.FootprintLoad(str(HW/'library/FRC_Sensor_CAN.pretty'),fpname)
    if not f:raise RuntimeError('Cannot load footprint '+fpname)
    f.SetReference(ref);f.SetValue(c['value']);f.SetFPIDAsString(c['footprint'])
    x,y,a=P[ref];f.SetPosition(pt(x,y));f.SetOrientationDegrees(a)
    for pad in f.Pads():
        pin=pad.GetNumber()
        if not pin:continue
        net=pin_nets.get((ref,pin))
        if net:pad.SetNet(nets[net])
        elif pin not in c['pins']:raise RuntimeError(f'{ref} footprint has unexpected pin{pin}')
    # Link to the generated schematic instance for KiCad update and DRC parity.
    comp=components[ref];spath=comp.find('sheetpath').get('tstamps')
    stamp=comp.find('tstamps').text.split()[0]
    f.SetPath(pcb.KIID_PATH('/'+uid('root')+spath+stamp))
    f.SetSheetname(comp.find('sheetpath').get('names'));f.SetSheetfile(c['sheet']+'.kicad_sch')
    f.Reference().SetTextSize(pt(.85,.85));f.Reference().SetTextThickness(pcb.FromMM(.13))
    f.Reference().SetKeepUpright(True);f.Value().SetVisible(False)
    if c.get('exclude_bom'): f.SetAttributes(f.GetAttributes()|pcb.FP_EXCLUDE_FROM_BOM|pcb.FP_EXCLUDE_FROM_POS_FILES)
    b.Add(f);footprints[ref]=f

# 96mm square board stays within common 100mm fabrication pricing.
for a,z in [((0,0),(96,0)),((96,0),(96,96)),((96,96),(0,96)),((0,96),(0,0))]:
    sh=pcb.PCB_SHAPE();sh.SetShape(pcb.SHAPE_T_SEGMENT);sh.SetStart(pt(*a));sh.SetEnd(pt(*z));sh.SetLayer(pcb.Edge_Cuts);sh.SetWidth(pcb.FromMM(.05));b.Add(sh)
# Four unplated M3 mounting holes; keep copper and tall parts away from screw heads.
for i,(x,y) in enumerate([(4,4),(92,4),(4,92),(92,92)],1):
    f=pcb.FOOTPRINT(b);f.SetReference(f'H{i}');f.SetValue('M3 NPTH');f.SetPosition(pt(x,y));f.Value().SetVisible(False)
    f.SetAttributes(pcb.FP_EXCLUDE_FROM_BOM|pcb.FP_EXCLUDE_FROM_POS_FILES)
    pad=pcb.PAD(f);pad.SetAttribute(pcb.PAD_ATTRIB_NPTH);pad.SetShape(pcb.PAD_SHAPE_CIRCLE);pad.SetSize(pt(3.2,3.2));pad.SetDrillSize(pt(3.2,3.2));pad.SetLayerSet(pcb.LSET.AllCuMask());f.Add(pad)
    f.Reference().SetPosition(pt(x,y+4 if y<48 else y-5));f.Reference().SetTextSize(pt(.85,.85));f.Reference().SetTextThickness(pcb.FromMM(.13));b.Add(f)
    # Courtyard conveys 6.4mm screw head space to assembly DRC.
    sh=pcb.PCB_SHAPE(f);sh.SetShape(pcb.SHAPE_T_CIRCLE);sh.SetCenter(pt(x,y));sh.SetEnd(pt(x+3.2,y));sh.SetLayer(pcb.F_CrtYd);sh.SetWidth(pcb.FromMM(.05));f.Add(sh)

# These board markings are a first pass, then adjusted after DRC and rendered review.
def text(s,x,y,size=1.2,layer=pcb.F_SilkS,angle=0):
    t=pcb.PCB_TEXT(b);t.SetText(s);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(pcb.FromMM(.15));t.SetLayer(layer);t.SetMirrored(layer==pcb.B_SilkS);t.SetTextAngle(pcb.EDA_ANGLE(angle,pcb.DEGREES_T));b.Add(t)
text('FRC SENSOR CAN',76,46,1.8);text('REV A - PROTOTYPE',76,49,1)
text('12V IN',15,2.5,1);text('+',17,12.5,1);text('-',12,12.5,1)
text('CAN IN',68.5,2.5,1);text('CAN OUT',82.5,2.5,1)
text('L  H',68.5,12.5,1);text('L  H',82.5,12.5,1)
for ch,cx in enumerate([15,37,59,81],1):
    text(f'IN {ch}',cx,94,1.1);text('P  G  S',cx,92.5,.85)
text('6-18V input | 0-30V signals | 300mA per sensor rail',48,4,1,pcb.B_SilkS)
text('Custom CAN protocol. Configure device ID before use.',48,7,1,pcb.B_SilkS)
text('Power JP:1-2=5V,2-3=VBAT. Bias JP:1-2=PORT,3-4=3V3,5-6=GND.',48,12,.9,pcb.B_SilkS)
text('Only ONE shunt per power or bias selector. Threshold short=logic.',48,15,.9,pcb.B_SilkS)
text('J8:1=3V3 REF OUT,2=SWDIO,3=GND,4=SWCLK,5=GND',48,20,.9,pcb.B_SilkS)
text('6=UART TX,7=BOOT0,8=UART RX,9=GND,10=RESET',48,23,.9,pcb.B_SilkS)

b.BuildListOfNets()
pcb.SaveBoard(str(HW/'placed.kicad_pcb'),b)
# Template project and netclass settings apply to both placed and final board.
pro=json.loads((HW/'FRC_Sensor_CAN.kicad_pro').read_text())
pro['net_settings']={'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.65,'via_drill':.3,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25},
 {'name':'Power','clearance':.2,'track_width':.5,'via_diameter':.8,'via_drill':.4,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25},
 {'name':'LogicPower','clearance':.2,'track_width':.3,'via_diameter':.7,'via_drill':.3,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}],
 'netclass_patterns':[{'netclass':'Power','pattern':n} for n in ['VIN_RAW','VIN_FUSED','VIN_PROT','V5_INTERNAL','SENSOR_5V','SENSOR_VBAT','VPORT*']]+[{'netclass':'LogicPower','pattern':'+3V3'}]}
for name in ['FRC_Sensor_CAN','placed']:(HW/(name+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
(HW/'design/placement.json').write_text(json.dumps(P,indent=2)+'\n')
print('Placed',len(footprints),'components plus4mounting holes on96x96mm.')
