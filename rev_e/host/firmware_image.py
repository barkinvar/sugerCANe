"""SC12 update image validation and factory Intel HEX generation (stdlib only)."""
from pathlib import Path
import argparse
import struct
import zlib

MAGIC = b'SC12UPD1'
APP_BASE, APP_SIZE, MANIFEST = 0x08002000, 21*1024, 0x08007400
TAG, IMAGE_MAGIC, COMMIT = 0x53433135, 0x49324353, 0xc035a19e
HEADER = struct.Struct('<8s6I')

def unpack(raw):
    if len(raw) < HEADER.size:
        raise ValueError('Truncated SC12 update header')
    magic, fmt, hardware, base, length, crc, version = HEADER.unpack_from(raw)
    data = raw[HEADER.size:]
    if (magic, fmt, hardware, base) != (MAGIC, 1, 5, APP_BASE):
        raise ValueError('Wrong update format, hardware or application address')
    if len(data) != length or not 192 <= length <= APP_SIZE or length % 4:
        raise ValueError('Invalid application length')
    if zlib.crc32(data) != crc:
        raise ValueError('Application CRC mismatch')
    sp, pc = struct.unpack_from('<II', data)
    if not (0x20000100 <= sp <= 0x20001800 and sp % 8 == 0 and pc & 1 and
            APP_BASE+192 <= (pc & ~1) < APP_BASE+length):
        raise ValueError('Invalid application vectors')
    return data, crc, version

def pack(data, version=0x00000600):
    data += b'\xff' * (-len(data) % 4)
    raw = HEADER.pack(MAGIC, 1, 5, APP_BASE, len(data), zlib.crc32(data), version) + data
    unpack(raw)
    return raw

def manifest(data):
    m = struct.pack('<4I', IMAGE_MAGIC, len(data), zlib.crc32(data), TAG)
    return m + struct.pack('<II', zlib.crc32(m), COMMIT)

def intel_hex(segments):
    lines = []
    def record(addr, typ, data):
        row = bytes((len(data), addr >> 8, addr & 255, typ)) + data
        lines.append(':' + (row + bytes((-sum(row) & 255,))).hex().upper())
    for address, data in segments:
        record(0, 4, (address >> 16).to_bytes(2, 'big'))
        for off in range(0, len(data), 16):
            record((address+off) & 0xffff, 0, data[off:off+16])
    record(0, 1, b'')
    return '\n'.join(lines) + '\n'

def build(folder):
    boot = (folder/'bootloader.bin').read_bytes()
    if len(boot) > 8192:
        raise ValueError('Bootloader exceeds protected region')
    raw = pack((folder/'sensor_can.bin').read_bytes())
    data, _, _ = unpack(raw)
    (folder/'application.sc12').write_bytes(raw)
    (folder/'factory.hex').write_text(intel_hex([(0x08000000,boot),(APP_BASE,data),(MANIFEST,manifest(data))]))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', required=True, type=Path)
    build(p.parse_args().build)
