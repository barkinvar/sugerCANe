#!/usr/bin/env python3
"""Generate native editable KiCad schematic and local symbols from reviewed circuit.
The first layout pass is deliberately spacious; final exported pages are visually reviewed.
"""
from pathlib import Path
import sys, json, uuid, math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware/design'))
from circuit import PARTS, ROOT, export

OUT=ROOT/'hardware'
NAMESPACE=uuid.UUID('1358f0c9-f8c1-4e34-9e77-f77f53fd04d3')
def uid(s): return str(uuid.uuid5(NAMESPACE,s))
def q(s): return json.dumps(str(s),ensure_ascii=False)
def num(v): return f'{v:.5f}'.rstrip('0').rstrip('.') if isinstance(v,float) else str(v)
def fx(size=1.27,justify='',hide=False):
    return f'(effects (font (size {size} {size}))'+(f' (justify {justify})' if justify else '')+(' (hide yes)' if hide else '')+')'
def prop(k,v,x=0,y=0,hide=False,size=1.27,justify='',angle=0):
    return f'(property {q(k)} {q(v)} (at {num(x)} {num(y)} {angle}) {fx(size,justify,hide)})'
def line(points,w=.254):
    return '(polyline (pts '+' '.join(f'(xy {num(x)} {num(y)})' for x,y in points)+f') (stroke (width {w}) (type default)) (fill (type none)))'
def rect(x1,y1,x2,y2):
    return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width .254) (type default)) (fill (type background)))'

SYMS={}
def define(name, units, graphics=None, prefix='U', width=15.24):
    # units: list of pin records (number,name,type,x,y,angle,length)
    body=[f'(symbol {q(name)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
          prop('Reference',prefix,0,10), prop('Value',name,0,7),prop('Footprint','',hide=True),prop('Datasheet','',hide=True)]
    for unit,pins in units.items():
        g=(graphics or {}).get(unit,[])
        body.append(f'(symbol {q(name+"_"+str(unit)+"_1")} '+''.join(g))
        for number,pn,typ,x,y,a,length in pins:
            body.append(f'(pin {typ} line (at {num(x)} {num(y)} {a}) (length {num(length)}) (name {q(pn)} {fx(1.016)}) (number {q(number)} {fx(1.016)}))')
        body.append(')')
    body.append(')')
    SYMS[name]={'text':'\n'.join(body),'units':units,'graphics':graphics or {}}

# Passives are horizontal. Pin1 of polar parts is marked explicitly.
for name in ['R','C','CP','D','LED','L']:
    pins=[('1','', 'passive',-5.08,0,0,2.54),('2','','passive',5.08,0,180,2.54)]
    if name in ['D','LED']: pins=[('2','A','passive',-5.08,0,0,2.54),('1','K','passive',5.08,0,180,2.54)]
    if name=='R': g=[rect(-2.54,1.016,2.54,-1.016)]
    elif name in ['C','CP']:
        pins=[('1','+ ' if name=='CP' else '','passive',-5.08,0,0,4.318),('2','','passive',5.08,0,180,4.318)]
        g=[line([(-.762,-2.54),(-.762,2.54)]),line([(.762,-2.54),(.762,2.54)])]
    elif name in ['D','LED']:
        g=[line([(-2.54,-2.032),(-2.54,2.032),(2.54,0),(-2.54,-2.032)]),line([(2.54,-2.032),(2.54,2.032)])]
        if name=='LED': g +=[line([(0,2.54),(2.54,5.08)]),line([(2.54,5.08),(1.27,5.08)]),line([(2.54,5.08),(2.54,3.81)])]
    else:
        g=[line([(-2.54,0),(-1.9,1.27),(-1.27,0),(-.63,1.27),(0,0),(.63,1.27),(1.27,0),(1.9,1.27),(2.54,0)])]
    define(name,{1:pins},{1:g},prefix=name[0])

define('NETTIE',{1:[('1','','passive',-5.08,0,0,2.54),('2','','passive',5.08,0,180,2.54)]},
       {1:[line([(-2.54,0),(2.54,0)],.762)]},prefix='NT')
define('KELVIN_R',{1:[('1','','passive',-10.16,0,0,5.08),('2','','passive',10.16,0,180,5.08),
 ('3','','passive',-5.08,7.62,270,5.08),('4','','passive',5.08,7.62,270,5.08)]},
 {1:[rect(-2.54,1.016,2.54,-1.016),line([(-5.08,2.54),(-5.08,0),(-2.54,0)]),line([(5.08,2.54),(5.08,0),(2.54,0)])]},prefix='R')

