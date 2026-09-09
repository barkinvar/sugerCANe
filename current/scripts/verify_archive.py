"""Validate delivered hashes and native CAD from a temporary extracted package."""
from pathlib import Path
import json,zipfile,tempfile,hashlib,subprocess
R=Path(__file__).resolve().parents[1];zpath=R/'release/FRC_Sensor_CAN_RevF_SC12_Prototype.zip'
assert hashlib.sha256(zpath.read_bytes()).hexdigest()==(zpath.with_suffix('.zip.sha256')).read_text().split()[0]
with tempfile.TemporaryDirectory(prefix='sc_lite_release_') as t:
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None;z.extractall(t)
 base=Path(t)/'SC12_RevF';manifest=json.loads((base/'manifest.json').read_text())
 for e in manifest['files']:
  p=base/e['path'];assert p.stat().st_size==e['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],e['path']
 for kind,command,extension in [('pcb','drc','kicad_pcb'),('sch','erc','kicad_sch')]:
  subprocess.run(['kicad-cli',kind,command,'--exit-code-violations','--severity-all','--format','json','-o',str(Path(t)/(command+'.json')),str(base/'hardware'/('FRC_Sensor_CAN.'+extension))],check=True)
 subprocess.run(['kicad-python',str(base/'scripts/check_design_parity.py')],check=True)
 subprocess.run(['kicad-python',str(base/'scripts/check_board_constraints.py')],check=True,stdout=subprocess.DEVNULL)
out=dict(result='PASS',archive=zpath.name,sha256=hashlib.sha256(zpath.read_bytes()).hexdigest(),files_verified=len(manifest['files']),extracted_erc_drc_and_parity='PASS',physical_qualification=False)
(R/'release/verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
