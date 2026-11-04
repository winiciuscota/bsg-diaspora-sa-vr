#!/usr/bin/env python3
"""Wavefront OBJ -> FreeSpace POF (version 2117, one detail level, one textured material, box-projected UVs).

usage: mesh2pof.py in.obj out.pof --texture NAME [--length METERS] [--tile METERS] [--hard DEGREES]

Written for static props (wrecks, derelicts, debris): the polygons are one flat BSP list (defpoints, tmappolys, bound box,
eof), no sub-objects, turrets or docking points. Vertex winding and normals follow the retail Diaspora models (the
polygon normal is cross(v1 - v0, v2 - v0)). The mesh is centred on its bounding box and scaled so its longest side is
--length metres. `mesh2pof.py --check file.pof` lists the chunks and the vertex / polygon counts of any POF.
"""
import argparse, math, struct, sys
import numpy as np


def read_obj(path):
    v, f = [], []
    for line in open(path, errors="replace"):
        if line.startswith("v "):
            v.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) for t in line.split()[1:]]
            idx = [i - 1 if i > 0 else len(v) + i for i in idx]
            for k in range(1, len(idx) - 1):
                f.append([idx[0], idx[k], idx[k + 1]])
    return np.array(v, dtype=np.float64), np.array(f, dtype=np.int64)


def weld(v, f, eps=1e-6):
    key = np.round(v / eps).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    v2, f2 = v[first], inv[f]
    keep = (f2[:, 0] != f2[:, 1]) & (f2[:, 1] != f2[:, 2]) & (f2[:, 0] != f2[:, 2])
    return v2, f2[keep]


def build(v, f, length, tile, hard_deg):
    v = v - (v.min(0) + v.max(0)) / 2
    scale = length / max(float((v.max(0) - v.min(0)).max()), 1e-9)
    v = v * scale
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    fn = np.cross(b - a, c - a)
    area = np.linalg.norm(fn, axis=1)
    ok = area > 1e-9
    f, fn, area = f[ok], fn[ok], area[ok]
    fnu = fn / area[:, None]
    vn = np.zeros_like(v)
    for k in range(3):
        np.add.at(vn, f[:, k], fn)
    ln = np.linalg.norm(vn, axis=1)
    vn = vn / np.where(ln > 0, ln, 1)[:, None]
    cos_hard = math.cos(math.radians(hard_deg))

    # output vertices: shared where the corner normal agrees with the vertex normal, split otherwise
    out_v, out_n, index, corners = [], [], {}, []
    for fi in range(len(f)):
        tri = []
        for k in range(3):
            vi = int(f[fi, k])
            if float(np.dot(fnu[fi], vn[vi])) >= cos_hard:
                key = (vi, -1)
                n = vn[vi]
            else:
                key = (vi, fi)
                n = fnu[fi]
            if key not in index:
                index[key] = len(out_v)
                out_v.append(v[vi])
                out_n.append(n)
            tri.append(index[key])
        corners.append(tri)
    out_v, out_n = np.array(out_v), np.array(out_n)
    if len(out_v) > 65000:
        raise SystemExit("too many vertices (%d): decimate the mesh first" % len(out_v))

    # box-projected UVs: the dominant axis of the face normal picks the plane
    polys = []
    for fi, tri in enumerate(corners):
        n = np.abs(fnu[fi])
        ax = int(np.argmax(n))
        u_ax, v_ax = [(1, 2), (0, 2), (0, 1)][ax]
        uvs = [(out_v[i][u_ax] / tile, out_v[i][v_ax] / tile) for i in tri]
        polys.append((fnu[fi], tri, uvs))
    return out_v, out_n, polys


def string(s):
    b = s.encode("latin1")
    return struct.pack("<i", len(b)) + b


def chunk(cid, body):
    return cid + struct.pack("<i", len(body)) + body