# Rectangular ICs with functional grouping; each physical pin remains separate.
define('ZENER',{1:[('2','A','passive',-5.08,0,0,2.54),('1','K','passive',5.08,0,180,2.54)]},
       {1:[line([(-2.54,-2.032),(-2.54,2.032),(2.54,0),(-2.54,-2.032)]),
           line([(1.27,-2.794),(2.54,-2.032),(2.54,2.032),(3.81,2.794)])]},prefix='D')
def ic(name,left,right,top=(),bottom=(),width=20.32):
    height=2.54*(max(len(left),len(right))+1)
    pins=[]
    for arr,side in [(left,'L'),(right,'R')]:
        for i,(number,pn,typ) in enumerate(arr):
            y=height/2-2.54*(i+1)
            pins.append((str(number),pn,typ,-width/2-5.08 if side=='L' else width/2+5.08,y,0 if side=='L' else 180,5.08))
    for arr,side in [(top,'T'),(bottom,'B')]:
        for i,(number,pn,typ) in enumerate(arr):
            x=(i-(len(arr)-1)/2)*2.54
            pins.append((str(number),pn,typ,x,height/2+5.08 if side=='T' else -height/2-5.08,270 if side=='T' else 90,5.08))
    define(name,{1:pins},{1:[rect(-width/2,height/2,width/2,-height/2)]})

ic('BOOST12',[(6,'IN','power_in'),(3,'EN','input'),(7,'FREQ','input')],[(5,'SW','power_out'),(2,'FB','input'),(1,'COMP','passive'),(8,'SS','passive')],bottom=[(4,'PGND','power_in')])
ic('BUCK',[(3,'VIN','power_in'),(5,'EN','input')],[(6,'CB','passive'),(2,'SW','power_out'),(4,'FB','input')],bottom=[(1,'GND','power_in')])
ic('PMOS8',[(5,'D','passive'),(6,'D','passive'),(7,'D','passive'),(8,'D','passive')],
   [(1,'S','passive'),(2,'S','passive'),(3,'S','passive')],bottom=[(4,'G','input')])
ic('LDO',[(1,'VIN','power_in'),(3,'EN','input')],[(5,'VOUT','power_out'),(4,'NC','no_connect')],bottom=[(2,'GND','power_in')])
ic('LOADSW',[(1,'IN','power_in'),(3,'EN','input'),(5,'ILIM','passive')],[(6,'OUT','power_out'),(4,'FAULT_N','open_collector')],bottom=[(2,'GND','power_in')])
ic('HSD',[(8,'VS','power_in'),(1,'IN','input'),(2,'DIAG_EN','input'),(4,'CL','passive')],
   [(7,'OUT','power_out'),(3,'FAULT_N','open_collector'),(5,'DELAY','passive')],
   bottom=[(6,'GND','power_in'),(9,'EP/GND','passive')],width=25.4)
ic('CAN',[(1,'TXD','input'),(4,'RXD','output'),(8,'STB','input')],[(7,'CANH','bidirectional'),(6,'CANL','bidirectional')],
   top=[(3,'VCC','power_in'),(5,'VIO','power_in')],bottom=[(2,'GND','power_in')])
ic('CAN_TVS',[(1,'IO1','passive'),(2,'IO2','passive')],[],bottom=[(3,'GND','passive')],width=10.16)
# MCU package mapping: ST DS10111 / DocID025832 LQFP32.
ic('MCU',[(2,'PF0/OSC_IN','input'),(3,'PF1/OSC_OUT','output'),(4,'NRST','bidirectional'),
 (6,'PA0/IN1','input'),(7,'PA1/IN2','input'),(8,'PA2/IN3','input'),(9,'PA3/12V_PG','bidirectional'),
 (10,'PA4/5V_FAULT','bidirectional'),(11,'PA5/UP1_N','output'),(27,'PB4/DOWN3','output'),(28,'PB5/NC','input'),
 (31,'PB8/BOOT0','input'),(23,'PA13/SWDIO','bidirectional'),(24,'PA14/SWCLK','input')],
 [(21,'PA11/CAN_RX','input'),(22,'PA12/CAN_TX','output'),(18,'PA8/CAN_STB','output'),
 (19,'PA9/UART_TX','output'),(20,'PA10/UART_RX','input'),(14,'PB0/DOWN1','output'),(15,'PB1/DOWN2','output'),
 (12,'PA6/UP2_N','output'),(13,'PA7/UP3_N','output'),(29,'PB6/NC','output'),(30,'PB7/NC','output'),
 (25,'PA15/NC','output'),(26,'PB3/STATUS','output')],
 top=[(1,'VDD','power_in'),(5,'VDDA','power_in'),(17,'VDDIO2','power_in')],
 bottom=[(16,'VSS','power_in'),(32,'VSS','power_in')],width=45.72)

