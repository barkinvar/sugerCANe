"""Verify deliverable memory ranges, Intel HEX checksums and combined-image parity."""
from pathlib import Path
import hashlib,json,struct,sys
from elftools.elf.elffile import ELFFile
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'host'))
from firmware_image import unpack,manifest,APP_BASE,MANIFEST
B=R/'firmware/build';data,crc,version=unpack((B/'application.sc12').read_bytes())
assert data==(B/'sensor_can.bin').read_bytes()+b'\xff'*(-(B/'sensor_can.bin').stat().st_size%4)
flash={};base=0;ended=False
for line in (B/'factory.hex').read_text().splitlines():
 row=bytes.fromhex(line[1:]);assert line.startswith(':') and sum(row)%256==0 and len(row)==row[0]+5
 n,address,kind=row[0],int.from_bytes(row[1:3],'big'),row[3]
 if kind==4:base=int.from_bytes(row[4:6],'big')<<16
 elif kind==0:
  for off,value in enumerate(row[4:4+n]):
   a=base+address+off;assert a not in flash and 0x08000000<=a<0x08007800;flash[a]=value
 elif kind==1:ended=True
 else:raise AssertionError(kind)
assert ended
for address,expected in [(0x08000000,(B/'bootloader.bin').read_bytes()),(APP_BASE,data),(MANIFEST,manifest(data))]:
 assert bytes(flash[address+i] for i in range(len(expected)))==expected
regions=[]
for name,low,high in [('bootloader',0x08000000,APP_BASE),('sensor_can',APP_BASE,MANIFEST)]:
 with (B/(name+'.elf')).open('rb') as f:
  elf=ELFFile(f);ram=0
  for s in elf.iter_sections():
   if not s['sh_flags']&2 or not s['sh_size']:continue
   a,n=s['sh_addr'],s['sh_size']
   if 0x08000000<=a<0x10000000:assert low<=a and a+n<=high
   else:assert 0x20000100<=a and a+n<=0x20001800;ram+=n
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  assert symbols['_estack']==0x20001800
  regions.append(dict(image=name,flash_bytes=(B/(name+'.bin')).stat().st_size,flash_capacity=high-low,allocated_ram_including_minimum_stack=ram,ram_capacity=5888,minimum_stack_reservation=1024))
report=dict(result='PASS',regions=regions,update_crc32=f'{crc:08x}',version=version,factory_hex_excludes_configuration=True,images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in B.iterdir() if p.suffix in ('.elf','.hex','.bin','.sc12')},limitations='Static link/image checks; runtime stack and silicon handoff unmeasured')
(R/'reports/firmware-images.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