def make_pof(out_v, out_n, polys, texture, mass=None):
    mins, maxs = out_v.min(0), out_v.max(0)
    rad = float(np.linalg.norm(out_v, axis=1).max())
    nv = len(out_v)

    # BSP data: DEFPOINTS (1 normal per vertex), TMAPPOLYs (3), BOUNDBOX (5), EOF
    head = struct.pack("<iiiii", 1, 0, nv, nv, 20 + nv)
    pts = b"".join(struct.pack("<3f", *out_v[i]) + struct.pack("<3f", *out_n[i]) for i in range(nv))
    defpoints = bytearray(head + bytes([1]) * nv + pts)
    struct.pack_into("<i", defpoints, 4, len(defpoints))
    bsp = bytes(defpoints)
    for n, tri, uvs in polys:
        pv = out_v[tri]
        ctr = pv.mean(0)
        prad = float(np.linalg.norm(pv - ctr, axis=1).max())
        body = struct.pack("<3f3ffii", *n, *ctr, prad, 3, 0)
        for i, (u, w) in zip(tri, uvs):
            body += struct.pack("<hhff", i, i, u, -w)
        bsp += struct.pack("<ii", 3, 8 + len(body)) + body
    bsp += struct.pack("<ii6f", 5, 32, *mins, *maxs)
    bsp += struct.pack("<ii", 0, 0)

    mass = mass or max(1000.0, rad ** 3 * 0.4)
    inertia = 0.4 * mass * rad * rad
    hdr2 = struct.pack("<fii", rad, 0, 1) + struct.pack("<6f", *mins, *maxs)
    hdr2 += struct.pack("<ii", 1, 0) + struct.pack("<i", 0)           # one detail level (submodel 0), no debris
    hdr2 += struct.pack("<f3f9f", mass, 0.0, 0.0, 0.0, inertia, 0, 0, 0, inertia, 0, 0, 0, inertia)
    hdr2 += struct.pack("<ii", 0, 0)                                  # cross sections, lights
    obj = struct.pack("<ifi", 0, rad, -1) + struct.pack("<12f", 0, 0, 0, 0, 0, 0, *mins, *maxs)
    obj += string("detail0") + string("") + struct.pack("<iiii", -1, -1, 0, len(bsp)) + bsp
    pof = b"PSPO" + struct.pack("<i", 2117)
    pof += chunk(b"TXTR", struct.pack("<i", 1) + string(texture))
    pof += chunk(b"HDR2", hdr2) + chunk(b"OBJ2", obj)
    pof += chunk(b"PINF", b"mesh2pof.py (Diaspora VR port)\0")
    return pof


def check(path):
    d = open(path, "rb").read()
    print(d[:4], "version", struct.unpack_from("<i", d, 4)[0])
    p, polys, verts = 8, 0, 0
    while p < len(d):
        cid, ln = d[p:p + 4], struct.unpack_from("<i", d, p + 4)[0]
        body = d[p + 8:p + 8 + ln]
        print(cid, ln)
        if cid == b"OBJ2":
            q = 12 + 48
            q += 4 + struct.unpack_from("<i", body, q)[0]
            q += 4 + struct.unpack_from("<i", body, q)[0]
            q += 8
            nch, bsz = struct.unpack_from("<ii", body, q)
            b, r = body[q + 8:q + 8 + bsz], 0
            while r + 8 <= len(b):
                t, s = struct.unpack_from("<ii", b, r)
                if t == 3:
                    polys += 1
                elif t == 1:
                    verts += struct.unpack_from("<i", b, r + 8)[0]
                if s <= 0 and t != 0:
                    break
                r += max(s, 8)
        p += 8 + ln
    print("vertices", verts, "polygons", polys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--texture", default="wreck_hull")
    ap.add_argument("--length", type=float, default=100.0)
    ap.add_argument("--tile", type=float, default=20.0, help="metres per texture repeat")
    ap.add_argument("--hard", type=float, default=50.0, help="edges sharper than this get flat normals")
    ap.add_argument("--check", metavar="POF")
    a = ap.parse_args()
    if a.check:
        return check(a.check)
    v, f = weld(*read_obj(a.src))
    out_v, out_n, polys = build(v, f, a.length, a.tile, a.hard)
    open(a.dst, "wb").write(make_pof(out_v, out_n, polys, a.texture))
    print("%s: %d vertices, %d polygons, %.0f m" % (a.dst, len(out_v), len(polys), a.length))


if __name__ == "__main__":
    main()
