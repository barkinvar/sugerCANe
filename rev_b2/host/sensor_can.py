#!/usr/bin/env python3
"""Configure through 3.3 V UART, or passively monitor the original CAN protocol.

Dependencies: pyserial for UART, python-can for CAN. No dependency is needed for codecs/tests.
"""
from __future__ import annotations
import argparse
import json
import struct
import time

VERSION = 1
BASE_ID = (10 << 24) | (8 << 16)
STATUS, COUNTS12, COUNTS34, DIAGNOSTIC, IDENTITY = 0x100, 0x101, 0x102, 0x110, 0x111
CONFIGURE, CLEAR_FAULTS = 0x200, 0x201


def bounded(value: int, low: int, high: int, name: str) -> int:
    if not low <= value <= high:
        raise ValueError(f"{name} must be {low}..{high}")
    return value


def can_id(device: int, api: int) -> int:
    return BASE_ID | (bounded(api, 0, 1023, "API") << 6) | bounded(device, 0, 63, "device ID")


def configuration(invert: int, debounce: int, rails: int) -> bytes:
    return struct.pack("<BBBBHBB", 0x53, 0x43, VERSION,
                       bounded(invert, 0, 7, "invert"), bounded(debounce, 1, 100, "debounce"),
                       bounded(rails, 0, 3, "rails"), 0)


def clear_faults(mask: int) -> bytes:
    return bytes((0x53, 0x43, VERSION, bounded(mask, 1, 3, "fault mask"), 0, 0, 0, 0))


def decode(api: int, data: bytes) -> dict:
    if len(data) != 8:
        raise ValueError("expected eight bytes")
    if api in (STATUS, IDENTITY) and data[0] != VERSION:
        raise ValueError("unsupported protocol version")
    if api == STATUS:
        if (data[2] | data[3]) >= 16 or (data[4] | data[5]) >= 4 or data[6] >= 8 or data[7] >= 16:
            raise ValueError("reserved status bits")
        return dict(kind="status", sequence=data[1], inputs=data[2], raw_inputs=data[3],
                    enabled_rails=data[4], latched_faults=data[5], configured=bool(data[6] & 1),
                    clock_ok=bool(data[6] & 2), adc_ok=bool(data[6] & 4), reset_flags=data[7])
    if api in (COUNTS12, COUNTS34):
        a, b = struct.unpack("<II", data)
        return dict(kind="counts12" if api == COUNTS12 else "counts34", first=a, second=b)
    if api == DIAGNOSTIC:
        bat, v5, drops, tec, rec = struct.unpack("<HHHBB", data)
        return dict(kind="diagnostic", sensor_battery_mV=bat, sensor5_mV=v5,
                    transmit_queue_drops=drops, transmit_errors=tec, receive_errors=rec)
    if api == IDENTITY:
        bounded(data[5], 0, 63, "device ID")
        bounded(data[6], 1, 100, "debounce")
        bounded(data[7], 0, 15, "invert")
        return dict(kind="identity", firmware=".".join(map(str, data[1:4])), hardware=data[4],
                    device_id=data[5], debounce_ms=data[6], invert=data[7])
    raise ValueError(f"unknown telemetry API 0x{api:03x}")


def parse_info(line: str) -> dict[str, str]:
    if not line.startswith("SC v"):
        raise ValueError("not an INFO response")
    return dict(token.split("=", 1) for token in line.split() if "=" in token)


def serial_exchange(port, command: str, wait_seconds: float = 2.0) -> list[str]:
    port.reset_input_buffer()
    port.write((command + "\r\n").encode("ascii"))
    port.flush()
    deadline = time.monotonic() + wait_seconds
    result = []
    while time.monotonic() < deadline:
        line = port.readline().decode("ascii", errors="replace").strip()
        if line:
            result.append(line)
            if line.startswith("ERR"):
                raise RuntimeError(line)
            if command == "INFO" and line.startswith("SC v"):
                return result
            if command.startswith("CLEAR ") and line == "OK":
                return result
    if not result:
        raise RuntimeError("No UART response; check board power, 3.3 V TX/RX, and common ground")
    return result


