#!/usr/bin/env python3
"""Minimal VP archive lister/extractor.  usage: vpx.py list|extract FILE.vp [outdir] [substring-filter]"""
import os, struct, sys

def entries(vp):
    with open(vp, "rb") as f:
        mag, ver, off, n = struct.unpack("<4sIII", f.read(16))
        assert mag == b"VPVP", "not a VP file"
        f.seek(off)
        path = []
        for _ in range(n):
            o, s, name, ts = struct.unpack("<II32sI", f.read(44))
            name = name.split(b"\0")[0].decode("latin1")
            if s == 0:
                if name == "..":
                    path and path.pop()
                else:
                    path.append(name)
            else:
                yield "/".join(path + [name]), o, s

def main():
    cmd, vp = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    flt = sys.argv[4].lower() if len(sys.argv) > 4 else ""
    with open(vp, "rb") as f:
        for p, o, s in entries(vp):
            if flt and flt not in p.lower():
                continue
            if cmd == "list":
                print(f"{s:>10} {p}")
            else:
                dst = os.path.join(out, p)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                f.seek(o)
                with open(dst, "wb") as g:
                    g.write(f.read(s))

main()
