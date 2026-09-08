"""Host uploader against the actual C service engine, with deterministic faults."""
import ctypes as C
import pathlib
import struct
import time
import unittest
import zlib
from can_service import Client, WIRE, INFO, SIZE, CRC, BEGIN, OFFSET, DATA, FINISH, SAVE, RATE, INPUTS, OPEN, MAGIC
from firmware_image import APP_BASE, APP_SIZE, HEADER, TAG, pack, unpack

LIB=pathlib.Path(__file__).resolve().parents[1]/'firmware/build/service_sim.so'

def image(byte=0xa5, length=1200):
    return struct.pack('<II',0x20001800,APP_BASE+193)+bytes([byte])*(length-8)

class Bus:
    def __init__(self, uids, boot=True):
        self.lib=C.CDLL(str(LIB));self.nodes=[];self.queue=[];self.drops={};self.duplicates=set();self.last=time.monotonic()
        self.lib.sim_new.argtypes=[C.c_char_p,C.c_int];self.lib.sim_new.restype=C.c_void_p
        for name in ('sim_free','sim_valid','sim_writes'):
            getattr(self.lib,name).argtypes=[C.c_void_p]
        self.lib.sim_exchange.argtypes=[C.c_void_p,C.c_char_p,C.c_void_p]
        self.lib.sim_tick.argtypes=[C.c_void_p,C.c_uint]
        self.lib.sim_seed.argtypes=[C.c_void_p,C.c_char_p,C.c_uint]
        self.lib.sim_protect.argtypes=[C.c_void_p,C.c_int]
        for uid in uids:
            node=self.lib.sim_new(uid,boot);self.nodes.append(node)
            self.lib.sim_seed(node,image(0x55),1200)
    def send(self, frame):
        now=time.monotonic();elapsed=int((now-self.last)*1000);self.last=now
        responses=[]
        for node in self.nodes:
            self.lib.sim_tick(node,elapsed);out=C.create_string_buffer(8)
            if self.lib.sim_exchange(node,frame,out):responses.append(out.raw)
            if frame[0] in self.duplicates:
                if self.lib.sim_exchange(node,frame,out):responses.append(out.raw)
        # CAN nodes replying simultaneously must transmit identical data.
        if responses:assert len(set(responses))==1, 'Conflicting discovery replies'
        if self.drops.get(frame[0],0):self.drops[frame[0]]-=1;return
        self.queue.extend(responses[:1])
    def recv(self, timeout):return self.queue.pop(0) if self.queue else None
    def close(self):
        for node in self.nodes:self.lib.sim_free(node)
        self.nodes=[]

