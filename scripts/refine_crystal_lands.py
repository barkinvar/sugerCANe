"""One-time Rev A crystal-pad refinement. Native PCB remains authoritative."""
from pathlib import Path
import uuid
import sexpdata as s
root=Path(__file__).resolve().parents[1]
path=root/'hardware/FRC_Sensor_CAN.kicad_pcb'
board=s.loads(path.read_text())
key=lambda x:str(x[0]) if isinstance(x,list) and x else ''
child=lambda x,k:next(v for v in x if key(v)==k)
f=next(f for f in board if key(f)=='footprint' and any(key(v)=='property' and v[1:3]==['Reference','Y1'] for v in f))
f[1]='FRC_Sensor_CAN:Abracon_ABM3B_5.0x3.2mm'
child(f,'descr')[1]='Abracon ABM3B recommended land pattern; https://abracon.com/Resonators/abm3b.pdf page 3. KiCad generic body/model retained under original license.'
for v in f:
    if key(v)=='pad':
        n=int(v[1]);v[3]=s.Symbol('rect')
        child(v,'at')[1:3]=[-2 if n in (1,4) else 2,1.2 if n in (1,2) else -1.2]
        child(v,'size')[1:]=[1.8,1.2]
        v[:]=[a for a in v if key(a)!='roundrect_rratio']
    elif key(v)=='fp_rect' and child(v,'layer')[1]=='F.CrtYd':
        child(v,'start')[1:]=[-3.15,-2.05];child(v,'end')[1:]=[3.15,2.05]
f[:]=[v for v in f if not (key(v)=='fp_line' and child(v,'layer')[1]=='F.SilkS')]
for coords in [(-.8,-1.8,.8,-1.8),(-.8,1.8,.8,1.8),(-3.12,1.8,-3.12,2.05),(-3.12,2.05,-2.65,2.05)]:
    x1,y1,x2,y2=coords
    f.append(s.loads(f'(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uuid.uuid4()}"))'))
path.write_text(s.dumps(board)+'\n')
print('Y1 changed to Abracon 1.8x1.2mm lands on 4.0x2.4mm centers; all positions retained.')
