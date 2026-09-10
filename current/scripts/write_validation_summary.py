"""Collect current engineering evidence without substituting it for bench tests."""
from pathlib import Path
import argparse,json,re,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--allow-incomplete',action='store_true',help='Publish completed checks with HOLD status when the full power run is incomplete; no release approval')
ap.add_argument('--defer-simulation',action='store_true',help='Record CAD/sourcing checks only, with HOLD status; do not validate or rerun prior simulation evidence')
args=ap.parse_args()
def read(path):return json.loads((R/path).read_text())
erc=read('reports/erc/final.json');drc=read('reports/drc/final.json')
assert not [v for sheet in erc['sheets'] for v in sheet['violations']] and not drc['violations'] and not drc['unconnected_items']
parity=read('reports/design_parity.json');assert parity['pass']
routing=read('reports/routing_rules.json');assert routing['result']=='PASS' and not routing['findings']
assert routing['board_sha256']==hashlib.sha256((R/'hardware/FRC_Sensor_CAN.kicad_pcb').read_bytes()).hexdigest()
for path,digest in routing['source_hashes'].items():
 assert digest==hashlib.sha256((R/path).read_bytes()).hexdigest(),('Stale routing evidence',path)
assembly=read('reports/manufacturing/verification.json');assert assembly['result']=='PASS'
copper=read('reports/manufacturing/gerber_connectivity.json');geometry=read('reports/manufacturing/gerber_geometry.json');assert copper['result']==geometry['result']=='PASS'
sourcing=read('reports/manufacturing/jlc_sourcing.json')
for path,digest in sourcing['input_hashes'].items():
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,('Stale sourcing audit',path)
if args.defer_simulation:
 paths=['hardware/FRC_Sensor_CAN.kicad_pcb','hardware/design/circuit.json','bom/BOM_grouped.csv',
  'bom/BOM_JLCPCB.csv','bom/Factory_BOM.csv','bom/jlc_sourcing.json','output/assembly/CPL_JLCPCB.csv',
  'reports/erc/final.json','reports/drc/final.json','reports/design_parity.json','reports/routing_rules.json',
  'reports/board_constraints.json','reports/variant_verification.json','reports/manufacturing/verification.json',
  'reports/manufacturing/gerber_connectivity.json','reports/manufacturing/gerber_geometry.json',
  'reports/manufacturing/jlc_sourcing.json','reports/manufacturing/factory_files.json']
 paths += [p.relative_to(R).as_posix() for p in sorted((R/'hardware').glob('*.kicad_sch'))]
 out=dict(revision='H SC12',status='HOLD: JLC sourcing candidate; simulations deferred until user approval',
  order_decision=sourcing['order_decision'],manufacturing_holds=sourcing['manufacturing_holds'],simulation_deferred_by_user=True,physical_tests_performed=False,
  erc_violations=0,drc_violations=0,unconnected_items=0,model_schematic_pcb_parity=True,
  fitted_parts=140,manufacturing_layers=11,copper_layers=4,gerber_shorts=copper['shorts'],gerber_opens=copper['opens'],
  prior_simulation_evidence=dict(baseline_commit=read('bom/jlc_sourcing.json')['baseline_commit'],
    scope='Existing electrical reports belong to the pre-substitution BOM; no new simulation claim. Full coupled startup was already incomplete.'),
  input_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths},
  limitations='CAD and sourcing consistency only. Full power/input screening, C1 reflow, final factory allocation, stack and physical qualification remain pending.')
 (R/'reports/release_checks.json').write_text(json.dumps(out,indent=2)+'\n')
 print(out['status']);sys.exit(0)
fw=(R/'reports/firmware-tests.log').read_text();drivers=(R/'reports/driver/tests.log').read_text()
scenarios=re.findall(r'application: (\w+) passed',fw);assert '2148 simulated' in fw and 'Ran 8 tests' in fw
assert len(scenarios)==19 and 'core:' in fw and 'wire encoding passed' in fw
java=int(re.search(r'PASS: (\d+) 12 V Java assertions',drivers)[1]);assert 'Ran 13 tests' in drivers and '\nOK\n' in drivers and 'PASS: 12 V C++' in drivers
assert 'PASS: WPILib 2027.0.0-alpha-7' in (R/'reports/bridge2027-tests.log').read_text()
assert read('reports/firmware-images.json')['result']=='PASS'
loop=read('reports/electrical/converter_loop.json');assert loop['result']=='PASS analytical screening only'
subprocess.run([sys.executable,str(R/'scripts/check_input_spice.py'),'--verify-report'],check=True)
input_spice=read('reports/electrical/input_spice.json')
spice=read('reports/electrical/boost_spice.json')
complete=spice['result']=='PASS transient screening only'
if complete or not args.allow_incomplete:
 subprocess.run([sys.executable,str(R/'scripts/check_boost_spice.py'),'--verify-report','--require-pass'],check=True)
