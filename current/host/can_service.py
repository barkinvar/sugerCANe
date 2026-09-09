"""SC12 maintenance over SocketCAN or the robot's localhost TCP bridge."""
from __future__ import annotations
import argparse
import json
import secrets
import socket
import struct
import time
from pathlib import Path
from input_settings import pack_settings, unpack_settings
from firmware_image import unpack, TAG, APP_SIZE

RX, TX = (10<<24)|(8<<16)|(0x300<<6), (10<<24)|(8<<16)|(0x301<<6)
OPEN, PREFIX0, PREFIX1, PREFIX2, PROBE, CLOSE = range(1,7)
INFO, BLINK, SAVE, BOOT, RUN, RATE, INPUTS, POWER = range(0x10,0x18)
SIZE, CRC, BEGIN, OFFSET, DATA, FINISH = range(0x20,0x26)
MAGIC = 0x314d4353
WIRE = struct.Struct('<BBHI')
ERRORS = {1:'invalid argument',2:'invalid state/offset',3:'flash operation failed',
          4:'image failed verification',5:'bootloader pages are not write-protected'}

class SocketCan:
    def __init__(self, interface, channel):
        try:import can
        except ImportError as error:raise RuntimeError("SocketCAN requires python-can; install it or use --bridge") from error
        self.can = can
        self.bus = can.Bus(interface=interface, channel=channel,
                           can_filters=[{'can_id':TX,'can_mask':0x1fffffff,'extended':True}])
    def send(self, data):
        try:self.bus.send(self.can.Message(arbitration_id=RX,is_extended_id=True,data=data),timeout=.3)
        except self.can.CanError as error:raise ConnectionError(str(error)) from error
    def recv(self, timeout):
        try:msg = self.bus.recv(timeout)
        except self.can.CanError as error:raise ConnectionError(str(error)) from error
        if msg is not None and msg.arbitration_id == TX and msg.is_extended_id and not (
                msg.is_remote_frame or msg.is_error_frame or msg.is_fd) and len(msg.data)==8:
            return bytes(msg.data)
        return None
    def close(self): self.bus.shutdown()

class TcpBridge:
    def __init__(self, address):
        host, port = address.rsplit(':',1)
        self.sock = socket.create_connection((host,int(port)),timeout=3)
        self.sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        self.buffer = bytearray()
    def send(self, data):
        self.sock.settimeout(1);self.sock.sendall(data)
    def recv(self, timeout):
        deadline=time.monotonic()+timeout
        while len(self.buffer)<8:
            remaining=deadline-time.monotonic()
            if remaining<=0:return None
            self.sock.settimeout(remaining)
            try: chunk=self.sock.recv(4096)
            except socket.timeout:return None
            if not chunk:raise ConnectionError('Maintenance bridge closed; check robot disabled state and maintenance permission')
            self.buffer.extend(chunk)
        result=bytes(self.buffer[:8]);del self.buffer[:8];return result
    def close(self):self.sock.close()