for name in ['PMOS3','NMOS3']:
    define(name,{1:[('1','G','input',-10.16,0,0,5.08),('2','S','passive',10.16,5.08,180,5.08),('3','D','passive',10.16,-5.08,180,5.08)]},
           {1:[rect(-5.08,7.62,5.08,-7.62)]},prefix='Q')

for n in [2,3,6,10]:
    p=[(str(i),str(i),'passive',-7.62,(n-1)*1.27-(i-1)*2.54,0,5.08) for i in range(1,n+1)]
    define(f'CONN{n}',{1:p},{1:[rect(-2.54,(n+1)*1.27,2.54,-(n+1)*1.27)]},prefix='J')
# Crystal terminal 1/3 active, 2/4 grounded case.
define('XTAL4',{1:[('1','','passive',-7.62,0,0,5.08),('3','','passive',7.62,0,180,5.08),
                   ('2','','passive',-1.27,-7.62,90,5.08),('4','','passive',1.27,-7.62,90,5.08)]},
       {1:[rect(-1.27,2.54,1.27,-2.54),line([(-2.54,-2.54),(-2.54,2.54)]),line([(2.54,-2.54),(2.54,2.54)])]},prefix='Y')
units={}; graphics={}
for u,(o,p,m) in enumerate([(2,5,4),(1,7,6),(14,9,8),(13,11,10)],1):
    units[u]=[(str(p),'+','input',-10.16,2.54,0,5.08),(str(m),'-','input',-10.16,-2.54,0,5.08),(str(o),'OUT','open_collector',10.16,0,180,5.08)]
    graphics[u]=[line([(-5.08,-5.08),(-5.08,5.08),(5.08,0),(-5.08,-5.08)])]
units[5]=[('3','','power_in',0,7.62,270,5.08),('12','','power_in',0,-7.62,90,5.08)]
graphics[5]=[rect(-2.54,2.54,2.54,-2.54)]
define('COMP4',units,graphics)
define('TP',{1:[('1','','passive',0,0,90,0)]},{1:['(circle (center 0 1.27) (radius 1.27) (stroke (width .254) (type default)) (fill (type none)))']},prefix='TP')
define('PWR_FLAG',{1:[('1','pwr','power_out',0,0,90,0)]},{1:[line([(-1.27,0),(0,1.27),(1.27,0),(-1.27,0)])]},prefix='#FLG')


for count in [2,3]:
    pitch=15.24  # Space the schematic nets; unrelated to physical header pitch.
    pins=[(str(i+1),'','passive',(i-(count-1)/2)*pitch,-5.08,90,2.54) for i in range(count)]
    graphics=[rect((i-(count-1)/2)*pitch-1.27,-2.54,(i-(count-1)/2)*pitch+1.27,0) for i in range(count)]
    define(f'SEL{count}',{1:pins},{1:graphics},prefix='JP')

SHEETS=['power','regulated_12v','sensor_power','controller','can','input1','input2','input3']
TITLES={'boost':'Fixed 5 V boost and reservoir','power':'Battery entry and internal supplies','sensor_power':'Protected sensor power rails','controller':'Controller, clock, debug and status',
        'regulated_12v':'Protected 5 V to 12 V boost','can':'CAN physical interface and termination',**{f'input{i}':f'Input {i}: fixed-threshold digital input' for i in range(1,5)}}
rootid=uid('root')

