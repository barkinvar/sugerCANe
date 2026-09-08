"""Protocol and real OS pseudo-terminal tests, without physical hardware."""
import os
from pathlib import Path
import random
import select
import struct
import subprocess
import sys
import threading
import unittest
import sensor_can as sc


class ProtocolTests(unittest.TestCase):
    def test_ids(self):
        for device in range(64):
            for api in range(1024):
                value = sc.can_id(device, api)
                self.assertEqual(value & 63, device)
                self.assertEqual((value >> 6) & 1023, api)
                self.assertEqual(value & 0x1FFF0000, 0x0A080000)

    def test_golden_vectors(self):
        value = sc.decode(sc.STATUS, bytes.fromhex("01fe0a0501020705"))
        self.assertEqual((value["sequence"], value["inputs"], value["raw_inputs"]), (254, 10, 5))
        self.assertEqual((value["enabled_rails"], value["latched_faults"], value["reset_flags"]), (1, 2, 5))
        self.assertTrue(value["configured"] and value["clock_ok"] and value["adc_ok"])
        value = sc.decode(sc.COUNTS12, bytes.fromhex("ffffffff00000080"))
        self.assertEqual((value["first"], value["second"]), (4294967295, 2147483648))
        value = sc.decode(sc.DIAGNOSTIC, bytes.fromhex("e02e8813ffff807f"))
        self.assertEqual((value["sensor_battery_mV"], value["sensor5_mV"]), (12000, 5000))
        self.assertEqual(sc.configuration(5, 100, 3).hex(), "5343010564000300")
        self.assertEqual(sc.clear_faults(3).hex(), "5343010300000000")

    def test_random_unsigned(self):
        rng = random.Random(20260907)
        for _ in range(10000):
            a, b = rng.getrandbits(32), rng.getrandbits(32)
            value = sc.decode(sc.COUNTS34, struct.pack("<II", a, b))
            self.assertEqual((value["first"], value["second"]), (a, b))

    def test_invalid(self):
        for field, maximum in ((0, 1), (2, 15), (3, 15), (4, 3), (5, 3), (6, 7), (7, 15)):
            for value in range(256):
                data = bytearray.fromhex("0100000000000701")
                data[field] = value
                if value > maximum or (field == 0 and value != 1):
                    with self.assertRaises(ValueError):
                        sc.decode(sc.STATUS, data)
        for args in ((-1, 1, 0), (8, 1, 0), (0, 0, 0), (0, 101, 0), (0, 1, 4)):
            with self.assertRaises(ValueError):
                sc.configuration(*args)
        for length in range(16):
            if length != 8:
                with self.assertRaises(ValueError):
                    sc.decode(sc.COUNTS12, bytes(length))

    def test_uart_cli_real_pty(self):
        """Run the actual CLI against a simulated ASCII board over Linux PTY."""
        master, slave = os.openpty()
        stop = threading.Event()
        commands = []

        def board():
            pending = b""
            while not stop.is_set():
                if not select.select([master], [], [], 0.1)[0]:
                    continue
                pending += os.read(master, 256)
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    commands.append(line)
                    if line == b"SET 20 1 2 2":
                        os.write(master, b"OK: saved; resetting\r\n")
                    elif line == b"INFO":
                        os.write(master, b"SC v0.1.0 proto=1 configured=1 id=20 invert=1 debounce_ms=2 rails=2 requested=2 faults=0 clock_ok=1 can_ok=1 adc_ok=1 sensorbat_mV=12000 sensor5_mV=0\r\n")
                    else:
                        os.write(master, b"ERR: unexpected command\r\n")

        worker = threading.Thread(target=board)
        worker.start()
        try:
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("sensor_can.py")),
                "configure", "--port", os.ttyname(slave), "--device", "20", "--invert", "1",
                "--debounce", "2", "--rails", "2"], capture_output=True, text=True, timeout=8)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Verified persistent configuration", result.stdout)
            self.assertEqual(commands, [b"SET 20 1 2 2", b"INFO"])
        finally:
            stop.set()
            worker.join(timeout=1)
            os.close(master)
            os.close(slave)


if __name__ == "__main__":
    unittest.main(verbosity=2)