class Client:
    def __init__(self, transport, *, timeout=.3, probe_timeout=.05, spacing=.006):
        self.transport=transport;self.timeout=timeout;self.probe_timeout=probe_timeout
        self.spacing=spacing;self.sent=0.;self.sequence=0;self.token=0;self.prefix=None;self.uid=None
    def _frame(self, op, value):
        self.sequence=(self.sequence+1)&255
        return WIRE.pack(op,self.sequence,self.token,value)
    def _send(self, frame):
        wait=self.spacing-(time.monotonic()-self.sent)
        if wait>0:time.sleep(wait)
        self.transport.send(frame);self.sent=time.monotonic()
    def request(self, op, value=0, *, expect=None, timeout=None, attempts=4):
        frame=self._frame(op,value);seq=self.sequence
        for _ in range(attempts):
            self._send(frame);deadline=time.monotonic()+(self.timeout if timeout is None else timeout)
            while time.monotonic()<deadline:
                raw=self.transport.recv(max(0,deadline-time.monotonic()))
                if raw is None:break
                if len(raw)!=8:continue
                code,rseq,token,result=WIRE.unpack(raw)
                if token!=self.token or rseq!=seq:continue
                if code==(op|0xc0):raise RuntimeError(ERRORS.get(result,f'device error {result}'))
                if code==(op|0x80) and (expect is None or result==expect):return result
        raise TimeoutError(f'No acknowledgement for service operation 0x{op:02x}')
    def open(self):
        self.token=secrets.randbelow(65535)+1;self.prefix=None;self.uid=None
        self.request(OPEN,MAGIC,expect=MAGIC)
    def _prefix(self, raw, force=False):
        for n in range(3):
            if force or self.prefix is None or raw[4*n:4*n+4]!=self.prefix[4*n:4*n+4]:
                self._send(self._frame(PREFIX0+n,int.from_bytes(raw[4*n:4*n+4],'little')))
        self.prefix=raw
    def probe(self, prefix, bits):
        raw=prefix.to_bytes(12,'big');self._prefix(raw)
        try:self.request(PROBE,bits,expect=1,timeout=self.probe_timeout,attempts=2);return True
        except TimeoutError:return False
    def discover(self, maximum=64):
        found=[];stack=[(0,0)]
        while stack:
            prefix,bits=stack.pop()
            if not self.probe(prefix,bits):continue
            if bits==96:
                uid=prefix.to_bytes(12,'big');self.select(uid);found.append(self.info())
                if len(found)>maximum:raise RuntimeError('Discovery limit exceeded')
            else:
                stack.append((prefix|(1<<(95-bits)),bits+1));stack.append((prefix,bits+1))
        return found
    def select(self, uid):
        if isinstance(uid,str):uid=bytes.fromhex(uid)
        if len(uid)!=12:raise ValueError('UID must contain exactly 24 hex digits')
        self._prefix(uid,force=True);self.request(PROBE,96,expect=1)
        # Full UID readback detects stale/missed prefix frames before any mutation.
        actual=b''.join(self.request(INFO,n).to_bytes(4,'little') for n in (6,7,8))
        if actual!=uid:raise RuntimeError('Selected UID readback differs; no change made')
        self.uid=uid
    def info(self):
        flags=self.request(INFO,0);cfg=self.request(INFO,1);version=self.request(INFO,2)
        if flags&255!=1 or flags>>24!=7:raise RuntimeError('Unsupported service/hardware version')
        word=self.request(INFO,9)
        rail_mv=self.request(INFO,10) if not flags&256 else 0
        rail_state=self.request(INFO,11) if not flags&256 else 0
        return dict(rail12_mV=rail_mv&65535,rail5_mV=rail_mv>>16,rail_enabled=rail_state&3,rail_good=(rail_state>>8)&3,rail_latched=(rail_state>>16)&3,rail_pending=(rail_state>>24)&3,input_config=word, **unpack_settings(word), uid=self.uid.hex(),mode='bootloader' if flags&256 else 'application',
                    configured=bool(flags&512),boot_protected=bool(flags&1024),
                    device_id=cfg&255,invert=(cfg>>8)&255,debounce=(cfg>>16)&255,
                    status_period=(cfg>>24)&255,version=f'{version>>16}.{(version>>8)&255}.{version&255}')
    def power_reset(self, uid, rail='both'):
        mask={'12v':1,'5v':2,'both':3}[rail]
        self.select(uid)
        if self.info()['mode']!='application':raise ValueError('Power reset requires the application')
        self.request(POWER,mask,expect=mask)
        time.sleep(.4)
        return self.info()
    def reconnect(self, uid, *, mode=None):
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            try:
                self.open();self.select(uid);info=self.info()
                if mode is None or info['mode']==mode:return info
            except TimeoutError:pass
            time.sleep(.1)
        raise TimeoutError('Device did not return in the expected mode')
    def configure(self, uid, device_id, invert, debounce, modes=None, active=None):
        if not 0<=device_id<=63 or not 0<=invert<=7 or not 1<=debounce<=100:raise ValueError('ID 0..63, invert 0..7, debounce 1..100 required')
        if active is not None and modes is None:raise ValueError('Active states require modes')
        word=pack_settings(modes,active) if modes is not None else None
        uid=bytes.fromhex(uid) if isinstance(uid,str) else uid
        inventory=self.discover()
        if any(x['configured'] and x['device_id']==device_id and x['uid']!=uid.hex() for x in inventory):
            raise ValueError('Requested CAN ID is occupied by another responding board')
        self.select(uid)
        if word is None:word=self.request(INFO,9)
        self.request(INPUTS,word,expect=word)
        value=device_id|(invert<<8)|(debounce<<16)
        # Read back after reset even if the acknowledgement was lost.
        try:self.request(SAVE,value,expect=value)
        except TimeoutError:pass
        time.sleep(.8);info=self.reconnect(uid)
        if (info['device_id'],info['invert'],info['debounce'])!=(device_id,invert,debounce) or info['input_config']!=word:
            raise RuntimeError('Persistent configuration readback failed')
        return info
    def update(self, uid, raw, progress=lambda p:None):
        data,crc,version=unpack(raw)  # Reject before entering bootloader or erasing anything.
        uid=bytes.fromhex(uid) if isinstance(uid,str) else uid
        self.select(uid);info=self.info()
        if not info['boot_protected']:raise RuntimeError(ERRORS[5])
        if info['mode']!='bootloader':
            try:self.request(BOOT)
            except TimeoutError:pass
            time.sleep(.25);info=self.reconnect(uid,mode='bootloader')
        if self.request(INFO,4)<len(data):raise ValueError('Image exceeds device capacity')
        self.request(SIZE,len(data),expect=len(data));self.request(CRC,crc,expect=crc)
        self.request(BEGIN,TAG,expect=0)
        for offset in range(0,len(data),4):
            self.request(OFFSET,offset,expect=offset)
            self.request(DATA,int.from_bytes(data[offset:offset+4],'little'),expect=offset+4)
            progress((offset+4)/len(data))
        self.request(FINISH,expect=crc)
        if self.request(INFO,5)!=1:raise RuntimeError('Device image verification failed')
        try:self.request(RUN)
        except TimeoutError:pass
        time.sleep(.8);info=self.reconnect(uid,mode='application')
        expected=f'{version>>16}.{(version>>8)&255}.{version&255}'
        if info['version']!=expected:raise RuntimeError('Running firmware version does not match update')
        return info
    def close(self):
        try:
            if self.token:self._send(self._frame(CLOSE,0))
        except OSError:pass
        finally:self.transport.close()

