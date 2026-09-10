"""Package a CAD-checked JLC quotation candidate, explicitly without release approval."""
from pathlib import Path
import hashlib, json, zipfile
from layout_contract import WIDTH, HEIGHT, BOTTOM_REFERENCES

R=Path(__file__).resolve().parents[1]
checks=json.loads((R/'reports/release_checks.json').read_text())
assert checks['revision']=='H SC12'
assert checks['status'].startswith('HOLD')
for path,digest in checks['input_hashes'].items():
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,('Stale candidate evidence',path)
power_status=('Required downstream power/input/firmware engineering screens passed; upstream buck and physical qualification remain outside that transient evidence.'
              if checks.get('spice_result')=='PASS transient screening only' else
              'Full power-transient evidence is still incomplete or failing; read reports/release_checks.json.')
status=f'REVIEW / QUOTATION ONLY. Compact Rev H: {WIDTH} x {HEIGHT} mm. Factory fits {129-len(BOTTOM_REFERENCES)} top and {len(BOTTOM_REFERENCES)} bottom SMT parts / 54 types, including C1 and D10. C25/C26 are 20 pF. U1 is LMR51430XDDCR; L1 is SRP7028A-8R2M (8.2 uH). U5 is omitted from BOM/CPL and stencil; user buys STM32F042K6T6 from DigiKey and hand solders it, plus ten THT parts and three loose caps. '+power_status+' Factory two-sided stack/process/inspection quotation remains pending. Not authorized for manufacture.'
stencil=json.loads((R/'reports/manufacturing/factory_stencil.json').read_text())
assert stencil['result']=='PASS' and stencil['removed_u5_apertures']==32
for path,digest in stencil['input_hashes'].items():
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,('Stale stencil evidence',path)
assert hashlib.sha256((R/stencil['output']).read_bytes()).hexdigest()==stencil['output_sha256']
gerber=R/'order/sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip'
with zipfile.ZipFile(gerber,'w',zipfile.ZIP_DEFLATED) as z:
 fabrication=[]
 for p in sorted((R/'output/fabrication').iterdir()):
  if p.suffix in ('.gtl','.gbl','.g1','.g2','.gts','.gbs','.gtp','.gbp','.gto','.gbo','.gm1','.gbrjob','.drl'):
   z.write(R/stencil['output'] if p.relative_to(R).as_posix()==stencil['source'] else p,p.name);fabrication.append(p.name)
 assert len(fabrication)==14 and sum(p.endswith('.drl') for p in fabrication)==2
 z.writestr('REVIEW_ONLY.txt',status+'\nSee the matching JLC review package for the required stack and BOM.\n')
files=['bom/BOM_JLCPCB.csv','bom/Factory_BOM.csv','bom/Hand_solder_BOM.csv','bom/ACCESSORIES.csv','bom/assembly_plan.json','bom/DigiKey_5_boards.csv','bom/DigiKey_10_boards.csv',
 'output/assembly/CPL_JLCPCB.csv','output/assembly/top_assembly.pdf','output/assembly/bottom_assembly.pdf','output/assembly/schematic.pdf','docs/COMPACT_BOARD.md','hardware/design/layout_contract.json',
 'output/documentation/BOM_RevH_SC12.pdf','output/documentation/ORDER_GUIDE.pdf','output/documentation/MCU_hand_solder_map.pdf','docs/JLC_SOURCING.md','docs/FACTORY_ORDER.md','docs/ASSEMBLY.md','docs/STATUS_AND_PROGRAMMING.md','docs/WIRING.md','docs/FIXTURE.md','docs/VALIDATION.md','docs/CAN_SERVICE.md',
 'firmware/build/factory.hex','firmware/build/application.sc12','tools/program_factory.tcl',
 'reports/release_checks.json','reports/manufacturing/jlc_sourcing.json','reports/manufacturing/factory_files.json','reports/manufacturing/factory_stencil.json','output/assembly/factory_top_paste.gtp',
 'docs/ROUTING_RULES.md','reports/routing_rules.json','reports/routing_cleanup.json',
 'reports/electrical/order_readiness.json',
 'hardware/design/routing_widths.json','reports/compact/layout_verification.json','reports/compact/source_snapshot.json',
 'reports/manufacturing/gerber_connectivity.json','reports/manufacturing/gerber_geometry.json','reports/manufacturing/verification.json',
 'output/review/board_top.png','output/review/board_bottom.png','output/review/board_3d_final.png','output/review/board_connectors.png','output/review/size_comparison.png',
 'reports/compact/completed_simulation_sources.json','reports/compact/u8_route_fix.json','output/review/u8_switch_route_fix.png',
 'reports/compact/pad_contact_sweep.json','output/review/pad_contact_sweep.png',
 'bom/jlc_sourcing.json',str(gerber.relative_to(R))]
preview=json.loads((R/'reports/manufacturing/preview_source.json').read_text())
assert hashlib.sha256((R/'scripts/render_gerber_previews.py').read_bytes()).hexdigest()==preview['script_sha256']
for name,digest in preview['sha256'].items():
 assert hashlib.sha256((R/'output/fabrication'/name).read_bytes()).hexdigest()==digest,('Stale copper preview source',name)
for name,digest in preview['output_sha256'].items():
 assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,('Changed copper preview',name)
files += ['reports/manufacturing/preview_source.json',*preview['output_sha256']]
files += [d['file'] for d in json.loads((R/'bom/jlc_sourcing.json').read_text())['datasheets']]
files += [p.relative_to(R).as_posix() for p in sorted((R/'host').glob('*.py')) if not p.name.startswith('test_')]
files += ['tools/fixture_measurements.template.json','tools-requirements.lock']
packages=json.loads((R/'reports/manufacturing/jlc_packages.json').read_text())
assert packages['result']=='PASS package and placement-file checks; factory process approval pending'
assert packages['board_sha256']==hashlib.sha256((R/'hardware/FRC_Sensor_CAN.kicad_pcb').read_bytes()).hexdigest()
for path,digest in packages['input_hashes'].items():
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,('Stale package review',path)
files += ['docs/JLC_PACKAGE_REVIEW.md','bom/jlc_package_review.json',
          'reports/manufacturing/jlc_packages.json','sources/datasheets/jlc_package_drawings.pdf']
files += ['reports/electrical/component_margins.json','reports/manufacturing/clock_load_change.json','reports/manufacturing/buck_margin_change.json','reports/manufacturing/final_native_recheck.json',
          'docs/ORDER_READINESS.md','reports/electrical/boost_spice.json',
          'reports/electrical/input_spice.json','reports/electrical/power_replay.json']
manifest=dict(status=status,files={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files})
dest=R/'order/sugarCANe_RevH_JLC_REVIEW_ONLY.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(R/p,p)
 z.writestr('REVIEW_ONLY.txt',status+'\nRead docs/FACTORY_ORDER.md first. Do not upload this whole documentation archive as the Gerber ZIP.\n')
 z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for p,digest in manifest['files'].items():assert hashlib.sha256(z.read(p)).hexdigest()==digest
for p in [gerber,dest]:
 p.with_suffix('.zip.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
print('Wrote and verified review-only Gerber and JLC packages. No manufacturing release.')
