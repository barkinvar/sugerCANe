"""Verify the extracted manual-MCU quotation packet against native references."""
from collections import Counter
from pathlib import Path
import csv,hashlib,io,json,tempfile,zipfile
from gerbonara import GerberFile
from gerbonara.graphic_objects import Flash

R=Path(__file__).resolve().parents[1]
packet=R/'order/sugarCANe_RevH_JLC_REVIEW_ONLY.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(packet) as z:
    assert z.testzip() is None
    manifest=json.loads(z.read('manifest.json'))
    for name,digest in manifest['files'].items():
        assert sha(z.read(name))==digest==sha((R/name).read_bytes()),name
    readcsv=lambda name:list(csv.DictReader(io.StringIO(z.read(name).decode())))
    bom=readcsv('bom/BOM_JLCPCB.csv');cpl=readcsv('output/assembly/CPL_JLCPCB.csv')
    hand=readcsv('bom/Hand_solder_BOM.csv')
    factory=Counter(ref.strip() for row in bom for ref in row['Designator'].split(','))
    manual=Counter(ref.strip() for row in hand for ref in row['References'].split(','))
    all_parts={r['reference'] for r in csv.DictReader((R/'bom/BOM_per_reference.csv').open())}
    assert len(bom)==54 and len(factory)==len(cpl)==129
    clock_caps=[row for row in bom if 'C25' in {ref.strip() for ref in row['Designator'].split(',')}]
    assert len(clock_caps)==1
    clock_caps=clock_caps[0]
    assert {ref.strip() for ref in clock_caps['Designator'].split(',')}=={'C25','C26'}
    assert clock_caps['LCSC Part #']=='C105173' and clock_caps['Comment']=='CC0805JRNPO9BN200'
    for ref,mpn,code in [('U1','LMR51430XDDCR','C5185863'),('L1','SRP7028A-8R2M','C2041815')]:
        row=next(r for r in bom if r['Designator']==ref)
        assert row['Comment']==mpn and row['LCSC Part #']==code
    assert factory==Counter(r['Designator'] for r in cpl)
    assert 'U5' not in factory and manual['U5']==1
    assert set(factory).isdisjoint(manual) and set(factory)|set(manual)==all_parts
    assert set(factory.values())==set(manual.values())=={1}
    native={c['reference']:c for c in json.loads((R/'reports/manufacturing/board_manifest.json').read_text())['components']}
    for row in cpl:
        n=native[row['Designator']]
        assert row['Layer']=='Top'
        assert abs(float(row['Mid X'].removesuffix('mm'))-n['x_mm'])<1e-5
        assert abs(float(row['Mid Y'].removesuffix('mm'))-(74+n['y_mm']))<1e-5
        assert abs((float(row['Rotation'])-n['rotation_deg']+180)%360-180)<1e-5
    gerber_data=z.read('order/sugarCANe_RevH_Gerbers_REVIEW_ONLY.zip')
    with zipfile.ZipFile(io.BytesIO(gerber_data)) as g:
        same=[]
        for name in g.namelist():
            if name=='REVIEW_ONLY.txt':continue
            expected=(R/'output/assembly/factory_top_paste.gtp' if name.endswith('.gtp')
                      else R/'output/fabrication'/name)
            assert g.read(name)==expected.read_bytes(),name
            if not name.endswith('.gtp'):same.append(name)
        assert len(same)==13
        with tempfile.TemporaryDirectory(prefix='sugarcane-order-') as folder:
            d=Path(folder)
            for name in ['FRC_Sensor_CAN-F_Paste.gtp','FRC_Sensor_CAN-F_Cu.gtl']:
                (d/name).write_bytes(g.read(name))
            paste=GerberFile.open(d/'FRC_Sensor_CAN-F_Paste.gtp')
            copper=GerberFile.open(d/'FRC_Sensor_CAN-F_Cu.gtl')
            assert len(paste.objects)==325
            assert not [o for o in paste.objects if o.attrs.get('.C')==('U5',)]
            u5=[o for o in copper.objects if isinstance(o,Flash) and o.attrs.get('.P',('',))[0]=='U5']
            assert {o.attrs['.P'][1] for o in u5}=={str(i) for i in range(1,33)}
            assert sum(o.attrs.get('.C')==('U9',) for o in paste.objects)==12
    for count,qty in [(5,7),(10,12)]:
        purchase=readcsv(f'bom/DigiKey_{count}_boards.csv')
        assert len(purchase)==5
        assert int(next(r for r in purchase if r['Part']=='497-14647-ND')['Quantity'])==qty
        assert all(r['Part']!='C492399' for r in purchase)
report=dict(result='PASS assembly-package integrity; manufacturing release remains HOLD',
    factory_placements=129,factory_mpn_types=54,manual_parts=11,finished_parts=140,
    u5_bom_cpl_and_paste_omitted=True,u5_copper_pads_preserved=32,u9_paste_apertures_preserved=12,
    other_fabrication_files_byte_identical=13,all_package_hashes_verified=True,
    shopping_imports_verified=True,packet_sha256=sha(packet.read_bytes()),
    clock_capacitors=dict(references=['C25','C26'],value='20pF',jlc_part='C105173'),
    upstream_buck='LMR51430XDDCR with SRP7028A-8R2M',
    board_sha256=sha((R/'hardware/FRC_Sensor_CAN.kicad_pcb').read_bytes()),
    limitations='File integrity and assembly scope only; no new simulation, physical qualification or supplier allocation.')
(R/'reports/manufacturing/order_package.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