class Sheet:
    def __init__(self,name):
        self.name=name; self.items=[]; self.used=set(); self.count=0; self.placed={}; self.usedlibs=set()
        self.path=f'/{rootid}/{uid("sheet_"+name)}'
    def key(self,kind):
        self.count+=1; return uid(f'{self.name}_{kind}_{self.count}')
    def text(self,t,x,y,size=1.5):
        self.items.append(f'(text {q(t)} (at {x} {y} 0) {fx(size,"left top")} (uuid {q(self.key("text"))}))')
    def wire(self,a,b):
        if a==b:return
        self.items.append(f'(wire (pts (xy {num(a[0])} {num(a[1])}) (xy {num(b[0])} {num(b[1])})) (stroke (width 0) (type default)) (uuid {q(self.key("wire"))}))')
    def junction(self,p):
        self.items.append(f'(junction (at {num(p[0])} {num(p[1])}) (diameter 0) (color 0 0 0 0) (uuid {q(self.key("junction"))}))')
    def label(self,net,p,angle=0):
        self.items.append(f'(global_label {q(net)} (shape passive) (at {num(p[0])} {num(p[1])} {angle}) {fx(1.016,"right" if angle==0 else "left")} (uuid {q(self.key("label"))}) '+prop('Intersheetrefs','${INTERSHEET_REFS}',p[0],p[1],True)+')')
    def place(self,ref,x,y,angle=0,unit=1,labels=True,only=None):
        x=round(x/1.27)*1.27; y=round(y/1.27)*1.27
        c=PARTS[ref]; kind=c['kind']; self.usedlibs.add(kind)
        pins=SYMS[kind]['units'][unit]
        self.used.add((ref,unit)); sid=uid(f'part_{ref}_{unit}')
        angle_rad=math.radians(angle)
        def trans(px,py):return (round(x+px*math.cos(angle_rad)-py*math.sin(angle_rad),5),round(y-px*math.sin(angle_rad)-py*math.cos(angle_rad),5))
        fieldy=min(trans(p[3],p[4])[1] for p in pins)-4
        # Most units have readable short values above; long part number on second row.
        if kind in ('SEL2','SEL3'):
            fields=prop('Reference',ref,x,y-5.08)+prop('Value',c['value'],x,y-2.54,size=1.016)
        elif kind=='KELVIN_R':
            fields=prop('Reference',ref,x,y+6.35)+prop('Value',c['value'],x,y+9.525,size=1.016)
        elif kind=='COMP4' and unit==5:
            fields=prop('Reference',ref,x+16,y-2)+prop('Value',c['value'],x+16,y+2,size=1.016)
        elif angle in [90,270] and kind in ['R','C','CP','D','ZENER','LED','L']:
            fields=prop('Reference',ref,x+8,y-1.5,angle=90)+prop('Value',c['value'],x+8,y+1.5,size=1.016,angle=90)
        else:
            fields=prop('Reference',ref,x,fieldy-2.5)+prop('Value',c['value'],x,fieldy,size=1.016)
        fields+=prop('Footprint',c['footprint'],x,y,True)+prop('Datasheet',c.get('datasheet',''),x,y,True)
        fields+=prop('MPN',c.get('mpn',''),x,y,True)+prop('Notes',c.get('note',''),x,y,True)
        inst=f'(symbol (lib_id {q("FRC_Sensor_CAN:"+kind)}) (at {x} {y} {angle}) (unit {unit}) (in_bom {"no" if c.get("exclude_bom") else "yes"}) (on_board yes) (dnp no) (uuid {q(sid)}) {fields}'
        coords={}
        for number,pn,typ,px,py,a,length in pins:
            inst+=f'(pin {q(number)} (uuid {q(uid(ref+"_pin_"+number))}))'
            p=trans(px,py); coords[number]=p
            net=c['pins'][number]
            if net is None:
                self.items.append(f'(no_connect (at {num(p[0])} {num(p[1])}) (uuid {q(self.key("nc"))}))')
            elif labels and (only is None or number in only):
                direction=(a+angle)%360
                dx={0:-7.62,180:7.62,90:0,270:0}[direction]
                dy={0:0,180:0,90:7.62,270:-7.62}[direction]
                end=(round(p[0]+dx,5),round(p[1]+dy,5))
                self.wire(p,end)
                self.label(net,end,0 if direction in [0,90,270] else 180)
        inst+=f'(instances (project "FRC_Sensor_CAN" (path {q(self.path)} (reference {q(ref)}) (unit {unit})))) )'
        self.items.append(inst); self.placed[(ref,unit)]=coords
        return coords
    def flag(self,net,x,y):
        ref=f'#FLG{len([k for k in PARTS if k.startswith(chr(35))])+1:02d}'
        PARTS[ref]=dict(kind='PWR_FLAG',value='PWR_FLAG',pins={'1':net},footprint='',exclude_bom=True)
        self.place(ref,x,y)
    def save(self):
        text=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(uid("page_"+self.name))}) (paper "A3")\n'
        text+=f'(title_block (title {q("SC12 - "+TITLES[self.name])}) (date "2026-09-08") (rev "F") (company "Original sensor interface design") (comment 1 "Prototype: bench validation required before robot use"))\n'
        text+='(lib_symbols\n'+'\n'.join(SYMS[n]['text'].replace('(symbol '+q(n),'(symbol '+q('FRC_Sensor_CAN:'+n),1) for n in sorted(self.usedlibs))+')\n'
        text+='\n'.join(self.items)+'\n(embedded_fonts no))\n'
        (OUT/(self.name+'.kicad_sch')).write_text(text)