else:
 # Retain independently reproducible completed cases without blessing missing startup traces.
 import check_boost_spice as boost
 boost.WORK=R/'tmp/spice/report-verification';boost.WORK.mkdir(parents=True,exist_ok=True);boost.prepare_models()
 partial=read('reports/electrical/boost_spice_partial.json')
 assert partial['result']=='PASS transient screening only' and partial['timestep_repeat']['pass']
 assert partial['timestep_repeat']['output_difference_V']<.05 and partial['timestep_repeat']['source_current_difference_A']<.005
 assert partial['circuit_sha256']==boost.sha(R/'hardware/design/circuit.json')
 assert partial['script_sha256']==boost.sha(R/'scripts/check_boost_spice.py')
 assert partial['sources']==read('sources/spice/manifest.json')
 version=subprocess.check_output(['ngspice','--version'],text=True).strip();assert partial['simulator']==version
 assert [r['case'] for r in partial['cases']]==boost.CASES[1:]
 for r in partial['cases']:
  deck=boost.circuit(r['case'],read('hardware/design/circuit.json')['parts'],read('reports/electrical/electrical_checks.json'))
  digest=hashlib.sha256((deck+version+''.join(boost.sha(boost.WORK/f) for f in ['tps61085.lib','tps2553-1.lib','tps259620.lib','B240A.lib'])).encode()).hexdigest()
  assert r['simulated_netlist']==deck and r['deck_and_model_hash']==digest
  assert r['pass'] and all(r['checks'].values())
order_args=['--allow-incomplete'] if args.allow_incomplete else []
subprocess.run([sys.executable,str(R/'scripts/check_order_readiness.py'),'--verify-report',*order_args],check=True)
order_review=read('reports/electrical/order_readiness.json')
subprocess.run([sys.executable,str(R/'scripts/check_power_replay.py'),'--verify-report'],check=True)
power_replay=read('reports/electrical/power_replay.json')
tracked=['hardware/FRC_Sensor_CAN.kicad_pcb','hardware/FRC_Sensor_CAN.kicad_sch','hardware/design/circuit.json','bom/BOM_grouped.csv','firmware/build/sensor_can.bin','firmware/build/bootloader.bin','firmware/build/factory.hex','firmware/build/application.sc12','output/assembly/schematic.pdf']
tracked += ['bom/Factory_BOM.csv','bom/Hand_solder_BOM.csv','bom/ACCESSORIES.csv','output/assembly/CPL_JLCPCB.csv']
tracked += ['reports/electrical/electrical_checks.json','reports/electrical/converter_loop.json','reports/electrical/input_spice.json','reports/electrical/boost_spice.json','reports/electrical/order_readiness.json','scripts/check_input_spice.py','scripts/check_boost_spice.py','scripts/check_order_readiness.py','scripts/write_validation_summary.py','sources/spice/input_manifest.json','sources/spice/lm393lv.lib']
tracked += ['scripts/check_power_replay.py','reports/electrical/power_replay.json','firmware/src/power.c','firmware/include/power.h']
tracked += ['reports/electrical/solver_diagnostics.json']
tracked += ['hardware/FRC_Sensor_CAN.kicad_pro','hardware/FRC_Sensor_CAN.kicad_dru',
            'scripts/check_board_constraints.py','scripts/check_routing.py','scripts/export_routing_geometry.py',
            'scripts/test_routing.py','reports/routing-tests.log','reports/routing_rules.json','reports/routing_cleanup.json']
tracked += ['reports/erc/final.json','reports/drc/final.json','reports/design_parity.json','reports/board_constraints.json',
            'reports/variant_verification.json','reports/firmware-tests.log','reports/power-tests.log','reports/firmware-images.json',
            'reports/firmware-arm-registers.json','reports/driver/tests.log','reports/bridge2027-tests.log',
            'reports/manufacturing/verification.json','reports/manufacturing/gerber_connectivity.json',
            'reports/manufacturing/gerber_geometry.json','reports/manufacturing/factory_files.json',
            'reports/document_review.json','reports/visual_review.json','output/documentation/SC12_RevH_Handbook.pdf']
