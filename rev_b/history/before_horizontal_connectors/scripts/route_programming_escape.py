from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
starts=json.loads((R/'hardware/design/pogo_escape_starts.json').read_text());goals=json.loads((R/'hardware/design/pogo_escape_targets.json').read_text())
for net in ['+3V3','BOOT0','SWDIO','NRST','SWCLK','UART_TX','UART_RX']:
 s=starts[net];g=goals[net]
 subprocess.run(['kicad-python',str(R/'scripts/export_routing_geometry.py'),'hardware/FRC_Sensor_CAN.kicad_pcb'],check=True)
 with (R/f'reports/pogo_route_{net}.log').open('w') as f:
  subprocess.run(['python',str(R/'scripts/route_precise.py'),net,str(s[1]),str(s[2]),str(g[1]),str(g[2]),str(s[0]),str(g[0]),'.20','40','.6'],check=True,stdout=f)
 subprocess.run(['kicad-python',str(R/'scripts/apply_last_route.py'),net,'FRC_Sensor_CAN.kicad_pcb'],check=True)
 print('Routed',net,flush=True)