pages={name:Sheet(name) for name in SHEETS}
# Initial organized block layouts on A3 (420x297mm). All grid coordinates are mm.
for name in SHEETS:
    page=pages[name]
    page.text(TITLES[name],15,15,2.54)

# Connected power circuit. All coordinates stay on the 1.27mm schematic grid.
def path(page,*pts):
    for a,z in zip(pts,pts[1:]):page.wire(a,z)
def gp(page,ref,gx,gy,angle=0,labels=False,unit=1):
    return page.place(ref,gx*2.54,gy*2.54,angle,unit,labels)

p=pages['power']
p.text('PROTECTED BATTERY ENTRY',15,28,1.8)
gp(p,'J1',14,24,labels=True)
f=gp(p,'F1',34,22.5);q1=gp(p,'Q1',49,24)
p.label('VIN_RAW',f['1']);dx=39.5*2.54;sx=59*2.54
path(p,f['2'],(dx,q1['5'][1]),q1['5']);p.label('VIN_FUSED',f['2'],180)
path(p,(dx,q1['5'][1]),(dx,q1['8'][1]))
for pin in ['6','7','8']:p.wire((dx,q1[pin][1]),q1[pin]);p.junction((dx,q1[pin][1]))
path(p,q1['1'],(sx,q1['1'][1]),(sx,q1['3'][1]),q1['3'])
p.wire(q1['2'],(sx,q1['2'][1]));p.junction((sx,q1['2'][1]))
z=gp(p,'D3',59,35,90);r=gp(p,'R3',49,40,270)
path(p,(sx,q1['3'][1]),(sx,z['1'][1]),z['1']);p.junction((sx,q1['3'][1]))
path(p,q1['4'],(q1['4'][0],z['2'][1]),z['2'])
path(p,(q1['4'][0],z['2'][1]),r['1']);p.junction((q1['4'][0],z['2'][1]))
p.label('REV_GATE',q1['4']);p.label('GND',r['2'])
entry_y=q1['1'][1];nodes=[]
for ref,gx,ang in [('D2',66,90),('C1',86,270),('C2',109,270),('C3',130,270)]:
    pins=gp(p,ref,gx,32,ang);node=(pins['1'][0],entry_y);nodes.append(node)
    p.wire(node,pins['1']);p.junction(node);p.label('GND',pins['2'])
path(p,(sx,entry_y),*nodes);p.junction((sx,entry_y));p.label('VIN_PROT',nodes[-1],180)
for i in range(1,2):gp(p,f'TP{i}',20+(i-1)*25,45,labels=True)
p.text('500 kHz BUCK / REGULATED 5 V',15,130,1.8)
u=gp(p,'U1',40,66);l=gp(p,'L1',74,66);cb=gp(p,'C6',60,55)
vinx=18*2.54
path(p,u['3'],(vinx,u['3'][1]),(vinx,u['5'][1]),u['5']);p.label('VIN_PROT',(vinx,u['3'][1]))
p.label('GND',u['1'])
sw=(68*2.54,u['2'][1]);path(p,u['2'],sw,l['1']);p.label('BUCK_SW',sw)
path(p,u['6'],(50*2.54,u['6'][1]),(50*2.54,cb['1'][1]),cb['1']);p.label('BUCK_CB',cb['1'])
path(p,cb['2'],(sw[0],cb['2'][1]),sw);p.junction(sw)
c4=gp(p,'C4',86,77,270);c5=gp(p,'C5',103,77,270);c13=gp(p,'C13',119,77,270)
r1=gp(p,'R1',135,77,270);r2=gp(p,'R2',135,94,270)
rail=[l['2']]+[(pin['1'][0],l['2'][1]) for pin in [c4,c5,c13,r1]]
path(p,*rail);p.label('V5_INTERNAL',rail[-1],180)
for pin in [c4,c5,c13,r1]:
    node=(pin['1'][0],l['2'][1]);p.wire(node,pin['1']);p.junction(node)
