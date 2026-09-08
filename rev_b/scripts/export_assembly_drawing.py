"""Plot an uncluttered assembly drawing without changing the native board.

KiCad footprints can contain both a movable reference field and an internal
${REFERENCE} graphic on F.Fab. Hide only the redundant internal label in a
throwaway copy. Keep actual silkscreen, body outlines and pin-one indicators.
"""
from pathlib import Path
import subprocess,tempfile
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
b=sx.loads((ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb').read_text())
removed=0
for fp in b:
    if not isinstance(fp,list) or not fp or str(fp[0])!='footprint':continue
    kept=[]
    for item in fp:
        redundant=(isinstance(item,list) and len(item)>2 and str(item[0])=='fp_text'
                   and str(item[1])=='user' and item[2] in ('${REFERENCE}','%R')
                   and any(isinstance(c,list) and len(c)>1 and str(c[0])=='layer' and c[1]=='F.Fab' for c in item))
        if redundant:removed+=1
        else:kept.append(item)
    fp[:]=kept
with tempfile.TemporaryDirectory(prefix='sensor_can_assembly_') as folder:
    path=Path(folder)/'assembly.kicad_pcb';path.write_text(sx.dumps(b))
    subprocess.run(['kicad-cli','pcb','export','pdf','--mode-single','--layers','F.Fab,F.Silkscreen,Edge.Cuts',
                    '--exclude-value','--scale','2','--black-and-white','-o',str(ROOT/'output/assembly/top_assembly.pdf'),str(path)],check=True)
print('Assembly-only redundant labels removed:',removed)
