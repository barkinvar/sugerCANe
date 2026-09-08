"""Collect current engineering evidence without substituting it for bench tests."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
def read(path):return json.loads((R/path).read_text())
erc=read('reports/erc/final.json');drc=read('reports/drc/final.json')
assert not [v for sheet in erc['sheets'] for v in sheet['violations']] and not drc['violations'] and not drc['unconnected_items']
parity=read('reports/design_parity.json');assert parity['pass']
assembly=read('reports/manufacturing/verification.json');assert assembly['result']=='PASS'
copper=read('reports/manufacturing/gerber_connectivity.json');geometry=read('reports/manufacturing/gerber_geometry.json');assert copper['result']==geometry['result']=='PASS'
fw=(R/'reports/firmware-tests.log').read_text();drivers=(R/'reports/driver/tests.log').read_text()
scenarios=re.findall(r'application: (\w+) passed',fw);assert '2148 simulated' in fw and 'Ran 6 tests' in fw
assert len(scenarios)==16 and 'core:' in fw and 'wire encoding passed' in fw
java=int(re.search(r'PASS: (\d+) 12 V Java assertions',drivers)[1]);assert 'Ran 11 tests' in drivers and '\nOK\n' in drivers and 'PASS: 12 V C++' in drivers
assert 'PASS: WPILib 2027.0.0-alpha-7' in (R/'reports/bridge2027-tests.log').read_text()
assert read('reports/firmware-images.json')['result']=='PASS'
loop=read('reports/electrical/converter_loop.json');assert loop['result']=='PASS analytical screening only'
tracked=['hardware/FRC_Sensor_CAN.kicad_pcb','hardware/FRC_Sensor_CAN.kicad_sch','hardware/design/circuit.json','bom/BOM_grouped.csv','firmware/build/sensor_can.bin','firmware/build/bootloader.bin','firmware/build/factory.hex','firmware/build/application.sc12','output/assembly/schematic.pdf']
tracked += ['bom/Factory_BOM.csv','bom/Hand_solder_BOM.csv','bom/ACCESSORIES.csv','output/assembly/CPL_JLCPCB.csv']
factory=read('reports/manufacturing/factory_files.json');assert factory['result']=='PASS' and factory['factory_smt_placements']==98 and factory['hand_solder_parts']==9
tracked += [p.relative_to(R).as_posix() for p in sorted((R/'hardware').glob('*.kicad_sch')) if p.name!='FRC_Sensor_CAN.kicad_sch']
out=dict(revision='D-2 SC12',status='PASS engineering checks; physical qualification pending',physical_tests_performed=False,erc_violations=0,drc_violations=0,unconnected_items=0,model_schematic_pcb_parity=True,fitted_parts=107,portable_models=assembly['portable_models_verified'],manufacturing_layers=assembly['graphic_layers'],copper_layers=4,gerber_shorts=copper['shorts'],gerber_opens=copper['opens'],net_tie_isolation=copper['intentional_net_tie_isolation']['extra_shorts'],firmware_core_tests='PASS under ASan/UBSan',firmware_application_scenarios=scenarios,java_assertions=java,python_test_methods=11,can_service_tests="6 host methods plus 2148 simulated flash boundaries",arm_register_tests=read("reports/firmware-arm-registers.json")["result"],bridge_tests="Real TCP with mock CAN; 2026 and 2027 adapters compile",cpp_tests='PASS under ASan/UBSan; WPILib example compiled',analytical_CCM_loop_corners=loop['corners'],input_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in tracked},limitations='No measured efficiency, thermal, surge, EMC, sensor startup, actual MCU/CAN, solder yield or enclosure fit qualification. See docs/VALIDATION.md.')
(R/'reports/release_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