for pin in [c4,c5,c13]:p.label('GND',pin['2'])
mid=(r1['2'][0],86*2.54)
path(p,r1['2'],mid,r2['1']);p.junction(mid);p.label('GND',r2['2'])
path(p,u['4'],(54*2.54,u['4'][1]),(54*2.54,mid[1]),mid);p.label('BUCK_FB',(54*2.54,mid[1]))
p.text('3.3 V LOGIC SUPPLY',15,245,1.8)
u=gp(p,'U2',42,106);c7=gp(p,'C7',20,104,270);c8=gp(p,'C8',67,104,270);r4=gp(p,'R4',88,104,270)
# Local labels keep the enable tie and the compact LDO drawing unambiguous.
for n in ['1','3']:p.label('V5_INTERNAL',u[n])
p.label('GND',u['2']);p.label('+3V3',u['5'],180)
for c,net in [(c7,'V5_INTERNAL'),(c8,'+3V3'),(r4,'+3V3')]:p.label(net,c['1']);p.label('GND',c['2'])
p.flag('GND',375.92,195.58);p.flag('VIN_PROT',375.92,215.9);p.flag('V5_INTERNAL',375.92,236.22)
p.text('6-22 V input target. Single buck: 5.07 V nominal.\nProtected 12 V boost supply is on the next sheet.\nR1/R2 = 102k / 13.7k, 0.1%. The boost input is fed by this 5 V rail through U9.\nTP1 is ground; use selectors/capacitor pads for rail checks.',243,246,1.0)

p=pages['sensor_power']
p.text('HARDWARE CURRENT LIMITING; NO FIRMWARE ENABLE',15,28,1.8)
p.place('U4',85,70)
for ref,x,y in [('R10',155,70),('C11',235,70),('C12',315,70)]:p.place(ref,x,y)
p.text('5 V sensor output: TPS2553-1 latch-off version, EN tied to input.\n59k current-limit resistor. Cycle board power to clear overload.\nFAULT_N goes to MCU PA4, with a firmware-enabled pull-up.\nDesign target: 300mA combined load on this rail, not per connector.\nDo not back-power either sensor supply output.',25,110,1.5)

p=pages['regulated_12v']
p.place('U9',80,65);p.place('U8',240,65)
for ref,x,y in [('C65',45,120),('R62',115,120),('C60',190,120),('C61',270,120),('C66',350,120),
 ('L2',45,163),('D4',115,163),('C62',190,163),('C63',270,163),('C64',350,163),
 ('R60',45,205),('R61',115,205),('R63',190,205),('C69',270,205)]:p.place(ref,x,y)
p.place('U7',65,245,unit=4)
for ref,x in [('R65',155),('R66',245),('R67',335)]:p.place(ref,x,245)
p.flag('SENSOR_12V',360,205)
p.text('U9 limits BOOST INPUT current and latches OFF on overload; cycle input power to reset.\n12 V useful output: 300 mA shared. U7D senses rail voltage; U9 fault also pulls PG low.\n100nF soft start; 13k / 33nF compensation requires assembled-board loop and transient qualification.',15,272,1.05)

p=pages['controller']
u=p.place('U5',95,95,only=[str(n) for n in range(1,33) if n not in [1,5,17,16,32]])
for pins,net,y in [(['1','5','17'],'+3V3',63.5),(['16','32'],'GND',127)]:
    nodes=[(u[n][0],y) for n in pins];path(p,*nodes)
    for n,node in zip(pins,nodes):p.wire(u[n],node)
    end=(nodes[0][0]-12.7,y);p.wire(end,nodes[0]);p.label(net,end)
p.text('8 MHz CRYSTAL / PLL x6',218,28,1.8)
y=gp(p,'Y1',99,23);r=gp(p,'R20',128,23,180)
c1=gp(p,'C25',88,37,270);c2=gp(p,'C26',116,37,270)
a=(c1['1'][0],y['1'][1]);z=(c2['1'][0],y['3'][1])
path(p,a,y['1']);p.label('HSE_IN',a);p.wire(a,c1['1'])
path(p,y['3'],z,r['2']);p.wire(z,c2['1']);p.junction(z);p.label('HSE_XTAL_OUT',z)
p.label('HSE_OUT',r['1'],180)
cy=30*2.54
path(p,y['2'],(y['2'][0],cy),(y['4'][0],cy),y['4']);p.label('GND',(y['2'][0],cy))
for c in [c1,c2]:p.label('GND',c['2'])
p.text('RESET / BOOT / SERVICE',218,112,1.8)
r=gp(p,'R21',92,52,270);c=gp(p,'C27',108,62,270);mid=(r['2'][0],59*2.54)
p.label('+3V3',r['1']);path(p,r['2'],mid,(c['1'][0],mid[1]),c['1']);p.label('NRST',mid);p.label('GND',c['2'])
r=gp(p,'R22',92,77,270);p.label('BOOT0',r['1']);p.label('GND',r['2'])
gp(p,'J8',143,67,labels=True)
p.text('LOCAL DECOUPLING',15,148,1.8)
caps=[]
for i,ref in enumerate(['C20','C21','C22','C23','C24']):
    c=gp(p,ref,14+i*14,68,270);caps.append(c);p.label('GND',c['2'])
