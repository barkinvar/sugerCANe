from pathlib import Path
import sexpdata as sx
p=Path(__file__).resolve().parents[1]/'hardware/FRC_Sensor_CAN.kicad_pcb'
x=sx.loads(p.read_text());x[:]=[q for q in x if not (isinstance(q,list) and q and str(q[0])=='gr_text')];p.write_text(sx.dumps(x)+'\n')
