import struct
import unittest
import sensor_can as sc


class LiteProtocolTest(unittest.TestCase):
    def test_version_and_reserved_fields(self):
        valid = bytes.fromhex('02fe0502031f0701')
        self.assertEqual(sc.decode(sc.STATUS, valid)['inputs'], 5)
        for field, choices in {0:[0,1,3],2:[8,255],3:[8],4:[0,4],5:[0,32],6:[16],7:[16]}.items():
            for value in choices:
                bad=bytearray(valid);bad[field]=value
                with self.assertRaises(ValueError):sc.decode(sc.STATUS,bad)
        for n in (0,7,9):
            with self.assertRaises(ValueError):sc.decode(sc.STATUS,bytes(n))
        with self.assertRaises(ValueError):sc.decode(0x100,valid)

    def test_three_channels_and_unsigned_counters(self):
        self.assertEqual(sc.decode(sc.COUNTS12,struct.pack('<II',0xffffffff,0x80000000))['first'],4294967295)
        self.assertEqual(sc.decode(sc.COUNTS3,struct.pack('<II',0xffffffff,0))['count'],4294967295)
        with self.assertRaises(ValueError):sc.decode(sc.COUNTS3,struct.pack('<II',1,1))
        d=sc.decode(sc.DIAGNOSTIC,bytes.fromhex('ffffffff807f0703'))
        self.assertEqual(d['transmit_queue_drops'],4294967295)
        self.assertTrue(d['bus_off'])
        with self.assertRaises(ValueError):sc.decode(sc.DIAGNOSTIC,bytes.fromhex('0000000000000800'))

    def test_commands_and_identity(self):
        self.assertEqual(sc.configuration(7,100).hex(),'5343020764000000')
        self.assertEqual(sc.resume().hex(),'5343020000000000')
        for inv,db in ((8,1),(-1,1),(0,0),(0,101)):
            with self.assertRaises(ValueError):sc.configuration(inv,db)
        self.assertEqual(sc.decode(sc.IDENTITY,bytes.fromhex('0200030003140207'))['device_id'],20)
        for h in ('0100030003140207','0200030002140207','0200030003400207','0200030003140208'):
            with self.assertRaises(ValueError):sc.decode(sc.IDENTITY,bytes.fromhex(h))
        for device in range(64):
            self.assertEqual(sc.can_id(device,sc.STATUS),0x0a084800|device)
        for device in (-1,64):
            with self.assertRaises(ValueError):sc.can_id(device,sc.STATUS)

    def test_uart_readback(self):
        self.assertEqual(sc.parse_info('SC Lite v0.3.0 proto=2 configured=1 id=20')['id'],'20')
        with self.assertRaises(ValueError):sc.parse_info('SC v0.1.0 configured=1')
        class Port:
            def reset_input_buffer(self):pass
            def write(self,data):self.command=data
            def flush(self):pass
            def readline(self):return b'OK\r\n'
        p=Port()
        self.assertEqual(sc.serial_exchange(p,'RESUME'),['OK'])
        self.assertEqual(p.command,b'RESUME\r\n')


if __name__=='__main__':unittest.main()