nodes=[(c['1'][0],63*2.54) for c in caps];path(p,*nodes);p.label('+3V3',nodes[0])
for c,node in zip(caps,nodes):p.wire(node,c['1']);p.junction(node)
p.text('TC2050-IDC-NL mechanical footprint; CUSTOM electrical pinout.\nPin 6 is 3.3 V reference OUTPUT, never a programming power input.\nUnused GPIOs are unconnected and initialized to analog mode.\nPA3 monitors 12 V PG; PA4 monitors active-low 5 V fault. No rail ADCs.',20,220,1.5)

p=pages['can']
u=gp(p,'U6',30,25)
for n in ['1','4','8']:p.label(PARTS['U6']['pins'][n],u[n])
p.label('GND',u['2'])
top_y=17*2.54
path(p,u['3'],(u['3'][0],top_y),(u['5'][0],top_y),u['5']);p.label('+3V3',(u['3'][0],top_y))
j=gp(p,'J2',75,24.5);gp(p,'J3',121,24.5,labels=True)
for n,m in [('7','1'),('6','2')]:path(p,u[n],j[m])
p.label('CANH',j['1']);p.label('CANL',j['2'])
gp(p,'R42',54,39,labels=True);gp(p,'JP2',75,39,labels=True)
gp(p,'D20',121,42,labels=True)
for ref,gx,net in [('R40',20,'CAN_STB'),('R41',48,'CAN_TX')]:
    r=gp(p,ref,gx,58,270);p.label('+3V3',r['1']);p.label(net,r['2'])
for ref,gx in [('C40',76),('C41',102)]:
    c=gp(p,ref,gx,58,270);p.label('+3V3',c['1']);p.label('GND',c['2'])
p.text('1 Mbit/s. Bridge JP2 only at a physical CAN trunk end.\nTCAN3413 uses 3.3 V for both VCC and VIO.\nSTB pull-up keeps the bus silent during MCU reset.\nCAN ground is shared through the power connection.',230,175,1.3)
p.text('SINGLE STATUS INDICATOR',15,195,1.8)
for i in range(1):
    r=gp(p,f'R{30+i}',18+i*23,86,270);d=gp(p,f'D{10+i}',18+i*23,96,270)
    p.label(PARTS[f'R{30+i}']['pins']['1'],r['1']);path(p,r['2'],d['2']);p.label('GND',d['1'])
    p.label(PARTS[f'R{30+i}']['pins']['2'],(r['2'][0],(r['2'][1]+d['2'][1])/2))

for ch in range(1,4):
    p=pages[f'input{ch}'];z=ch*100
    p.text('CAN-CONFIGURED INPUT BIAS / REMOVABLE SENSOR POWER',15,22,1.7)
    for ref,x,y in [(f'J{ch+3}',35,48),(f'JP{z+1}',115,48),(f'Q{z+1}',215,48),(f'Q{z+2}',320,48),
                     (f'R{z+11}',40,95),(f'R{z+12}',115,95),(f'D{z+2}',190,95),(f'R{z+10}',265,95),(f'R{z+9}',340,95)]:p.place(ref,x,y)
    p.text('POWER: one 2 mm cap, 1-2=5 V or 2-3=12 V; no cap=off.\nBIAS: 1k pull-up to internal 3.3 V through PMOS/diode; 10k pull-down through 60 V NMOS.\nBoth gates return OFF during reset. Software selects UP / DOWN / OFF / FLOAT / KEEPER. No bias bridges.',15,127,1.2)
    # Connected signal divider, input filter and positive feedback.
    rr=p.place(f'R{z+1}',65,176,labels=False)
    tv=p.place(f'D{z+1}',25.4,201.93,90,labels=False)
    rg=p.place(f'R{z+3}',109.22,204.47,270,labels=False)
    cf=p.place(f'C{z+1}',147.32,204.47,270,labels=False)
    u=p.place('U7',220.98,178.435,unit=ch,labels=False)
    fb=p.place(f'R{z+4}',185.42,156.21,180,labels=False)
    pu=p.place(f'R{z+5}',281.94,163.83,270,labels=False)
    op=str([2,1,14][ch-1]);plus=str([5,7,9][ch-1]);minus=str([4,6,8][ch-1])
    raw=(tv['1'][0],rr['1'][1]);p.label(f'SIG{ch}',raw);path(p,raw,rr['1']);path(p,raw,tv['1']);p.junction(raw);p.label('GND',tv['2'])
    sy=rr['2'][1];sx=195.58
    path(p,rr['2'],(sx,sy),(sx,u[plus][1]),u[plus]);p.label(f'SENSE{ch}',(sx,sy))
    for c in [rg,cf]:p.wire((c['1'][0],sy),c['1']);p.junction((c['1'][0],sy));p.label('GND',c['2'])
    p.label('REF_LOGIC',u[minus])
    oy=u[op][1];ox=322.58
    path(p,u[op],(ox,oy));p.label(f'INPUT{ch}',(ox,oy),180)
    path(p,pu['2'],(pu['2'][0],oy));p.junction((pu['2'][0],oy));p.label('+3V3',pu['1'])
    path(p,(ox,oy),(ox,fb['1'][1]),fb['1']);path(p,fb['2'],(sx-25.4,fb['2'][1]),(sx-25.4,sy));p.junction((sx-25.4,sy))
    if ch==1:
        for ref,x,y in [('R52',38.1,225),('R50',38.1,247.65),('R51',114.3,247.65),('C51',190.5,247.65),('C50',337.82,247.65)]:p.place(ref,x,y)
        p.place('U7',292.1,247.65,unit=5)
    else:p.text('The reference divider/filter and comparator power connections are on input1.\nOne fixed logic-compatible threshold for all three channels; no industrial threshold selector.',20,243,1.5)
    p.text('0-30 V signal design range; software debounce follows the hardware filter.\nNominal thresholds near 2.0 V rising / 1.65 V falling. Final bounds are in electrical_checks.json.\nNo analog measurement, 1.8 V logic guarantee or CTRE protocol compatibility.',15,273,1.1)

