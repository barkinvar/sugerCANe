#!/usr/bin/env python3
"""Replace the series Schottky with reviewed AO4485 reverse-polarity protection."""
from pathlib import Path
import json,uuid,xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];HW=ROOT/'hardware';PATH=HW/'FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(PATH));parts=json.loads((HW/'design/circuit.json').read_text())['parts']
old=b.FindFootprintByReference('D1');assert old,'Run once on before_mosfet_entry board'
b.Remove(old)
# Two old heat-spreading vias would lie under the new package/gate escape.
for item in list(b.GetTracks()):
 if isinstance(item,p.PCB_VIA):
  oldpos=tuple(p.ToMM(item.GetPosition()))
  if oldpos==(15.0,13.2):item.SetPosition(p.VECTOR2I(p.FromMM(14.2),p.FromMM(18.5)))
  if oldpos==(23.0,13.0):item.SetPosition(p.VECTOR2I(p.FromMM(23),p.FromMM(16)))
if 'REV_GATE' not in b.GetNetsByName():b.Add(p.NETINFO_ITEM(b,'REV_GATE'))
nets=b.GetNetsByName()
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
tree=ET.parse(HW/'design/schematic.net.xml').getroot()
components={x.get('ref'):x for x in tree.find('components')}
ns=uuid.UUID('1358f0c9-f8c1-4e34-9e77-f77f53fd04d3')
for ref,x,y,angle,label in [('Q1',18,15.4,180,(18,19.7)),('D3',24,11.2,0,(24.8,9.3)),('R3',29.5,10.8,0,(29.5,9))]:
 c=parts[ref];f=p.FootprintLoad(str(HW/'library/FRC_Sensor_CAN.pretty'),c['footprint'].split(':')[1])
 f.SetReference(ref);f.SetValue(c['value']);f.SetFPIDAsString(c['footprint']);f.SetPosition(v(x,y));f.SetOrientationDegrees(angle)
 for pad in f.Pads():pad.SetNet(nets[c['pins'][pad.GetNumber()]]);pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
 comp=components[ref];spath=comp.find('sheetpath').get('tstamps');stamp=comp.find('tstamps').text.split()[0]
 f.SetPath(p.KIID_PATH('/'+str(uuid.uuid5(ns,'root'))+spath+stamp));f.SetSheetname(comp.find('sheetpath').get('names'));f.SetSheetfile('power.kicad_sch')
 f.Reference().SetTextSize(v(.85,.85));f.Reference().SetTextThickness(p.FromMM(.13));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.Reference().SetPosition(v(*label));f.Value().SetVisible(False);b.Add(f)
def route(net,points,width=.3,layer=p.F_Cu):
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
def via(net,x,y):
 t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(.7));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[net]);t.SetFrontTentingMode(p.TENTING_MODE_TENTED);t.SetBackTentingMode(p.TENTING_MODE_TENTED);t.SetLocked(True);b.Add(t)
route('REV_GATE',[(20.475,13.495),(21.305,13.495),(21.8,13)]);via('REV_GATE',21.8,13)
route('REV_GATE',[(21.8,13),(22.3,12.5),(26.5,12.5)],.3,p.B_Cu);via('REV_GATE',26.5,12.5)
route('REV_GATE',[(26.5,12.5),(26.5,12.35),(25.35,11.2),(25.75,10.8),(28.55,10.8)])
route('VIN_PROT',[(22.65,11.2),(23,11.2)],.35)
b.FindFootprintByReference('D2').Reference().SetPosition(v(27.2,18.3))
for d in b.GetDrawings():
 if isinstance(d,p.PCB_TEXT) and d.GetText()=='+':d.SetPosition(v(17,11.6))
for zone in b.Zones():
 if zone.GetZoneName().startswith('D1 heat spread'):zone.SetZoneName(zone.GetZoneName().replace('D1 heat spread','Q1 power copper'))
filler=p.ZONE_FILLER(b);filler.Fill(b.Zones());p.SaveBoard(str(PATH),b)
print('AO4485 Q1,12V gate clamp D3,and gate pulldown R3 installed in routed PCB.')