@unittest.skipUnless(LIB.exists(),'run scripts/test_firmware.sh to build the C engine simulator')
class Service(unittest.TestCase):
    def setUp(self):
        self.uids=[bytes.fromhex(x) for x in ('000000000000000000000001','000000000000000000000002','ffffffffffffffffffffffff')]
        self.bus=Bus(self.uids);self.client=Client(self.bus,timeout=.001,probe_timeout=.001,spacing=0);self.client.open()
    def tearDown(self):self.client.close()
    def test_discovery_blank_duplicate_ids_and_targeting(self):
        found=self.client.discover();self.assertEqual({x['uid'] for x in found},{u.hex() for u in self.uids})
        self.assertTrue(all(not x['configured'] for x in found))
        for node in self.bus.nodes:
            # Each targeted change is followed by the real C reset callback.
            self.client.select(self.uids[self.bus.nodes.index(node)]);self.client.request(SAVE,17|(2<<16));self.bus.lib.sim_tick(node,60);self.client.open()
        self.assertEqual([x['device_id'] for x in self.client.discover()],[17]*3)
        with self.assertRaisesRegex(ValueError,'occupied'):self.client.configure(self.uids[0],17,0,2)
        info=self.client.configure(self.uids[1],18,3,7)
        self.assertEqual((info['device_id'],info['invert'],info['debounce']),(18,3,7))
    def test_update_retries_and_running_version(self):
        self.bus.drops={DATA:3,FINISH:2};self.bus.duplicates={DATA,OFFSET,BEGIN}
        info=self.client.update(self.uids[0],pack(image()))
        self.assertEqual(info['mode'],'application');self.assertEqual(info['version'],'0.6.0')
        self.assertTrue(all(self.bus.lib.sim_valid(n) for n in self.bus.nodes))
        self.assertEqual([self.bus.lib.sim_writes(n) for n in self.bus.nodes[1:]],[0,0])
    def test_bounds_protection_offsets_and_crc(self):
        c=self.client;c.select(self.uids[0]);node=self.bus.nodes[0]
        for bad in (0,188,APP_SIZE+4,193):
            with self.assertRaises(RuntimeError):c.request(SIZE,bad)
        c.request(SIZE,1200);c.request(CRC,0)
        self.bus.lib.sim_protect(node,0)
        with self.assertRaisesRegex(RuntimeError,'protected'):c.request(BEGIN,TAG)
        self.assertEqual(self.bus.lib.sim_writes(node),0)
        self.bus.lib.sim_protect(node,1);c.request(BEGIN,TAG)
        with self.assertRaises(RuntimeError):c.request(OFFSET,4)
        c.request(OFFSET,0);c.request(DATA,int.from_bytes(image()[:4],'little'))
        with self.assertRaises(RuntimeError):c.request(DATA,0)
        with self.assertRaises(RuntimeError):c.request(FINISH)
        self.assertFalse(self.bus.lib.sim_valid(node))
        # Upload all data with incorrect expected CRC; commit must remain invalid.
        for off in range(4,1200,4):c.request(OFFSET,off);c.request(DATA,int.from_bytes(image()[off:off+4],'little'))
        with self.assertRaisesRegex(RuntimeError,'verification'):c.request(FINISH)
        self.assertFalse(self.bus.lib.sim_valid(node))
    def test_stale_session_and_expiry(self):
        c=self.client;c.select(self.uids[0]);old=c.token;c.open()
        self.bus.send(WIRE.pack(SAVE,1,old,7|(2<<16)));self.assertIsNone(self.bus.recv(0))
        c.select(self.uids[0]);c.request(RATE,50);self.assertEqual(c.info()['status_period'],50)
        self.bus.lib.sim_tick(self.bus.nodes[0],5001)
        with self.assertRaises(TimeoutError):c.request(INFO)
        c.open();c.select(self.uids[0]);self.assertEqual(c.info()['device_id'],255)
    def test_input_settings_persist_and_stage_isolation(self):
        from input_settings import pack_settings
        modes=['npn','pnp','float'];word=pack_settings(modes)
        info=self.client.configure(self.uids[0],20,0,3,modes)
        self.assertEqual(info['input_config'],word)
        self.assertEqual(info['active'],['low','high','driven'])
        self.assertEqual(self.client.configure(self.uids[0],21,1,4)['input_config'],word)
        self.client.select(self.uids[0]);self.client.request(INPUTS,0)
        self.assertEqual(self.client.info()['input_config'],word)
        self.client.select(self.uids[1]);self.client.request(SAVE,22|(2<<16))
        self.bus.lib.sim_tick(self.bus.nodes[1],60);self.client.open();self.client.select(self.uids[1])
        self.assertEqual(self.client.info()['input_config'],0)
        for bad in (5,7,6<<9,1<<18,0xffffffff):
            with self.assertRaises(RuntimeError):self.client.request(INPUTS,bad)

    def test_wrong_file_rejected_without_writes(self):
        raw=bytearray(pack(image()));raw[-1]^=1
        with self.assertRaises(ValueError):self.client.update(self.uids[0],raw)
        self.assertEqual(sum(self.bus.lib.sim_writes(n) for n in self.bus.nodes),0)

class Images(unittest.TestCase):
    def test_format_crc_vectors_and_bounds(self):
        raw=pack(image());self.assertEqual(unpack(raw)[0],image())
        for i in (0,8,12,16,20,24,len(raw)-1):
            bad=bytearray(raw);bad[i]^=1
            with self.assertRaises(ValueError):unpack(bad)
        for data in (b'',bytes(1200),image(length=APP_SIZE+4)):
            with self.assertRaises(ValueError):pack(data)
        self.assertEqual(len(unpack(pack(image(length=APP_SIZE)))[0]),APP_SIZE)

if __name__=='__main__':unittest.main()
