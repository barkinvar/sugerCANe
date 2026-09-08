"""Execute the actual linked Cortex-M0 functions against explicit register models.

Unicorn emulates CPU instructions, not STM32 peripherals. The small behavioral
models below supply ready bits, ADC samples, FIFO contents, flash erase and GPIO
BSRR effects. These tests check compiled register/pin intent and data handling;
no electrical behavior, interrupt timing, CAN arbitration or silicon erratum is
validated by this harness. Host application/core tests remain separate.
"""
from pathlib import Path
import json,struct,hashlib,time
import unicorn as uc
from unicorn import arm_const as ar
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[2]
ELF=ROOT/'firmware/build/sensor_can.elf'
FLASH=0x08000000;RAM=0x20000000;STOP=FLASH+0x7000
RCC=0x40021000;GPIOA=0x48000000;GPIOB=0x48000400;GPIOF=0x48001400
CAN=0x40006400;ADC=0x40012400;UART=0x40013800;FCTL=0x40022000
PWR=0x40007000;EXTI=0x40010400;IWDG=0x40003000
with ELF.open('rb') as f:
    elf=ELFFile(f)
    symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name}
    initialized=[(s['sh_addr'],s.data()) for s in elf.iter_sections()
                 if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS' and s['sh_size']]
class PowerLoss(Exception):
    pass

class Board:
    def __init__(self):
        self.u=uc.Uc(uc.UC_ARCH_ARM,uc.UC_MODE_THUMB|uc.UC_MODE_MCLASS)
        self.u.ctl_set_cpu_model(ar.UC_CPU_ARM_CORTEX_M0)
        for base,size in [(FLASH,0x8000),(RAM,0x2000),(0x40000000,0x30000),
                          (0x48000000,0x2000),(0xe000e000,0x2000),(0x1ffff000,0x1000)]:self.u.mem_map(base,size)
        self.u.mem_write(FLASH,b'\xff'*0x8000)
        self.u.mem_write(STOP,b'\x00\xbf')
        for address,data in initialized:self.u.mem_write(address,data)
        self.write(GPIOA,0x28000000) # PA13/PA14 reset SWD alternate functions.
        self.write(RCC,3) # HSI on/ready.
        self.write(0x1ffff7ba,1500,2)
        self.hse=True;self.pll=True;self.adc_ready=True;self.adc_samples={17:1500,4:1354,5:3102}
        self.adc_status=0;self.adc_channels=[];self.uart_status=0xc0;self.tx=[]
        self.fifos=[[],[]];self.can_ack_init=True;self.flash_status=0;self.flash_unlocked=False;self.flash_key=0
        self.flash_writes=[];self.erases=[];self.cut_after=None;self.flash_error_after=None;self.trace=[];self.returned=False
        self.u.hook_add(uc.UC_HOOK_MEM_READ,self.on_read,begin=0x40000000,end=0x48001fff)
        self.u.hook_add(uc.UC_HOOK_MEM_WRITE,self.on_write,begin=0x40000000,end=0x48001fff)
        self.u.hook_add(uc.UC_HOOK_MEM_WRITE,self.on_flash,begin=FLASH+0x7800,end=FLASH+0x7fff)
        self.u.hook_add(uc.UC_HOOK_CODE,self.on_stop,begin=STOP,end=STOP)
    def read(self,address,size=4):return int.from_bytes(self.u.mem_read(address,size),'little')
    def write(self,address,value,size=4):self.u.mem_write(address,int(value).to_bytes(size,'little'))
    def on_stop(self,*args):self.returned=True;self.u.emu_stop()
    def on_read(self,u,access,a,size,value,data):
        if a==RCC:
            v=self.read(a);v=(v&~((1<<17)|(1<<25)))|((1<<17) if v&(1<<16) and self.hse else 0)|((1<<25) if v&(1<<24) and self.pll else 0);self.write(a,v)
        elif a==RCC+4:
            v=self.read(a);self.write(a,(v&~12)|((v&3)<<2))
        elif a==RCC+0x34:
            v=self.read(a);self.write(a,v|2 if v&1 else v&~2)
        elif a==CAN+4:self.write(a,1 if self.read(CAN)&1 and self.can_ack_init else 0)
        elif a in (CAN+0xc,CAN+0x10):self.write(a,len(self.fifos[(a-CAN-0xc)//4]))
        elif CAN+0x1b0<=a<CAN+0x1d0:
            fifo=(a-CAN-0x1b0)//16;off=(a-CAN-0x1b0)%16
            if self.fifos[fifo]:self.write(a,self.fifos[fifo][0][off//4])
        elif a==ADC+8:
            v=self.read(a)&~((1<<31)|(1<<2));self.write(a,v)
        elif a==ADC:self.write(a,self.adc_status if self.adc_ready else 0)
        elif a==UART+0x1c:self.write(a,self.uart_status)
        elif a==UART+0x24:self.uart_status&=~0x20
        elif a==FCTL+0xc:self.write(a,self.flash_status)
    def on_write(self,u,access,a,size,v,data):
        self.trace.append((a,size,v))
        for port in [GPIOA,GPIOB,GPIOF]:
            if a==port+0x18:self.write(port+0x14,(self.read(port+0x14)|(v&0xffff))&~(v>>16))
        if a==ADC+8:
            if v&1:self.adc_status|=1
            if v&4:
                selected=self.read(ADC+0x28);assert selected and selected&(selected-1)==0
                ch=selected.bit_length()-1;self.adc_channels.append(ch)
                self.write(ADC+0x40,self.adc_samples[ch]);self.adc_status|=12
        elif a==ADC:self.adc_status&=~v
        elif a in (CAN+0xc,CAN+0x10) and v&0x20:
            self.fifos[(a-CAN-0xc)//4].pop(0)
        elif a==UART+0x28:self.tx.append(v&255)
        elif a==UART+0x20:self.uart_status&=~v
        elif a==FCTL+4:
            if v==0x45670123:self.flash_key=1
            elif v==0xcdef89ab and self.flash_key==1:self.flash_unlocked=True
            else:raise AssertionError('Unexpected flash unlock sequence')
        elif a==FCTL+0xc:self.flash_status&=~v
        elif a==FCTL+0x10:
            if v&0x40 and v&2:
                assert self.flash_unlocked
                address=self.read(FCTL+0x14);assert address in (FLASH+0x7800,FLASH+0x7c00)
                self.u.mem_write(address,b'\xff'*1024);self.erases.append(address)
            if v&0x80:self.flash_unlocked=False
    def on_power_cut(self,*args):
        if self.erases and len(self.flash_writes)>=self.cut_after:raise PowerLoss()
    def on_flash(self,u,access,a,size,v,data):
        assert self.flash_unlocked and self.read(FCTL+0x10)&1
        if self.flash_error_after is not None and len(self.flash_writes)==self.flash_error_after:self.flash_status|=4
        assert size==2 and self.read(a,2)&v==v
        self.flash_writes.append((a,size,v))
    def call(self,name,*args,limit=5000000,returns=True):
        for reg in range(ar.UC_ARM_REG_R0,ar.UC_ARM_REG_R12+1):self.u.reg_write(reg,0)
        for reg,arg in zip([ar.UC_ARM_REG_R0,ar.UC_ARM_REG_R1,ar.UC_ARM_REG_R2,ar.UC_ARM_REG_R3],args):self.u.reg_write(reg,arg)
        self.u.reg_write(ar.UC_ARM_REG_SP,RAM+0x1800);self.u.reg_write(ar.UC_ARM_REG_LR,STOP|1)
        self.u.reg_write(ar.UC_ARM_REG_XPSR,1<<24);self.returned=False
        try:self.u.emu_start(symbols[name]|1,FLASH+0x8000,count=limit)
        except uc.UcError:
            print(name, 'PC',hex(self.u.reg_read(ar.UC_ARM_REG_PC)),'SP',hex(self.u.reg_read(ar.UC_ARM_REG_SP)),'LR',hex(self.u.reg_read(ar.UC_ARM_REG_LR)), 'recent writes', self.trace[-4:])
            raise
        assert self.returned==returns,(name,'return mismatch',hex(self.u.reg_read(ar.UC_ARM_REG_PC)))
        return self.u.reg_read(ar.UC_ARM_REG_R0)
    def receive(self,fifo,identifier,payload,ide=True,rtr=False,dlc=None):
        rid=(identifier<<3 if ide else identifier<<21)|(4 if ide else 0)|(2 if rtr else 0)
        padded=payload.ljust(8,b'\0');lo,hi=struct.unpack('<II',padded)
        self.fifos[fifo].append((rid,len(payload) if dlc is None else dlc,lo,hi))

def mode(b,port,pin):return (b.read(port)>>(2*pin))&3
def af(b,port,pin):return (b.read(port+0x20+(pin//8)*4)>>((pin%8)*4))&15
checks=[]
def passed(name):checks.append(name);print('PASS',name)
start=time.monotonic()
b=Board();b.call('board_gpio_init')
assert b.read(GPIOA+0x14)&(1<<8) and b.read(GPIOB+0x14)&3==0
for pin in [0,1,2,3]:assert mode(b,GPIOA,pin)==0
for pin in [4,5]:assert mode(b,GPIOA,pin)==3
for pin in [6,7,8,15]:assert mode(b,GPIOA,pin)==1
for pin in [0,1,3,6,7]:assert mode(b,GPIOB,pin)==1
for pin in [4,5]:assert mode(b,GPIOB,pin)==0
for pin in [13,14]:assert mode(b,GPIOA,pin)==2
for mask in range(4):
    b.call('board_set_rails',mask);assert b.read(GPIOB+0x14)&3==((mask&1)<<1)|((mask&2)>>1)
for mask in range(4):
    b.write(GPIOB+0x10,(0x30&~(((mask&1)<<5)|((mask&2)<<3))))
    assert b.call('board_faults')==mask
for bits in range(16):
    b.call('board_leds',bits,1,1)
    assert (b.read(GPIOA+0x14)>>6)&3==bits&3
    assert (b.read(GPIOB+0x14)>>6)&3==(bits>>2)&3
    assert b.read(GPIOA+0x14)&(1<<15) and b.read(GPIOB+0x14)&8
b.call('board_safe_off');assert b.read(GPIOB+0x14)&3==0 and b.read(GPIOA+0x14)&256
passed('GPIO directions, SWD preservation, all rail/fault masks, LEDs and safe-off')
assert b.call('board_clock_init')==1 and b.read(symbols['SystemCoreClock'])==48000000
assert b.read(RCC+4)&3==2 and b.read(RCC+4)&0x003c0000==0x00100000
assert b.read(FCTL)&1 and b.read(RCC)&(1<<19)
passed('8 MHz HSE to 48 MHz PLL, flash wait state and clock-security setup')
f=Board();f.hse=False;assert f.call('board_clock_init')==0 and f.read(symbols['SystemCoreClock'])==8000000
passed('Bounded HSE startup failure')
b.call('board_voltage_guard_init')
assert b.read(PWR)&0xf0==0xf0 and b.read(EXTI)&(1<<16) and b.read(EXTI+8)&(1<<16)
b.call('board_watchdog_start');assert b.read(IWDG+4)==4 and b.read(IWDG+8)==624 and b.read(IWDG)==0xaaaa
b.call('board_set_rails',3);b.write(PWR+4,4);b.call('PVD_VDDIO2_IRQHandler',limit=1000,returns=False)
assert b.read(GPIOB+0x14)&3==0 and b.read(GPIOA+0x14)&256
passed('PVD and watchdog register setup; undervoltage handler forces safe-off')
# A fresh model avoids the deliberately non-returning exception state.
b=Board();b.call('board_gpio_init');b.call('board_clock_init')
for node in [0,1,17,63]:
    assert b.call('board_can_init',node)==1
    assert af(b,GPIOA,11)==af(b,GPIOA,12)==4
    timing=b.read(CAN+0x1c);prescaler=(timing&1023)+1;t1=((timing>>16)&15)+1;t2=((timing>>20)&7)+1
    assert 48000000//(prescaler*(1+t1+t2))==1000000 and (1+t1)/(1+t1+t2)==.875
    assert b.read(CAN+0x20c)&3==3 and b.read(CAN+0x214)&3==2 and b.read(CAN+0x21c)&3==3
    fr=[(b.read(CAN+0x240+i*8),b.read(CAN+0x244+i*8)) for i in range(2)]
    def accepts(bank,id,ide=True,rtr=False):
        encoded=(id<<3 if ide else id<<21)|(4 if ide else 0)|(2 if rtr else 0)
        return (encoded&fr[bank][1])==(fr[bank][0]&fr[bank][1])
    for other in range(64):
        for api in [0,1,63,64,511,1023]:
            identifier=(10<<24)|(8<<16)|(api<<6)|other
            assert accepts(0,identifier)==(other==node)
            assert not accepts(0,identifier,rtr=True)
            assert not accepts(0,identifier^(1<<16))
            assert not accepts(1,identifier)
    assert accepts(1,0) and not accepts(1,0,ide=False) and not accepts(1,0,rtr=True)
passed('Compiled CAN timing, pin mux, Team Use filters and dedicated Broadcast Disable FIFO')
data=RAM+0x1000;b.u.mem_write(data,b'\x01\x23\x45\x67\x89\xab\xcd\xef')
for mailbox in range(3):
    b.write(CAN+8,1<<(26+mailbox));b.write(CAN+0x18,0)
    assert b.call('board_can_send',0x0a080043,data)==1
    base=CAN+0x180+mailbox*16
    assert b.read(base)==(0x0a080043<<3)|5 and b.read(base+4)==8
    assert bytes(b.u.mem_read(base+8,8))==bytes(b.u.mem_read(data,8))
b.write(CAN+8,0);assert b.call('board_can_send',123,data)==0
b.write(CAN+8,7<<26);b.write(CAN+0x18,4);assert b.call('board_can_send',123,data)==0
passed('All CAN transmit mailboxes, byte order, busy and bus-off rejection')
ptr_id,ptr_data,ptr_len=RAM+0x1100,RAM+0x1110,RAM+0x1120
b.receive(0,0x0a084043,b'12345678');b.receive(1,0,b'')
assert b.call('board_can_receive',ptr_id,ptr_data,ptr_len)==1 and b.read(ptr_id)==0 and b.read(ptr_len,1)==0
assert b.call('board_can_receive',ptr_id,ptr_data,ptr_len)==1 and b.read(ptr_id)==0x0a084043
assert bytes(b.u.mem_read(ptr_data,8))==b'12345678'
for kw in [dict(ide=False),dict(rtr=True),dict(dlc=9)]:
    b.receive(0,42,b'12345678',**kw);assert b.call('board_can_receive',ptr_id,ptr_data,ptr_len)==1
    assert b.read(ptr_id)==0xffffffff and b.read(ptr_len,1)==0
assert b.call('board_can_receive',ptr_id,ptr_data,ptr_len)==0
passed('Receive FIFO priority, payload extraction and invalid frame rejection')
assert b.call('board_adc_init')==1 and b.read(ADC+0x14)&7==7 and b.read(0x40012708)&(1<<22)
a,c=RAM+0x1140,RAM+0x1142
assert b.call('board_adc_millivolts',a,c)==1 and b.adc_channels[-3:]==[17,4,5]
assert b.read(a,2)==1354*3300*11//4095 and b.read(c,2)==3102*3300*2//4095
b.adc_samples[17]=0;assert b.call('board_adc_millivolts',a,c)==0
b.adc_samples[17]=1500;b.write(0x1ffff7ba,0xffff,2);assert b.call('board_adc_millivolts',a,c)==0
passed('ADC calibration/setup, channel order, factory-reference scaling and invalid calibration')
b.call('board_uart_init');assert af(b,GPIOA,9)==af(b,GPIOA,10)==1 and b.read(UART+0xc)==417
for byte in b'INFO\r\n':
    b.write(UART+0x24,byte);b.uart_status|=0x20;b.call('USART1_IRQHandler')
for byte in b'INFO\r\n':assert b.call('board_uart_get')==byte
assert b.call('board_uart_get')==0xffffffff
b.uart_status|=8;b.call('USART1_IRQHandler');assert b.call('board_uart_get')==0xfffffffe
assert b.call('board_uart_get')==0xffffffff
b.u.mem_write(data,b'Hello CAN\r\n\0');b.call('board_uart_write',data)
for _ in range(13):b.call('USART1_IRQHandler')
assert bytes(b.tx)==b'Hello CAN\r\n'
passed('UART baud/pin mux, ISR receive/transmit buffers and error reporting')
f=Board();assert f.call('board_config_load')==0
record=RAM+0x1000
# Record fields are specified in sensor_core.h; magic/sequence/CRC/commit are
# intentionally left blank for the actual production flash routine to generate.
r=bytearray(32);r[10]=17;r[11]=5;struct.pack_into('<H',r,12,2);r[14]=3
f.u.mem_write(record,bytes(r))
assert f.call('board_config_store',record)==1
assert f.erases==[FLASH+0x7800] and len(f.flash_writes)==16
assert f.flash_writes[-1][0]==FLASH+0x781e and not f.flash_unlocked
assert f.call('board_config_load')==FLASH+0x7800
assert f.call('board_config_store',record)==1 and f.erases[-1]==FLASH+0x7c00
assert f.call('board_config_load')==FLASH+0x7c00
# Corrupt latest record; production integrity check must recover the older page.
f.write(FLASH+0x7c00+10,0xff,1)
assert f.call('board_config_load')==FLASH+0x7800
passed('Actual flash unlock/erase/halfword order, alternating pages and corrupt-record fallback')
# Exercise byte-program interruption at every halfword of the actual routine.
# The emulator is restarted with the resulting flash bytes to model a reset;
# analog erase/program brownout behavior is outside this digital test.
for existing in [False,True]:
    seed=Board()
    seed.u.mem_write(record,bytes(r))
    if existing:assert seed.call('board_config_store',record)==1
    snapshot=bytes(seed.u.mem_read(FLASH+0x7800,2048))
    for cut in range(17):
        trial=Board();trial.u.mem_write(FLASH+0x7800,snapshot)
        newer=bytearray(r);newer[10]=37;trial.u.mem_write(record,bytes(newer));trial.cut_after=cut
        trial.u.hook_add(uc.UC_HOOK_CODE,trial.on_power_cut,begin=FLASH,end=FLASH+0x6fff)
        try:
            assert trial.call('board_config_store',record)==1
            raise AssertionError('Expected modeled power interruption')
        except PowerLoss:
            assert len(trial.flash_writes)==cut
        reboot=Board();reboot.u.mem_write(FLASH+0x7800,bytes(trial.u.mem_read(FLASH+0x7800,2048)))
        loaded=reboot.call('board_config_load')
        if cut==16:assert loaded and reboot.read(loaded+10,1)==37
        elif existing:assert loaded and reboot.read(loaded+10,1)==17
        else:assert loaded==0
failed=Board();failed.u.mem_write(record,bytes(r));failed.flash_error_after=0
assert failed.call('board_config_store',record)==0 and not failed.flash_unlocked
assert failed.call('board_config_load')==0
passed('34 compiled flash halfword power-cut cases and programming-error rejection')
u=Board();u.call('board_gpio_init');u.call('board_clock_init');u.call('board_uart_init')
for n in range(140):
    u.write(UART+0x24,n&255);u.uart_status|=0x20;u.call('USART1_IRQHandler')
assert u.call('board_uart_get')==0xfffffffe
for n in range(127):assert u.call('board_uart_get')==n
assert u.call('board_uart_get')==0xffffffff
u.u.mem_write(data,b'x'*600+b'\0');u.call('board_uart_write',data)
for _ in range(520):u.call('USART1_IRQHandler')
assert bytes(u.tx)==b'x'*511
passed('UART RX overflow ordering and bounded TX buffer under flooding')
slow=Board();slow.adc_ready=False
assert slow.call('board_adc_init')==0
bad=Board();bad.call('board_adc_init');bad.adc_samples[17]=100
assert bad.call('board_adc_millivolts',a,c)==0
passed('ADC-ready timeout and implausible supply-reference rejection')
report=dict(result='PASS',completed_checks=checks,elapsed_seconds=time.monotonic()-start,
            emulator='Unicorn2.1.4 Cortex-M0',elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),
            binary_sha256=hashlib.sha256((ELF.parent/'sensor_can.bin').read_bytes()).hexdigest(),
            limits=__doc__.strip(),sources=['https://github.com/unicorn-engine/unicorn',
            'firmware/third_party/cmsis_device_f0/Include/stm32f042x6.h'])
(ROOT/'reports/firmware-arm-registers.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='completed_checks'},indent=2))