# Check every physical unit appears exactly once before writing.
placed=[(ref,u) for p in pages.values() for ref,u in p.used]
assert len(placed)==len(set(placed)), 'Duplicated schematic unit'
for ref,c in PARTS.items():
    for u in SYMS[c['kind']]['units']:
        assert (ref,u) in placed, f'Missing unit {ref}.{u}'
for page in pages.values():page.save()

root=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(rootid)}) (paper "A3") (title_block (title "FRC Sensor CAN") (date "2026-09-08") (rev "F") (comment 1 "Original design - custom WPILib CAN protocol")) (lib_symbols)'
for i,name in enumerate(SHEETS):
    x=25+(i%4)*95;y=90+(i//4)*85;si=uid('sheet_'+name)
    root+=f'(sheet (at {x} {y}) (size 75 45) (stroke (width .254) (type solid)) (fill (color 0 0 0 0)) (uuid {q(si)})'
    root+=prop('Sheetname',TITLES[name],x,y-3,justify='left')+prop('Sheetfile',name+'.kicad_sch',x,y+48,justify='left')
    root+=f'(instances (project "FRC_Sensor_CAN" (path {q("/"+rootid)} (page {q(i+2)})))))'
root+=f'(text {q("FRC SENSOR CAN - REVISION F REGULATED PROTOTYPE")} (at 25 25 0) {fx(3.81,"left")} (uuid {q(uid("root_title"))}))'
root+=f'(text {q("Three fixed-threshold digital inputs. 6-22 V input; regulated 12 V and 5 V sensor power.\nSTM32F042 + TCAN3413. Digital status and edge counts over a custom team CAN protocol.\nNot a CTRE Phoenix-compatible device. Inspect and bench-test prototypes before robot use.")} (at 25 43 0) {fx(2,"left top")} (uuid {q(uid("root_note"))}))'
root+='(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
(OUT/'FRC_Sensor_CAN.kicad_sch').write_text(root)
(OUT/'library/FRC_Sensor_CAN.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+'\n'.join(s['text'] for s in SYMS.values())+'\n)')
(OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "FRC_Sensor_CAN")(type "KiCad")(uri "${KIPRJMOD}/library/FRC_Sensor_CAN.kicad_sym")(options "")(descr "Project symbols, datasheet pin mapping")))\n')
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "FRC_Sensor_CAN")(type "KiCad")(uri "${KIPRJMOD}/library/FRC_Sensor_CAN.pretty")(options "")(descr "Project footprints")))\n')
# Save original physical model without virtual ERC flags.
for k in list(PARTS):
    if k.startswith('#'):del PARTS[k]
export()
(OUT/'design/symbol_pinmap.json').write_text(json.dumps({k:v['units'] for k,v in SYMS.items()},indent=2)+'\n')
print('Generated hierarchical KiCad schematic and project symbol library.')
