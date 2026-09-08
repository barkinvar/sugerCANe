"""Revision A circuit definition; generated schematic is checked against this model.

Pin numbers follow manufacturer datasheets. The generator never infers electrical
connections from geometric proximity; netlist parity is checked after KiCad export.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PARTS = {}
CATALOG = {}
SYMBOLS = {}


def component(ref, kind, value, pins, sheet, footprint, mpn='', note='', **kw):
    assert ref not in PARTS
    PARTS[ref] = dict(ref=ref, kind=kind, value=value,
        pins={str(k):v for k,v in pins.items()}, sheet=sheet,
        footprint=footprint, mpn=mpn, note=note, **kw)
    return PARTS[ref]


def resistor(ref, value, a, b, sheet, size='0805', tolerance='1%', mpn='', note=''):
    return component(ref,'R',value,{1:a,2:b},sheet,
        f'Resistor_SMD:R_{size}_{dict(zip(["0805","1206","2010"],["2012","3216","5025"]))[size]}Metric',
        mpn=mpn, tolerance=tolerance,note=note)


def cap(ref, value, a, b, sheet, size='0805', voltage='50V', dielectric='X7R', mpn='', note=''):
    return component(ref,'C',value,{1:a,2:b},sheet,
        f'Capacitor_SMD:C_{size}_{dict(zip(["0805","1206","1210"],["2012","3216","3225"]))[size]}Metric',
        mpn=mpn, voltage=voltage,dielectric=dielectric,note=note)


def diode(ref, value, anode, cathode, sheet, size='SOD-123', mpn='', note=''):
    return component(ref,'D',value,{1:cathode,2:anode},sheet,
        f'Diode_SMD:D_{size}',mpn=mpn,note=note)


def header(ref, names, sheet, n=1, note=''):
    # For two columns pin numbering is 1,2 across the first row, then 3,4.
    rows=len(names)//n
    kind=f'CONN{len(names)}'
    return component(ref,kind,'SELECT' if ref.startswith('JP') else 'DEBUG',
        dict(enumerate(names,1)),sheet,
        f'Connector_PinHeader_2.54mm:PinHeader_{n}x{rows:02d}_P2.54mm_Vertical',note=note)


def terminal(ref, names, sheet):
    n=len(names)
    return component(ref,f'CONN{n}',f'{n}P 5.00mm',dict(enumerate(names,1)),sheet,
        f'FRC_Sensor_CAN:Wuerth_69113771000{n}',mpn=f'69113771000{n}')

# Entry, buck and 3.3 V logic supply.
s='power'
terminal('J1',['VIN_RAW','GND'],s)
component('F1','R','1.5A FAST',{1:'VIN_RAW',2:'VIN_FUSED'},s,
          'Fuse:Fuse_Littelfuse-NANO2-451_453',mpn='045101.5MRL',note='Secondary protection; feed only from fused robot distribution.')
diode('D1','B360A','VIN_FUSED','VIN_PROT',s,'SMA',mpn='B360A-13-F')
diode('D2','SMBJ18A','GND','VIN_PROT',s,'SMB',mpn='SMBJ18A-E3/52',note='Transient suppression, not sustained overvoltage regulation.')
component('C1','CP','47uF',{1:'VIN_PROT',2:'GND'},s,
          'Capacitor_SMD:CP_Elec_6.3x5.8',voltage='35V',mpn='EEE-FK1V470P')
cap('C2','10uF','VIN_PROT','GND',s,'1210','50V')
cap('C3','100nF','VIN_PROT','GND',s)
component('U1','BUCK','LMR51420XDDCR',{1:'GND',2:'BUCK_SW',3:'VIN_PROT',4:'BUCK_FB',5:'VIN_PROT',6:'BUCK_CB'},s,
          'Package_TO_SOT_SMD:TSOT-23-6',mpn='LMR51420XDDCR')
component('L1','L','10uH',{1:'BUCK_SW',2:'V5_INTERNAL'},s,
          'Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm',mpn='SRP7028A-100M',note='3.5A RMS, 6A saturation; use specified family, not NRND SRP7030.')
cap('C4','22uF','V5_INTERNAL','GND',s,'1206','25V')
cap('C5','22uF','V5_INTERNAL','GND',s,'1206','25V')
cap('C6','100nF','BUCK_CB','BUCK_SW',s)
resistor('R1','100k','V5_INTERNAL','BUCK_FB',s,tolerance='0.1%')
resistor('R2','13.7k','BUCK_FB','GND',s,tolerance='0.1%')
component('U2','LDO','AP2112K-3.3',{1:'V5_INTERNAL',2:'GND',3:'V5_INTERNAL',4:None,5:'+3V3'},s,
          'Package_TO_SOT_SMD:SOT-23-5',mpn='AP2112K-3.3TRG1')
cap('C7','1uF','V5_INTERNAL','GND',s,voltage='25V')
cap('C8','4.7uF','+3V3','GND',s,voltage='25V')
resistor('R4','10k','+3V3','GND',s,note='Bleeds microamp-level input feedback when board supply is off.')

# Two protected sensor power rails.
s='sensor_power'
component('U3','HSD','TPS1H100A-Q1',{
    1:None,2:'GND',3:'VBAT_EN_PIN',4:None,5:'SENSOR_VBAT',6:'SENSOR_VBAT',7:'SENSOR_VBAT',
    8:'VIN_PROT',9:'VIN_PROT',10:'VIN_PROT',11:None,12:'VBAT_DIAG_EN',13:'VBAT_ILIM',14:'VBAT_FAULT_N',15:'GND'},s,
    'FRC_Sensor_CAN:TI_PWP0014K_HTSSOP14_EP',mpn='TPS1H100AQPWPRQ1')
resistor('R5','4.87k','VBAT_ILIM','GND',s)
resistor('R6','10k','+3V3','VBAT_FAULT_N',s)
resistor('R7','100k','VBAT_EN_PIN','GND',s)
resistor('R8','4.7k','VBAT_ENABLE','VBAT_EN_PIN',s)
resistor('R9','10k','+3V3','VBAT_DIAG_EN',s)
cap('C9','100nF','VIN_PROT','GND',s)
cap('C10','1uF','SENSOR_VBAT','GND',s)
component('U4','LOADSW','TPS2553DBVR-1',{1:'V5_INTERNAL',2:'GND',3:'V5_EN_PIN',4:'V5_FAULT_N',5:'V5_ILIM',6:'SENSOR_5V'},s,
          'Package_TO_SOT_SMD:SOT-23-6',mpn='TPS2553DBVR-1')
resistor('R10','59k','V5_ILIM','GND',s)
resistor('R11','10k','+3V3','V5_FAULT_N',s)
resistor('R12','100k','V5_EN_PIN','GND',s)
resistor('R13','1k','V5_ENABLE','V5_EN_PIN',s)
cap('C11','100nF','V5_INTERNAL','GND',s)
cap('C12','10uF','SENSOR_5V','GND',s,'1206','25V')
resistor('R14','100k','SENSOR_VBAT','GND',s,note='Provides defined discharge for unloaded output.')
resistor('R15','10k','SENSOR_5V','GND',s)

# Controller, clock, debug, indicator LEDs, rail monitoring.
s='controller'
component('U5','MCU','STM32F042K6T6',{
 1:'+3V3',2:'HSE_IN',3:'HSE_OUT',4:'NRST',5:'+3V3',6:'INPUT1',7:'INPUT2',8:'INPUT3',9:'INPUT4',
 10:'ADC_VBAT',11:'ADC_5V',12:'LED1',13:'LED2',14:'VBAT_ENABLE',15:'V5_ENABLE',16:'GND',17:'+3V3',
 18:'CAN_STB',19:'UART_TX',20:'UART_RX',21:'CAN_RX',22:'CAN_TX',23:'SWDIO',24:'SWCLK',
 25:'STATUS_RED',26:'STATUS_GREEN',27:'VBAT_FAULT_N',28:'V5_FAULT_N',29:'LED3',30:'LED4',31:'BOOT0',32:'GND'},s,
 'Package_QFP:LQFP-32_7x7mm_P0.8mm',mpn='STM32F042K6T6')
for ref in ['C20','C21','C22']:
    cap(ref,'100nF','+3V3','GND',s)
cap('C23','1uF','+3V3','GND',s,voltage='25V',note='VDDA local capacitor.')
cap('C24','4.7uF','+3V3','GND',s,voltage='25V')
component('Y1','XTAL4','8MHz 18pF',{1:'HSE_IN',2:'GND',3:'HSE_XTAL_OUT',4:'GND'},s,
          'Crystal:Crystal_SMD_5032-4Pin_5.0x3.2mm',mpn='ABM3B-8.000MHZ-B2-T')
resistor('R20','0','HSE_OUT','HSE_XTAL_OUT',s,note='Drive-level/startup measurement position. Tune only after oscillator characterization.')
cap('C25','30pF','HSE_IN','GND',s,dielectric='C0G')
cap('C26','30pF','HSE_XTAL_OUT','GND',s,dielectric='C0G')
resistor('R21','10k','+3V3','NRST',s)
cap('C27','100nF','NRST','GND',s)
resistor('R22','10k','BOOT0','GND',s)
header('J8',['+3V3','SWDIO','GND','SWCLK','GND','UART_TX','BOOT0','UART_RX','GND','NRST'],s,2,
       note='Custom 2.54mm service header, NOT standard Cortex pinout. Pin1 voltage reference only; do not feed external power.')
header('JP1',['NRST','GND'],s,note='Momentary reset by shorting pins; no shunt during normal operation.')
resistor('R23','100k','VIN_PROT','ADC_VBAT',s)
resistor('R24','10k','ADC_VBAT','GND',s)
cap('C28','10nF','ADC_VBAT','GND',s)
resistor('R25','10k','SENSOR_5V','ADC_5V',s)
resistor('R26','10k','ADC_5V','GND',s)
cap('C29','10nF','ADC_5V','GND',s)
for i,(net,color) in enumerate([('STATUS_GREEN','GREEN'),('STATUS_RED','RED'),('LED1','GREEN'),('LED2','GREEN'),('LED3','GREEN'),('LED4','GREEN')]):
    resistor(f'R{30+i}','1k',net,f'{net}_A',s)
    component(f'D{10+i}','LED',color,{1:'GND',2:f'{net}_A'},s,'LED_SMD:LED_0805_2012Metric')

# CAN interface; powered-off/recessive default.
s='can'
component('U6','CAN','TCAN3413DR',{1:'CAN_TX',2:'GND',3:'+3V3',4:'CAN_RX',5:'+3V3',6:'CANL',7:'CANH',8:'CAN_STB'},s,
          'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',mpn='TCAN3413DR')
resistor('R40','10k','+3V3','CAN_STB',s)
resistor('R41','10k','+3V3','CAN_TX',s)
cap('C40','100nF','+3V3','GND',s)
cap('C41','100nF','+3V3','GND',s)
cap('C42','1uF','+3V3','GND',s,voltage='25V')
component('D20','CAN_TVS','ESD2CAN24-Q1',{1:'CANH',2:'CANL',3:'GND'},s,
          'Package_TO_SOT_SMD:SOT-23',mpn='ESD2CAN24DBZRQ1')
terminal('J2',['CANH','CANL'],s)
terminal('J3',['CANH','CANL'],s)
resistor('R42','120','CANH','CAN_TERM',s,size='1206',note='Use termination only if board is the physical end of the CAN trunk.')
header('JP2',['CAN_TERM','CANL'],s,note='Optional 120-ohm termination: shipped OPEN.')

# Four identical independently selected channels. Comparator units split between sheets.
comp_pins={3:'VIN_PROT',12:'GND'}
for ch,(out,pplus,pminus) in enumerate([(2,5,4),(1,7,6),(14,9,8),(13,11,10)],1):
    s=f'input{ch}'
    prefix=ch*100
    sig=f'SIG{ch}'; vp=f'VPORT{ch}'; sense=f'SENSE{ch}'; ref=f'REF{ch}'; outnet=f'INPUT{ch}'
    comp_pins.update({out:outnet,pplus:sense,pminus:ref})
    terminal(f'J{ch+3}',[vp,'GND',sig],s)
    header(f'JP{prefix+1}',['SENSOR_5V',vp,'SENSOR_VBAT'],s,
           note='Fit ONE shunt: 1-2=5V, 2-3=VBAT. Never bridge all pins.')
    header(f'JP{prefix+2}',[f'LOW_SEL{ch}','GND'],s,
           note='Open=industrial thresholds; fitted=3.3/5V logic thresholds.')
    header(f'JP{prefix+3}',[f'PULL_PORT{ch}',sig,f'PULL_3V3_{ch}',sig,f'BIAS_GND{ch}',sig],s,2,
           note='ONE horizontal shunt only:1-2=port pullup,3-4=3V3 pullup,5-6=pulldown. Open=driven input.')
    resistor(f'R{prefix+1}','110k',sig,f'SIG_MID{ch}',s)
    resistor(f'R{prefix+2}','110k',f'SIG_MID{ch}',sense,s)
    resistor(f'R{prefix+3}','20k',sense,'GND',s)
    resistor(f'R{prefix+4}','910k',outnet,sense,s)
    resistor(f'R{prefix+5}','10k','+3V3',outnet,s)
    resistor(f'R{prefix+6}','100k','+3V3',ref,s)
    resistor(f'R{prefix+7}','17.8k',ref,'GND',s)
    resistor(f'R{prefix+8}','7.15k',ref,f'LOW_SEL{ch}',s)
    resistor(f'R{prefix+9}','4.7k',f'BIAS_GND{ch}','GND',s,size='2010',note='Pulldown: >=0.75W; about0.193W at30V. Each bias branch has its own limiting resistor.')
    resistor(f'R{prefix+10}','4.7k',f'BIAS_PORT{ch}',f'PULL_PORT{ch}',s,note='Port pullup. Limits current even with multiple bias shunts fitted.')
    resistor(f'R{prefix+11}','4.7k',f'BIAS_3V3_{ch}',f'PULL_3V3_{ch}',s,note='Logic pullup. Prevents a bias jumper error from shorting the 3.3V rail.')
    cap(f'C{prefix+1}','1nF',sense,'GND',s,dielectric='C0G')
    diode(f'D{prefix+1}','SMAJ30A','GND',sig,s,'SMA',mpn='SMAJ30A',note='30V working standoff; unidirectional transient clamp.')
    diode(f'D{prefix+2}','BAT46W',vp,f'BIAS_PORT{ch}',s,mpn='BAT46W-E3-18')
    diode(f'D{prefix+3}','BAT46W','+3V3',f'BIAS_3V3_{ch}',s,mpn='BAT46W-E3-18')
component('U7','COMP4','LM2901BIDR',comp_pins,'input1','Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',mpn='LM2901BIDR')
cap('C50','100nF','VIN_PROT','GND','input1')

# Explicit test pads: no separate purchased part.
for i,net in enumerate(['GND','VIN_PROT','V5_INTERNAL','+3V3','SENSOR_5V','SENSOR_VBAT','INPUT1','INPUT2','INPUT3','INPUT4'],1):
    component(f'TP{i}','TP',net,{1:net},'power' if i<=6 else f'input{i-6}',
              'TestPoint:TestPoint_Pad_D2.0mm',note='Bare PCB test pad; excluded from purchased BOM.',exclude_bom=True)


# Final purchasing choices. Passives retain common footprints and independent
# alternate sourcing; electrical values are never inferred from the order code.
R_MPN={'0':'RC0805JR-070RL','1k':'RC0805FR-071KL','4.7k':'RC0805FR-074K7L',
 '4.87k':'ERJ-6ENF4871V','7.15k':'RC0805FR-077K15L','10k':'RC0805FR-0710KL',
 '17.8k':'ERJ-6ENF1782V','20k':'RC0805FR-0720KL','59k':'RC0805FR-0759KL',
 '100k':'RC0805FR-07100KL','110k':'RC0805FR-07110KL','910k':'RC0805FR-07910KL'}
for ref,c in PARTS.items():
 if c.get('mpn') or c.get('exclude_bom'):continue
 if c['kind']=='R':
  c['mpn']=('RT0805BRD07100KL' if c['value']=='100k' else 'RT0805BRD0713K7L') if c['tolerance']=='0.1%' else ('RC2010FK-074K7L' if '2010' in c['footprint'] else ('RC1206FR-07120RL' if c['value']=='120' else R_MPN[c['value']]))
 elif c['kind']=='C':
  if ref in ['C4','C5','C12']:
   c.update(value='22uF',dielectric='X5R',voltage='25V',mpn='CL31A226KAHNNNE')
  elif ref=='C2':c['mpn']='CL32B106KBJNNWE'
  elif c['value']=='100nF':c['mpn']='CC0805KRX7R9BB104'
  elif c['value']=='10nF':c['mpn']='CC0805KRX7R9BB103'
  elif c['value']=='1uF':c.update(voltage='50V',mpn='C0805C105K5RACTU')
  elif c['value']=='4.7uF':c['mpn']='TMK212AB7475KG-T'
  elif c['value']=='1nF':c['mpn']='CC0805JRNPO9BN102'
  elif c['value']=='30pF':c['mpn']='C0805C300J5GACTU'
  else:raise ValueError(ref)
 elif c['kind']=='LED':c['mpn']='LTST-C170KRKT' if c['value']=='RED' else 'LTST-C170KGKT'
 elif c['kind'].startswith('CONN'):
  c['mpn']={'CONN2':'M20-9990245','CONN3':'M20-9990345','CONN6':'M20-9980345','CONN10':'M20-9980545'}[c['kind']]
 else:raise ValueError('Unselected part '+ref)

# Ship every footprint and 3D model locally to make the project portable.
for part in PARTS.values():
    part['source_footprint'] = part['footprint']
    part['footprint'] = 'FRC_Sensor_CAN:' + part['footprint'].split(':',1)[1]

def export():
    p=ROOT/'hardware/design/circuit.json'
    p.write_text(json.dumps({'revision':'A','parts':PARTS},indent=2)+'\n')
    print(f'{len(PARTS)} components, {len({n for c in PARTS.values() for n in c["pins"].values() if n})} nets')

if __name__=='__main__': export()