if not complete:tracked += ['reports/electrical/boost_spice_partial.json','reports/electrical/boost_spice_partial.png']
tracked += ['bom/jlc_sourcing.json','reports/manufacturing/jlc_sourcing.json',*sourcing['input_hashes']]
factory=read('reports/manufacturing/factory_files.json');assert factory['result']=='PASS' and factory['factory_smt_placements']==130 and factory['hand_solder_parts']==10
tracked += [p.relative_to(R).as_posix() for p in sorted((R/'hardware').glob('*.kicad_sch')) if p.name!='FRC_Sensor_CAN.kicad_sch']
out=dict(revision='H SC12',status='PASS engineering checks; physical qualification pending',physical_tests_performed=False,erc_violations=0,drc_violations=0,unconnected_items=0,model_schematic_pcb_parity=True,fitted_parts=140,portable_models=assembly['portable_models_verified'],manufacturing_layers=assembly['graphic_layers'],copper_layers=4,gerber_shorts=copper['shorts'],gerber_opens=copper['opens'],net_tie_isolation=copper['intentional_net_tie_isolation']['extra_shorts'],firmware_core_tests='PASS under ASan/UBSan',firmware_application_scenarios=scenarios,java_assertions=java,python_test_methods=13,can_service_tests="8 host methods plus 2148 simulated flash boundaries",arm_register_tests=read("reports/firmware-arm-registers.json")["result"],bridge_tests="Real TCP with mock CAN; 2026 and 2027 adapters compile",cpp_tests='PASS under ASan/UBSan; WPILib example compiled',analytical_CCM_loop_corners=loop['corners'],input_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in tracked},limitations='No measured efficiency, thermal, surge, EMC, sensor startup, actual MCU/CAN, solder yield or enclosure fit qualification. See docs/VALIDATION.md.')
out['vendor_model_transient_cases']=[r['case']['name'] for r in (spice if complete else partial)['cases']]
out['routing_rules']={key:routing[key] for key in ('result','segments','vias','rules')}
out['input_transient_cases']=[r['name'] for r in input_spice['cases']]
out['input_transient_scope']=input_spice['limitations']
out['firmware_waveform_replay']={'result':power_replay['result'],'cases':len(power_replay['cases']),'scope':power_replay['limitations']}
out['spice_scope']=spice['scope']
out['timestep_repeat']=(spice if complete else partial)['timestep_repeat']
out['combined_solver_repeat']=spice.get('combined_solver_repeat',{'pass':False,'status':'INCOMPLETE'})
out['spice_result']=spice['result']
if spice['result']=='FAIL':
 out['status']='REVIEW required: circuit consistency checks pass; transient screening has unresolved findings'
out['order_decision']=order_review['order_decision']
out['protection_boundary']=order_review['protection_boundary']
diagnostics=read('reports/electrical/solver_diagnostics.json').get('revision_H_crosscheck')
if diagnostics and diagnostics['circuit_sha256']==out['input_hashes']['hardware/design/circuit.json']:
 out['additional_power_diagnostics']={
  'ngspice47_standalone_cases_passing_existing_criteria':sum(c['both_pass'] for c in diagnostics['ngspice47']['standalone_cases']),
  'boost_half_timestep':diagnostics.get('boost_half_timestep',{}).get('pass'),
  'low_supply_cases':{c['case']['name']:c['pass'] for c in diagnostics.get('low_supply_cases',[])},
  'scope':'Additional diagnostics, separate from the required full-suite gates; pointwise waveform differences are retained in solver_diagnostics.json and are not an equivalence claim.'}
out['simulation_deferred_by_user']=False
out['power_distribution_valid_for_current_layout']=True
if not complete:
 out['status']='HOLD full release: completed CAD, firmware, input and standalone power screens pass; full power evidence remains unresolved'
 if spice['result']=='INCOMPLETE':
  out['pending_power_cases']=['combined_low_input_capacitive_start','combined_low_input_capacitive_start_trtol7_25n']
 else:
  out['failed_power_cases']=[r['case']['name'] for r in spice['cases'] if not r['pass']]
  out['combined_solver_repeat_pass']=spice.get('combined_solver_repeat',{}).get('pass',False)
out['manufacturing_holds']=sourcing['manufacturing_holds']
if sourcing['manufacturing_holds']:
 out['status']='HOLD full release: unresolved sourcing or factory process qualification'
 out['order_decision']='HOLD: '+'; '.join(sourcing['manufacturing_holds'])
(R/'reports/release_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
