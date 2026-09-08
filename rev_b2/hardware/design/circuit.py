"""Compact three-channel revision B; explicit changes to the frozen A circuit."""
from pathlib import Path
from copy import deepcopy
import json
from circuit_rev_a import PARTS as A
ROOT=Path(__file__).resolve().parents[2]
PARTS=deepcopy(A)
for ref in list(PARTS):
    if PARTS[ref]['sheet']=='input4' or ref in ['D15','R35','JP1']:
        del PARTS[ref]
PARTS['U5']['pins']['9']=None
PARTS['U5']['pins']['30']=None
PARTS['U7']['pins'].update({'13':None,'11':'GND','10':'+3V3','3':'+3V3'})
PARTS['U7'].update(value='LM339LV',mpn='LM339LVDR',note='Rail-to-rail failsafe comparator on regulated 3V3. 0-30V signal is divided before this pin; NOT a 30V supply IC. Same SO14 pin assignment as LM2901B.')
PARTS['C50']['pins']['1']='+3V3'
PARTS['D2'].update(value='SMBJ22A',mpn='SMBJ22A-E3/52',note='22 V continuous standoff; 35.5 V specified pulse clamp. Bench-check overshoot. Not sustained overvoltage regulation.')
PARTS['C1'].update(voltage='50V',mpn='EEE-FK1H470P',footprint='FRC_Sensor_CAN:CP_Elec_8x6.5',source_footprint='Capacitor_SMD:CP_Elec_8x6.5')
PARTS['R3']['note']='Gate pull-down; maximum 1 mA nominal zener current at 22 V input.'
PARTS['R14']['note']='Switched battery output bleed; 2.2 mA at 22 V.'
PARTS['R1'].update(value='100k',mpn='RC0805FR-07100KL',tolerance='1%')
PARTS['R2'].update(value='17.8k',mpn='ERJ-6ENF1782V',tolerance='1%')
for ref in ['L1','C4','C5','C13','R1']:
    PARTS[ref]['pins']={k:('V4P2' if n=='V5_INTERNAL' else n) for k,n in PARTS[ref]['pins'].items()}
for ref in ['J1','J2','J3','J4','J5','J6']:
    c=PARTS[ref];n=len(c['pins'])
    c.update(value=f'{n}P PUSH 3.5mm',mpn='1824420000' if n==2 else '1824430000',
        footprint=f'FRC_Sensor_CAN:Weidmuller_LSF_90_{n}P',source_footprint=f'FRC_Sensor_CAN:Weidmuller_LSF_90_{n}P',
        note='Horizontal /90 push-in; 8 mm strip, 7 mm pin-row spacing, two solder pins per pole.')
for ref,c in PARTS.items():
    if ref.startswith('JP'):
        n=len(c['pins']);cols=2 if n==6 else 1;rows=n//cols
        name=f'PinHeader_{cols}x{rows:02d}_P2.00mm_Vertical'
        c.update(mpn={2:'M22-2010205',3:'M22-2010305',6:'M22-2020305'}[n],
            footprint='FRC_Sensor_CAN:'+name,source_footprint='Connector_PinHeader_2.00mm:'+name)
PARTS['J8'].update(value='POGO SERVICE',mpn='',exclude_bom=True,
    footprint='FRC_Sensor_CAN:Tag-Connect_TC2050-IDC-NL_2x05_P1.27mm_Vertical',source_footprint='Connector:Tag-Connect_TC2050-IDC-NL_2x05_P1.27mm_Vertical',
    note='Standard TC2050-IDC-NL mechanical footprint; CUSTOM electrical pinout. Cable pin6 VTref output only. Follow adapter wiring table.')
PARTS['J8']['pins']={'1':'NRST','2':'UART_RX','3':'UART_TX','4':'SWCLK','5':'SWDIO','6':'+3V3','7':'GND','8':'GND','9':'BOOT0','10':'GND'}
def add(ref,kind,value,pins,fp,mpn,note='',**kw):
    PARTS[ref]=dict(ref=ref,kind=kind,value=value,pins={str(k):v for k,v in pins.items()},sheet='boost',
        footprint='FRC_Sensor_CAN:'+fp.split(':')[1],source_footprint=fp,mpn=mpn,note=note,**kw)
add('U8','BOOST','TPS613222A',{1:'BOOST_SW',2:'GND',3:None,4:'V5_INTERNAL',5:None},
    'Package_TO_SOT_SMD:SOT-23-5','TPS613222ADBVR','Fixed 5 V boost; powered through L2 from 4.0 V buck. DBV pins checked against TI table.')
add('L2','L','4.7uH',{1:'V4P2',2:'BOOST_SW'},'FRC_Sensor_CAN:Bourns_SRP4020TA','SRP4020TA-4R7M',
    '2.6 A RMS / 3.5 A saturation, 105 milliohm max; supports converter current-limit excursions.')
add('D4','D','SS14',{1:'V5_INTERNAL',2:'BOOST_SW'},'Diode_SMD:D_SMA','SS14-E3/61T',
    'External Schottky rectifier shares boost current as recommended by TI for 500 mA designs.')
for ref in ['C15','C16']:
    add(ref,'C','22uF',{1:'V5_INTERNAL',2:'GND'},'Capacitor_SMD:C_1206_3216Metric','CL31A226KAHNNNE',
        'Boost output reservoir; check effective capacitance and converter loop on bench.',voltage='25V',dielectric='X5R',tolerance='10%')
add('C17','C','100nF',{1:'V5_INTERNAL',2:'GND'},'Capacitor_SMD:C_0805_2012Metric','CC0805KRX7R9BB104',voltage='50V',dielectric='X7R',tolerance='10%')
# Factory variant: values, pin maps and land patterns remain unchanged.
SUBSTITUTIONS = json.loads((ROOT/'bom/substitutions.json').read_text())
for ref, component in PARTS.items():
    original = component.get('mpn')
    if original in SUBSTITUTIONS:
        mpn, manufacturer, lcsc = SUBSTITUTIONS[original]
        component.update(mpn=mpn, manufacturer=manufacturer, lcsc=lcsc,
                         original_rev_b_mpn=original)
        component['note'] += ' Rev B-2: same-value factory sourcing equivalent.'
        if component['kind'] == 'C':
            component['voltage'] = '100V'
def export():
    p=ROOT/'hardware/design/circuit.json'
    p.write_text(json.dumps({'revision':'B-2','parts':PARTS},indent=2)+'\n')
    print(len(PARTS),'parts;',len({n for c in PARTS.values() for n in c['pins'].values() if n}),'named nets')
if __name__=='__main__': export()
