"""Validate delivered hashes and native CAD from a temporary extracted package."""
from pathlib import Path
import json,zipfile,tempfile,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[1];zpath=R/'release/FRC_Sensor_CAN_RevH_SC12_Prototype.zip'
assert hashlib.sha256(zpath.read_bytes()).hexdigest()==(zpath.with_suffix('.zip.sha256')).read_text().split()[0]
with tempfile.TemporaryDirectory(prefix='sc_lite_release_') as t:
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None;z.extractall(t)
 base=Path(t)/'SC12_RevH';manifest=json.loads((base/'manifest.json').read_text())
 for e in manifest['files']:
  p=base/e['path'];assert p.stat().st_size==e['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],e['path']
 for kind,command,extension in [('pcb','drc','kicad_pcb'),('sch','erc','kicad_sch')]:
  subprocess.run(['kicad-cli',kind,command,'--exit-code-violations','--severity-all','--format','json','-o',str(Path(t)/(command+'.json')),str(base/'hardware'/('FRC_Sensor_CAN.'+extension))],check=True)
 subprocess.run(['kicad-python',str(base/'scripts/check_design_parity.py')],check=True)
 subprocess.run(['kicad-python',str(base/'scripts/check_board_constraints.py')],check=True,stdout=subprocess.DEVNULL)
 subprocess.run([sys.executable,str(base/'scripts/check_boost_spice.py'),'--verify-report'],check=True)
 subprocess.run([sys.executable,str(base/'scripts/check_order_readiness.py'),'--verify-report'],check=True)
 spice_result=json.loads((base/'reports/electrical/boost_spice.json').read_text())['result']
 order_decision=json.loads((base/'reports/electrical/order_readiness.json').read_text())['order_decision']
out=dict(result='PASS archive integrity',archive=zpath.name,sha256=hashlib.sha256(zpath.read_bytes()).hexdigest(),files_verified=len(manifest['files']),extracted_erc_drc_and_parity='PASS',simulation_screening=spice_result,order_decision=order_decision,physical_qualification=False)
(R/'release/verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
