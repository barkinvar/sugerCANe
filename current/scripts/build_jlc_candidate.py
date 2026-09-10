"""Package a CAD-checked JLC quotation candidate, explicitly without release approval."""
from pathlib import Path
import hashlib, json, zipfile

R=Path(__file__).resolve().parents[1]
checks=json.loads((R/'reports/release_checks.json').read_text())
assert checks['revision']=='H SC12' and checks['simulation_deferred_by_user'] is True
assert checks['status'].startswith('HOLD:')
for path,digest in checks['input_hashes'].items():
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,('Stale candidate evidence',path)
status='REVIEW / QUOTATION ONLY. Simulations await user approval; MCU stock and final factory stack are unresolved. Not authorized for manufacture.'
gerber=R/'order/sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip'
with zipfile.ZipFile(gerber,'w',zipfile.ZIP_DEFLATED) as z:
 fabrication=[]
 for p in sorted((R/'output/fabrication').iterdir()):
  if p.suffix in ('.gtl','.gbl','.g1','.g2','.gts','.gbs','.gtp','.gbp','.gto','.gbo','.gm1','.gbrjob','.drl'):
   z.write(p,p.name);fabrication.append(p.name)
 assert len(fabrication)==14 and sum(p.endswith('.drl') for p in fabrication)==2
 z.writestr('REVIEW_ONLY.txt',status+'\nSee the matching JLC review package for the required stack and BOM.\n')
files=['bom/BOM_JLCPCB.csv','bom/Factory_BOM.csv','bom/Hand_solder_BOM.csv','bom/ACCESSORIES.csv',
 'output/assembly/CPL_JLCPCB.csv','output/assembly/top_assembly.pdf','output/assembly/schematic.pdf',
 'output/documentation/BOM_RevH_SC12.pdf','docs/JLC_SOURCING.md','docs/FACTORY_ORDER.md',
 'firmware/build/factory.hex','firmware/build/application.sc12','tools/program_factory.tcl',
 'reports/release_checks.json','reports/manufacturing/jlc_sourcing.json',str(gerber.relative_to(R))]
manifest=dict(status=status,files={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files})
dest=R/'order/sugarCANe_RevH_JLC_REVIEW_ONLY.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(R/p,p)
 z.writestr('REVIEW_ONLY.txt',status+'\nFactory scope: 130 top SMT placements. Ten THT parts and three caps are hand fitted.\n')
 z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for p,digest in manifest['files'].items():assert hashlib.sha256(z.read(p)).hexdigest()==digest
for p in [gerber,dest]:
 p.with_suffix('.zip.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
print('Wrote and verified review-only Gerber and JLC packages. No manufacturing release.')
