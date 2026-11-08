#!/usr/bin/env python3
"""Textured glTF binary (.glb, one mesh, TEXCOORD_0, base colour image) -> FreeSpace POF (version 2117).

usage: glb2pof.py in.glb out.pof --texture NAME [--length M] [--axes long,up,side] [--flip-front] [--hard DEG] [--image out.jpg]

Unlike mesh2pof.py this keeps the mesh's own UVs (so the generated texture stays valid) and the full polygon count: the
polygons are cut into submodels of 20 000 triangles (a POF vertex index is 16 bit), all children of an empty root, so the
model renders and collides as one object. glTF is right handed, FreeSpace left handed: the forward axis is negated and the
winding reversed so the ship is not mirrored. --axes tells which glTF axis (x, y, z with optional leading -) is the ship's
length, height and width (default x,z,y: long along x, up along z, which is what the assetgen/Hunyuan exports look like).
"""
import argparse, json, struct
import numpy as np
from mesh2pof import string, chunk


def read_glb(path):
    d = open(path, "rb").read()
    cl, _ = struct.unpack_from("<I4s", d, 12)
    j = json.loads(d[20:20 + cl])
    off = 20 + cl
    bl, _ = struct.unpack_from("<I4s", d, off)
    binary = d[off + 8:off + 8 + bl]

    def acc(i):
        a = j["accessors"][i]
        bv = j["bufferViews"][a["bufferView"]]
        dt = {5126: "<f4", 5125: "<u4", 5123: "<u2", 5121: "u1"}[a["componentType"]]
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[a["type"]]
        o = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(binary, dtype=dt, count=a["count"] * n, offset=o).reshape(-1, n).astype(np.float64 if dt == "<f4" else np.int64)

    prim = j["meshes"][0]["primitives"][0]
    pos = acc(prim["attributes"]["POSITION"])
    uv = acc(prim["attributes"]["TEXCOORD_0"])
    idx = acc(prim["indices"]).reshape(-1, 3)
    mat = j["materials"][prim.get("material", 0)]["pbrMetallicRoughness"]
    img = j["images"][j["textures"][mat["baseColorTexture"]["index"]]["source"]]
    bv = j["bufferViews"][img["bufferView"]]
    image = binary[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
    return pos, uv, idx, image, img.get("mimeType", "image/jpeg")


def axis(spec):
    sign = -1.0 if spec.startswith("-") else 1.0
    return "xyz".index(spec.lstrip("-")), sign


def build_lod(a, pos, uv, idx, first_sub, lod_name, xform):
    """Submodels of one detail level (first one is the level's root, the rest are its children): (chunks, count, mins, maxs, radius)."""
    (il, sl), (iu, su), (iw, sw) = [axis(s) for s in a.axes.split(",")]
    # glTF -> ship space: x = width, y = up, z = forward (length); forward negated + winding reversed (handedness change)
    p = np.stack([pos[:, iw] * sw, pos[:, iu] * su, -pos[:, il] * sl * (-1.0 if a.flip_front else 1.0)], 1)
    if not xform:                                 # the first (most detailed) mesh sets the placement, the LODs follow it
        xform["center"] = (p.min(0) + p.max(0)) / 2
        xform["scale"] = a.length / float((p.max(0) - p.min(0)).max())
    p = (p - xform["center"]) * xform["scale"]
    f = idx[:, [0, 2, 1]]                         # reversed winding

    a0, b0, c0 = p[f[:, 0]], p[f[:, 1]], p[f[:, 2]]
    fn = np.cross(b0 - a0, c0 - a0)
    area = np.linalg.norm(fn, axis=1)
    keep = area > 1e-9
    f, fn, area = f[keep], fn[keep], area[keep]
    fnu = fn / area[:, None]
    vn = np.zeros_like(p)
    for k in range(3):
        np.add.at(vn, f[:, k], fn)
    ln = np.linalg.norm(vn, axis=1)
    vn /= np.where(ln > 0, ln, 1)[:, None]

    # corner arrays (F, 3): position index, normal, uv; split hard corners by giving them the face normal
    corner_n = vn[f]                                                   # (F,3,3)
    hard = np.einsum("fkc,fc->fk", corner_n, fnu) < np.cos(np.radians(a.hard))
    corner_n = np.where(hard[..., None], fnu[:, None, :], corner_n)
    corner_uv = uv[f]                                                  # (F,3,2)

    order = np.argsort((p[f].mean(1))[:, 2])                           # sweep along the length
    parts = [order[i:i + a.faces_per_part] for i in range(0, len(order), a.faces_per_part)]
    if a.max_parts:
        parts = parts[:a.max_parts]
    mins, maxs = p.min(0), p.max(0)
    rad = float(np.linalg.norm(p, axis=1).max())

    objs = []
    poly_dt = np.dtype([("id", "<i4"), ("size", "<i4"), ("n", "<3f4"), ("c", "<3f4"), ("r", "<f4"), ("nv", "<i4"), ("tm", "<i4"),
                        ("v", [("vi", "<i2"), ("ni", "<i2"), ("u", "<f4"), ("w", "<f4")], (3,))])
    for pi, sel in enumerate(parts, start=1):
        fi = f[sel]                                                    # (m,3) position indices
        uniq, inv = np.unique(np.concatenate([fi.reshape(-1)[:, None], (hard[sel].reshape(-1, 1)).astype(np.int64),
                                              (np.arange(len(sel) * 3) // 3 * hard[sel].reshape(-1))[:, None]], 1),
                              axis=0, return_inverse=True)
        inv = inv.reshape(-1)
        verts = p[uniq[:, 0]]
        # one normal per output vertex: the first corner that maps to it
        first = np.zeros(len(uniq), dtype=np.int64)
        first[inv[::-1]] = np.arange(len(inv))[::-1]
        norms = corner_n[sel].reshape(-1, 3)[first]
        if len(verts) > 65000:
            raise SystemExit("part %d has %d vertices: lower --faces-per-part" % (pi, len(verts)))
        m = len(sel)
        tri = inv.reshape(m, 3)
        polys = np.zeros(m, dtype=poly_dt)
        polys["id"], polys["size"], polys["nv"], polys["tm"] = 3, poly_dt.itemsize, 3, 0
        polys["n"] = fnu[sel]
        pv = verts[tri]
        polys["c"] = pv.mean(1)
        polys["r"] = np.linalg.norm(pv - pv.mean(1, keepdims=True), axis=2).max(1)
        polys["v"]["vi"], polys["v"]["ni"] = tri, tri
        polys["v"]["u"] = corner_uv[sel][..., 0]
        polys["v"]["w"] = corner_uv[sel][..., 1]
        head = bytearray(struct.pack("<iiiii", 1, 0, len(verts), len(verts), 20 + len(verts)) + bytes([1]) * len(verts))
        body = np.concatenate([verts, norms], 1).astype("<f4").tobytes()
        defpoints = bytes(head) + body
        defpoints = defpoints[:4] + struct.pack("<i", len(defpoints)) + defpoints[8:]
        vmin, vmax = verts.min(0), verts.max(0)
        # the engine's collision parser wants DEFPOINTS, then BOUNDBOX followed by the polygons of that leaf, then EOF
        bsp = defpoints + struct.pack("<ii6f", 5, 32, *vmin, *vmax) + polys.tobytes() + struct.pack("<ii", 0, 0)
        sub, parent, pname = (first_sub + pi - 1, -1, lod_name) if pi == 1 else (first_sub + pi - 1, first_sub, "%s_part%02d" % (lod_name, pi))
        o = struct.pack("<ifi", sub, float(np.linalg.norm(verts, axis=1).max()), parent) + struct.pack("<12f", 0, 0, 0, *((vmin + vmax) / 2), *vmin, *vmax)
        o += string(pname) + string("") + struct.pack("<iiii", -1, -1, 0, len(bsp)) + bsp
        objs.append(chunk(b"OBJ2", o))
        print("part %d: %d polygons, %d vertices" % (pi, m, len(verts)))
    return objs, len(parts), mins, maxs, rad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--texture", required=True)
    ap.add_argument("--length", type=float, default=900.0)
    ap.add_argument("--axes", default="auto", help="glTF axes of length,height,width, e.g. x,z,y; auto = z is up, the longer of x / y is the length")
    ap.add_argument("--flip-front", action="store_true")
    ap.add_argument("--hard", type=float, default=60.0)
    ap.add_argument("--image", help="write the base colour image here")
    ap.add_argument("--glow", help="json file with glow point banks: {\"banks\": [{\"texture\": name, \"points\": [[x,y,z,nx,ny,nz,radius], ...]}]}")
    ap.add_argument("--lods", help="comma separated GLBs with lower detail versions of the model (same orientation), written as detail levels 1, 2, ...")
    ap.add_argument("--faces-per-part", type=int, default=20000)
    ap.add_argument("--max-parts", type=int, default=0, help="debug: keep only the first N parts")
    ap.add_argument("--empty-root", action="store_true", help="debug: empty root submodel + all parts as children (the engine runs out of memory loading that layout)")
    a = ap.parse_args()
    a.root_geometry = not a.empty_root

    pos, uv, idx, image, mime = read_glb(a.src)
    if a.image:
        open(a.image, "wb").write(image)
    if a.axes == "auto":
        a.axes = "x,z,y" if np.ptp(pos[:, 0]) >= np.ptp(pos[:, 1]) else "y,z,x"
        print("axes:", a.axes)
    xform = {}
    objs, nparts, mins, maxs, rad = build_lod(a, pos, uv, idx, 0, "detail0", xform)
    firsts = [0]
    for k, path in enumerate([p for p in (a.lods or "").split(",") if p], start=1):
        lpos, luv, lidx, _, _ = read_glb(path)
        firsts.append(nparts)
        lobjs, lparts, _, _, _ = build_lod(a, lpos, luv, lidx, nparts, "detail%d" % k, xform)
        objs += lobjs
        nparts += lparts
    nsub = nparts + (0 if a.root_geometry else 1)

    root_bsp = struct.pack("<ii6f", 5, 32, *mins, *maxs) + struct.pack("<ii", 0, 0)
    root = struct.pack("<ifi", 0, rad, -1) + struct.pack("<12f", 0, 0, 0, 0, 0, 0, *mins, *maxs)
    root += string("detail0") + string("") + struct.pack("<iiii", -1, -1, 0, len(root_bsp)) + root_bsp
    mass = max(1000.0, rad ** 3 * 0.05)
    inertia = 0.4 * mass * rad * rad
    hdr2 = struct.pack("<fii", rad, 0, nsub) + struct.pack("<6f", *mins, *maxs) + struct.pack("<i", len(firsts)) + struct.pack("<%di" % len(firsts), *firsts) + struct.pack("<i", 0)
    hdr2 += struct.pack("<f3f9f", mass, 0.0, 0.0, 0.0, inertia, 0, 0, 0, inertia, 0, 0, 0, inertia) + struct.pack("<ii", 0, 0)
    pof = b"PSPO" + struct.pack("<i", 2117) + chunk(b"TXTR", struct.pack("<i", 1) + string(a.texture)) + chunk(b"HDR2", hdr2)
    if a.glow:
        banks = json.load(open(a.glow))["banks"]
        g = struct.pack("<i", len(banks))
        for b in banks:       # always on: disp_time, on_time, off_time = 0; parent submodel 0; LOD 0; type 0 (omni)
            g += struct.pack("<6i", 0, 0, 0, 0, 0, 0) + struct.pack("<i", len(b["points"])) + string("$glow_texture=" + b["texture"])
            for pt in b["points"]:
                g += struct.pack("<7f", *pt)
        glow_chunk = chunk(b"GLOW", g)
    else:
        glow_chunk = b""
    pof += glow_chunk
    pof += (b"" if a.root_geometry else chunk(b"OBJ2", root)) + b"".join(objs) + chunk(b"PINF", b"glb2pof.py (Diaspora VR port)\0")
    open(a.dst, "wb").write(pof)
    print("%s: %d submodels, %d bytes, %.0f m long, radius %.0f" % (a.dst, nsub, len(pof), (maxs - mins)[2], rad))


if __name__ == "__main__":
    main()
