"""Apply service markings and assembly references to the final native board."""
from pathlib import Path
import json,subprocess,os
import pcbnew as p
R=Path(__file__).resolve().parents[1];f=R/'hardware/FRC_Sensor_CAN.kicad_pcb';subprocess.run(['python',str(R/'scripts/clear_board_markings.py')],check=True,env={k:v for k,v in os.environ.items() if k not in ['PYTHONHOME','PYTHONPATH']});b=p.LoadBoard(str(f))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def text(s,x,y,size=.8,back=False,angle=0):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));size=max(.8,size);t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.12));t.SetLayer(p.B_SilkS if back else p.F_SilkS);t.SetMirrored(back);t.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));b.Add(t)
# Movable field is the sole reference used in the assembly PDF.
placements={}
for fp in b.GetFootprints():
 ref=fp.GetReference();rf=fp.Reference();rf.SetLayer(p.F_Fab);rf.SetVisible(True);rf.SetPosition(fp.GetPosition());rf.SetTextSize(v(.65,.65));rf.SetTextThickness(p.FromMM(.1));rf.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));fp.Value().SetVisible(False)
 placements[ref]=[*p.ToMM(fp.GetPosition()),fp.GetOrientationDegrees()]
text('5-22V',3.2,9.6,.8,angle=90)
text('-',9.5,14.05,.8);text('+',13,13.75,.8)
for x in [37,47]:text('L',x,13.75,.8);text('H',x+3.5,14.05,.8)
text('120R',58.2,22,.75,angle=90)
text('SWD',34,5.7,.7,angle=90)
for n,x in enumerate([13,30,47],1):
 for label,px in [('+',x-3.5),('-',x),(f'S{n}',x+3.5)]:text(label,px,53.85,.8)
# Bottom guide is read with the board flipped, wire-entry edge still upward.
for s,y,size in [
 ('SENSOR CAN / REV B',17,1.8),('3 INPUTS  |  TEAM USE CAN',20.5,1.0),
 ('5-22V INPUT  /  COMMON GROUND',23,1.0),('0-30V SIGNALS  /  1 Mbit/s CAN',25.5,1.0),
 ('POWER: 1-2 = 5V   2-3 = VBAT',29,1.0),('300mA TOTAL PER SHARED RAIL',31.5,1.0),
 ('MODE: CLOSED = LOGIC',35,1.0),('OPEN = INDUSTRIAL',37.5,1.0),
 ('BIAS: 1-2 PORT / 3-4 3V3 / 5-6 GND',41, .9),
 ('POWER OFF BEFORE MOVING SHUNTS',55.5,.9),
 ('PROTOTYPE - VERIFY BEFORE ROBOT USE',66.5,.75)]:text(s,30,y,size,True)
# Exact physical pin labels next to exposed terminal solder rows.
for s,x in [('+IN',13),('GND',9.5),('H',40.5),('L',37),('H',50.5),('L',47)]:text(s,x,11.5,.7,True)
for x in [13,30,47]:
 for s,dx in [('+',-3.5),('G',0),('S',3.5)]:text(s,x+dx,61.5,.8,True)
text('TC2050: CUSTOM PIN MAP',23,13,.75,True)
(R/'hardware/design/final_placement.json').write_text(json.dumps(placements,indent=2)+'\n')
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
