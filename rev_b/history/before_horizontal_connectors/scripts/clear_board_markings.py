from pathlib import Path
import sexpdata as s
f=Path(__file__).resolve().parents[1]/'hardware/FRC_Sensor_CAN.kicad_pcb'
a=s.loads(f.read_text());a[:]=[z for z in a if not(isinstance(z,list) and str(z[0])=='gr_text')];f.write_text(s.dumps(a))
