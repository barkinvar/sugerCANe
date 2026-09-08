"""Verify a prototype archive and rebuild it in a new directory and Python venv.

Native KiCad/compiler/SPICE/JDK installations are reused from this workstation.
The archive is never changed. The extracted workspace is retained for inspection.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('archive',type=Path)
p.add_argument('--report',type=Path,default=ROOT/'release/reproduction.json')
args=p.parse_args()
archive=args.archive.resolve()
archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
work=Path(tempfile.mkdtemp(prefix='frc_sensor_can_reproduction_'))
print(f'Independent extraction: {work}',flush=True)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for entry in z.infolist():
        path=Path(entry.filename)
        assert not path.is_absolute() and '..' not in path.parts
        assert not stat.S_ISLNK(entry.external_attr>>16)
    z.extractall(work)
project=work/'FRC_Sensor_CAN_RevA'
manifest=json.loads((project/'release/manifest.json').read_text())
for entry in manifest['files']:
    assert hashlib.sha256((project/entry['path']).read_bytes()).hexdigest()==entry['sha256'],entry['path']
expected=json.loads((project/'reports/validation/run.json').read_text())['sha256']
env=os.environ.copy()
env.pop('VIRTUAL_ENV',None);env.pop('PYTHONPATH',None)
env['PATH']=':'.join(s for s in env['PATH'].split(':') if not s.endswith('/.venv/bin'))
log_path=work/'reproduction.log'
log=log_path.open('w')

def run(label,command):
    print(label,flush=True)
    log.write('\n'+label+'\n');log.flush()
    subprocess.run(['python3',str(ROOT/'scripts/progress.py'),label],check=True,stdout=subprocess.DEVNULL)
    process=subprocess.Popen(command,cwd=project,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    for line in process.stdout:
        log.write(line);log.flush()
        if line.startswith(('PASS ', 'Release validation:', 'All release validation')):
            print(line,end='',flush=True)
            subprocess.run(['python3',str(ROOT/'scripts/progress.py'),'Archive rebuild: '+line.strip()],check=True,stdout=subprocess.DEVNULL)
    code=process.wait()
    if code:raise RuntimeError(f'{label} failed ({code}); see {log_path}')

result={'archive':archive.name,'archive_sha256':archive_hash,'workspace':str(project),
        'method':'Verified every archived manifest entry, created a fresh Python venv from the lock, removed firmware build products, restored pinned driver dependencies, and ran the complete validation script.',
        'scope':'Same workstation/native toolchain; not a different-OS reproduction or physical hardware test.'}
try:
    run('Archive rebuild: create fresh Python environment',['uv','venv','--python','python3.12','.venv'])
    run('Archive rebuild: install exact locked Python packages',['uv','pip','sync','--python','.venv/bin/python','tools-requirements.lock'])
    shutil.rmtree(project/'firmware/build')
    run('Archive rebuild: complete design and firmware validation',['bash','scripts/validate_release.sh'])
    reproduced=json.loads((project/'reports/validation/run.json').read_text())
    assert reproduced['result']=='PASS'
    assert reproduced['sha256']==expected,'Validated source/artifact hashes differ after reproduction'
    result.update(result='PASS',identical_validated_hashes=expected,
                  manifest_entries_verified=len(manifest['files']))
except Exception as error:
    result.update(result='FAIL',error=str(error))
    raise
finally:
    result['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+'\n')
    log.close()
print(f'PASS: {len(expected)} validated inputs/artifacts reproduce. Report: {args.report}',flush=True)