def uart_action(args) -> None:
    import serial
    # This opens an ordinary UART only; no DTR/RTS reset wiring is required or recommended.
    with serial.Serial(args.port, baudrate=115200, timeout=0.1, write_timeout=1) as port:
        if args.action == "info":
            lines = serial_exchange(port, "INFO")
            print("\n".join(lines))
            return
        if args.action == "configure":
            can_id(args.device, 0)
            configuration(args.invert, args.debounce, args.rails)
            command = f"SET {args.device} {args.invert} {args.debounce} {args.rails}"
            print("\n".join(serial_exchange(port, command)))
            lines = serial_exchange(port, "INFO")
            infos = [parse_info(line) for line in lines if line.startswith("SC v")]
            expected = dict(configured="1", id=str(args.device), invert=str(args.invert),
                            debounce_ms=str(args.debounce), requested=str(args.rails))
            if not infos or any(infos[-1].get(k) != v for k, v in expected.items()):
                raise RuntimeError("Configuration readback did not match; inspect INFO before use")
            print("Verified persistent configuration:", json.dumps(infos[-1], sort_keys=True))
        elif args.action == "clear":
            clear_faults(args.mask)
            print("\n".join(serial_exchange(port, f"CLEAR {args.mask}")))
            print("\n".join(serial_exchange(port, "INFO")))


def monitor(args) -> None:
    import can
    can_id(args.device, 0)
    # Filters only this board's extended IDs. No transmit, configuration, or automatic clear.
    filters = [{"can_id": can_id(args.device, 0), "can_mask": 0x1FFF003F, "extended": True}]
    with can.Bus(interface=args.interface, channel=args.channel, can_filters=filters) as bus:
        deadline = time.monotonic() + args.seconds if args.seconds else float("inf")
        last_status = None
        stale_reported = False
        while time.monotonic() < deadline:
            msg = bus.recv(timeout=0.05)
            now = time.monotonic()
            if msg and msg.is_extended_id and not msg.is_remote_frame and not msg.is_error_frame:
                api = (msg.arbitration_id >> 6) & 1023
                if api in (STATUS, COUNTS12, COUNTS34, DIAGNOSTIC, IDENTITY):
                    try:
                        payload = decode(api, bytes(msg.data))
                        if api == STATUS:
                            last_status, stale_reported = now, False
                        print(json.dumps(dict(timestamp=msg.timestamp, **payload)), flush=True)
                    except ValueError as error:
                        print(json.dumps(dict(kind="invalid", error=str(error))), flush=True)
            if (last_status is None or now - last_status > 0.1) and not stale_reported:
                print(json.dumps(dict(kind="unavailable", reason="no valid status within 100 ms")), flush=True)
                stale_reported = True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("info", "configure", "clear"):
        p = sub.add_parser(name)
        p.add_argument("--port", required=True, help="3.3 V UART serial port, e.g. /dev/ttyUSB0")
        if name == "configure":
            p.add_argument("--device", type=int, required=True)
            p.add_argument("--invert", type=int, required=True, help="3-bit active-low channel mask (Rev B)")
            p.add_argument("--debounce", type=int, required=True, help="1..100 milliseconds")
            p.add_argument("--rails", type=int, required=True, help="0=off, 1=5 V, 2=battery, 3=both")
        if name == "clear":
            p.add_argument("--mask", type=int, required=True, help="1=5 V, 2=battery, 3=both")
    p = sub.add_parser("monitor")
    p.add_argument("--interface", default="socketcan")
    p.add_argument("--channel", default="can0")
    p.add_argument("--device", type=int, required=True)
    p.add_argument("--seconds", type=float, default=0, help="0 runs until interrupted")
    args = parser.parse_args()
    try:
        monitor(args) if args.action == "monitor" else uart_action(args)
    except (ValueError, RuntimeError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