def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bridge',help='TCP tunnel endpoint, e.g. localhost:5810')
    p.add_argument('--interface',default='socketcan');p.add_argument('--channel',default='can0')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('discover')
    for command in ('info','blink','configure','update','run','rate','power-reset'):
        q=sub.add_parser(command);q.add_argument('--uid',required=True)
        if command=='configure':
            q.add_argument('--device',type=int,required=True);q.add_argument('--invert',type=int,required=True);q.add_argument('--debounce',type=int,required=True)
        if command=='configure':
            q.add_argument('--modes',help='Three comma-separated modes: push-pull,npn,pnp,float,keeper')
            q.add_argument('--active',help='Three active states: high,low,driven,floating,not-high,not-low')
        if command=='update':q.add_argument('--file',type=Path,required=True)
        if command=='power-reset':q.add_argument('--rail',choices=('12v','5v','both'),default='both')
        if command=='rate':q.add_argument('--milliseconds',type=int,choices=(10,20,50),required=True)
    return p

def connect(args):return TcpBridge(args.bridge) if args.bridge else SocketCan(args.interface,args.channel)

def main():
    p=parser();args=p.parse_args();client=None
    try:
        client=Client(connect(args));client.open()
        if args.command=='discover':result=client.discover()
        elif args.command=='configure':result=client.configure(args.uid,args.device,args.invert,args.debounce,args.modes,args.active)
        elif args.command=='power-reset':result=client.power_reset(args.uid,args.rail)
        elif args.command=='update':result=client.update(args.uid,args.file.read_bytes())
        else:
            client.select(args.uid)
            if args.command=='blink':client.request(BLINK)
            if args.command=='run':client.request(RUN);time.sleep(.8);client.reconnect(bytes.fromhex(args.uid),mode='application')
            if args.command=='rate':client.request(RATE,args.milliseconds,expect=args.milliseconds)
            result=client.info()
        print(json.dumps(result,indent=2))
    except (OSError,RuntimeError,ValueError) as error:p.exit(1,f'Error: {error}\n')
    finally:
        if client:client.close()

if __name__=='__main__':main()
