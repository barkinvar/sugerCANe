"""Bounded routing trials; failed trials do not alter the board. Native DRC follows."""
from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
tasks=[
 ('+3V3',38.05,37.5,39.73,44.975,0,0,.2),
 ('+3V3',38.05,37.5,27.75,39,0,0,.2),
 
 
 ('LOW_SEL3',48,44.5,56.5,44.5875,1,0,.18),
 ('BIAS_3V3_3',53.5,37.15,58.5,46.4125,0,0,.18),
 ('+3V3',1.5,42.9125,3.6103,43.0124,0,1,.18),
 ('+3V3',3.6103,43.0124,3.6103,37.1908,1,1,.18),
 ('+3V3',20.9125,47,27.75,39,0,0,.18),
 ('VBAT_FAULT_N',3.75,42.325,43.2,23.825,1,0,.18),
]
result=[]
with (R/'reports/connection_trials.log').open('w') as log:
 for t in tasks:
  subprocess.run(['kicad-python',str(R/'scripts/export_routing_geometry.py'),'hardware/finishing.kicad_pcb'],check=True)
  cmd=['python',str(R/'scripts/route_last_connection.py'),*map(str,t),'30','.6']
  r=subprocess.run(cmd,stdout=log,stderr=log)
  if not r.returncode:subprocess.run(['kicad-python',str(R/'scripts/apply_last_route.py'),t[0]],check=True)
  item=dict(task=t,routed=r.returncode==0);result.append(item);print(item,flush=True)
(R/'reports/connection_trials.json').write_text(json.dumps(result,indent=2)+'\n')
