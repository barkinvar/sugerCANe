"""Conservative static stack review of this exact linked Cortex-M0 firmware.

GCC .su frames are combined along direct linked call/tail-branch paths. The
few linked library frames are measured from their simple push/sub prologues.
Unsupported indirect runtime calls or recursion fail the screen. This is not
runtime stack watermarking, cycle timing or a general-purpose binary analyzer.
"""
from pathlib import Path
import subprocess,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'firmware/build'
elf=BUILD/'sensor_can.elf'
asm=subprocess.check_output(['arm-none-eabi-objdump','-d',str(elf)],text=True)
(ROOT/'reports/firmware-disassembly.txt').write_text(asm)
functions={};current=None
for line in asm.splitlines():
    m=re.match(r'^[0-9a-f]+ <([^>]+)>:',line)
    if m:current=m[1];functions[current]=[]
    elif current and re.match(r'^\s*[0-9a-f]+:',line):functions[current].append(line)
frames={};origin={}
for path in BUILD.glob('*.su'):
    for line in path.read_text().splitlines():
        location,size,kind=line.split('\t');name=location.rsplit(':',1)[-1]
        assert kind=='static',(name,kind)
        frames[name]=int(size);origin[name]='GCC -fstack-usage'
# These are the only library leaves/helpers reached after main begins. Verify
# their exact instruction patterns below rather than assigning an opaque budget.
libraries={'__udivsi3','__aeabi_uidivmod','__aeabi_idiv0','memcpy','memset','strcmp','strncmp'}
for name in libraries:
    stack=0
    for line in functions[name]:
        instruction=line.split('\t')[-2:] if '\t' in line else []
        m=re.search(r'\bpush\s+\{([^}]+)\}',line)
        if m:stack+=4*len(m[1].split(','))
        m=re.search(r'\bsub(?:s)?\s+sp,\s*#(\d+)',line)
        if m:stack+=int(m[1])
        assert not re.search(r'\bmov(?:s)?\s+sp,|\bsub(?:s)?\s+sp,\s*r|\bstmdb\s+sp',line),(name,line)
    frames[name]=stack;origin[name]='Linked assembly push/sub inspection'
calls={};indirect={}
for name,lines in functions.items():
    calls[name]=set();indirect[name]=[]
    for line in lines:
        m=re.search(r'\b(?:bl|b(?:\.n)?|b(?:eq|ne|cs|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)(?:\.n)?)\s+[0-9a-f]+ <([^>]+)>',line)
        if m:
            target=m[1].split('+')[0]
            if target!=name:calls[name].add(target)
            elif re.search(r'\bbl\s',line):raise AssertionError(('Recursion',name))
        if re.search(r'\bblx\s|\bbx\s+(?!lr\b)',line):indirect[name].append(line)
visited=set()
def bound(name,path=()):
    assert name not in path,('Call cycle',path,name)
    assert name in frames,('Missing frame review',name)
    assert not indirect[name],('Indirect runtime transfer',name,indirect[name])
    visited.add(name)
    children=[bound(child,path+(name,)) for child in sorted(calls[name])]
    child=max(children,key=lambda v:v[0]) if children else (0,[])
    return frames[name]+child[0],[name]+child[1]
foreground,chain=bound('main')
handlers=['SysTick_Handler','USART1_IRQHandler','PVD_VDDIO2_IRQHandler','HardFault_Handler','NMI_Handler']
interrupts={name:dict(zip(['software_stack_bytes','deepest_chain'],bound(name))) for name in handlers}
# Deliberately count every enabled/fault handler as if simultaneously nested;
# actual priority rules prevent some combinations. Allow36B hardware frame each
# (eight registers plus possible alignment word) and retain all foreground frames.
exception_allowance=sum(v['software_stack_bytes']+36 for v in interrupts.values())
estimate=foreground+exception_allowance
nm=subprocess.check_output(['arm-none-eabi-nm','-n',str(elf)],text=True)
symbols={m[2]:int(m[0],16) for l in nm.splitlines() if len(m:=l.split())==3}
for prefix in ['__preinit_array','__init_array']:
    assert symbols[prefix+'_start']==symbols[prefix+'_end'],'Startup indirect constructors require review'
reserved=symbols['_Min_Stack_Size'];available=symbols['_estack']-symbols['_ebss']
assert estimate<=reserved,(estimate,reserved)
report=dict(result='PASS',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
            firmware_binary_sha256=hashlib.sha256((BUILD/'sensor_can.bin').read_bytes()).hexdigest(),
            foreground_stack_bytes=foreground,deepest_foreground_chain=chain,interrupts=interrupts,
            conservative_exception_allowance_bytes=exception_allowance,combined_estimate_bytes=estimate,
            linker_minimum_stack_bytes=reserved,actual_space_above_bss_bytes=available,
            reached_functions={n:dict(frame_bytes=frames[n],source=origin[n],callees=sorted(calls[n])) for n in sorted(visited)},
            limitations='Static screen of this linked build. Direct call/tail paths plus GCC frames; simple inspected library pushes. Counts all listed exceptions simultaneously with alignment allowance, conservatively. No dynamic allocation, variable frames, reachable indirect runtime calls or recursive graph accepted. Does not detect memory corruption, validate execution timing, or replace hardware stack watermarking. Startup constructor arrays are empty.')
(ROOT/'reports/firmware-stack.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='reached_functions'},indent=2))
