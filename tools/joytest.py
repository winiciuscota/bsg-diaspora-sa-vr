#!/usr/bin/env python3
"""Print joystick axis / button / hat events of a /dev/input/jsN device (joydev API) with the indexes FSO uses.
Usage: python3 -I tools/joytest.py [/dev/input/js0]   (run it where the stick is attached, e.g. on the Wolf host)
Press the physical controls and note the numbers: buttons are 'Button N' in the FSO Controls screen,
axes follow SDL order (0 X, 1 Y, 2 Z, 3 RX, 4 RY, 5 RZ, 6 THROTTLE, ...)."""
import struct, sys
dev = sys.argv[1] if len(sys.argv) > 1 else "/dev/input/js0"
with open(dev, "rb") as f:
    while True:
        data = f.read(8)
        if len(data) < 8:
            break
        _t, value, kind, number = struct.unpack("IhBB", data)
        if kind & 0x80:     # initial state
            continue
        if kind & 1:
            print(f"button {number:3d} {'down' if value else 'up'}", flush=True)
        elif kind & 2 and abs(value) > 3000:
            print(f"axis   {number:3d} {value:6d}", flush=True)
