#!/usr/bin/env python3
"""Software renderer for FreeSpace POF models (numpy + PIL, no GPU): textured, lit, with the glow point banks (engine lights)
drawn as additive sprites. For checking generated ships without starting the game.

usage: pofview.py model.pof out.png [--maps DIR ...] [--views rear,side,top,front,3q] [--size 960x480] [--light x,y,z]
Views are montaged into one PNG. Camera convention is the engine's: x right, y up, z forward (left handed, like D3D LookAt).
Textures are found by the names in the POF (.dds/.png/.jpg/.tga) in the --maps folders. Only the highest detail level and its
child submodels are drawn."""
import argparse, math, os, struct
import numpy as np
from PIL import Image, ImageFilter

# ------------------------------------------------------------------------------------------------------ POF reading
def read_pof(path):
    d = open(path, "rb").read()
    ver = struct.unpack_from("<i", d, 4)[0]
    pof = dict(version=ver, textures=[], subs={}, glow=[], detail0=0, rad=1.0)
    q = 8
    while q + 8 <= len(d):
        cid, ln = d[q:q + 4], struct.unpack_from("<i", d, q + 4)[0]
        b = d[q + 8:q + 8 + ln]
        q += 8 + ln
        if cid == b"TXTR":
            n, r = struct.unpack_from("<i", b, 0)[0], 4
            for _ in range(n):
                l = struct.unpack_from("<i", b, r)[0]; pof["textures"].append(b[r + 4:r + 4 + l].decode("latin1")); r += 4 + l
        elif cid == b"HDR2":
            pof["rad"] = struct.unpack_from("<f", b, 0)[0]
            nsub = struct.unpack_from("<i", b, 8)[0]
            r = 12 + 24
            nd = struct.unpack_from("<i", b, r)[0]
            pof["detail0"] = struct.unpack_from("<i", b, r + 4)[0] if nd else 0
        elif cid == b"OBJ2":
            sm = read_obj2(b, ver)
            pof["subs"][sm["id"]] = sm
        elif cid == b"GLOW":
            n, r = struct.unpack_from("<i", b, 0)[0], 4
            for _ in range(n):
                disp, on, off, par, lod, typ, npts = struct.unpack_from("<7i", b, r); r += 28
                l = struct.unpack_from("<i", b, r)[0]; props = b[r + 4:r + 4 + l].decode("latin1"); r += 4 + l
                pts = []
                for _ in range(npts):
                    pts.append(struct.unpack_from("<7f", b, r)); r += 28
                tex = props.split("$glow_texture=")[1].strip("\0 ") if "$glow_texture=" in props else None
                pof["glow"].append(dict(parent=par, lod=lod, tex=tex, pts=np.array(pts).reshape(-1, 7)))
    return pof


def read_obj2(b, ver):
    sid, rad, parent = struct.unpack_from("<ifi", b, 0)
    off = np.array(struct.unpack_from("<3f", b, 12))
    r = 12 + 48
    l = struct.unpack_from("<i", b, r)[0]; name = b[r + 4:r + 4 + l].decode("latin1"); r += 4 + l
    l = struct.unpack_from("<i", b, r)[0]; r += 4 + l
    r += 8 + (8 if ver >= 2301 else 0)
    nch, bsz = struct.unpack_from("<ii", b, r)
    bsp = b[r + 8:r + 8 + bsz]
    verts = norms = None
    tris = []   # (vi0,vi1,vi2, ni0,ni1,ni2, u0,v0,u1,v1,u2,v2, tmap, nx,ny,nz)
    p = 0
    while p + 8 <= len(bsp):
        t, sz = struct.unpack_from("<ii", bsp, p)
        if t == 0 and sz == 0:
            p += 8; continue
        if sz <= 0:
            break
        if t == 1:
            nv, nn, o = struct.unpack_from("<iii", bsp, p + 8)
            cnt = np.frombuffer(bsp, np.uint8, nv, p + 20)
            V, N, c = [], [], p + o
            for i in range(nv):
                V.append(struct.unpack_from("<3f", bsp, c)); c += 12
                N.append(struct.unpack_from("<3f", bsp, c) if cnt[i] else (0, 0, 0)); c += 12 * int(cnt[i])
            verts, norms = np.array(V), np.array(N)
        elif t == 3:
            n = struct.unpack_from("<3f", bsp, p + 8)
            nvt, tm = struct.unpack_from("<ii", bsp, p + 36)
            pv = [struct.unpack_from("<hhff", bsp, p + 44 + 12 * i) for i in range(nvt)]
            for k in range(1, nvt - 1):
                a, bb, cc = pv[0], pv[k], pv[k + 1]
                tris.append((a[0], bb[0], cc[0], a[1], bb[1], cc[1], a[2], a[3], bb[2], bb[3], cc[2], cc[3], tm, *n))
        p += sz
    return dict(id=sid, parent=parent, off=off, name=name, verts=verts, norms=norms, tris=np.array(tris, dtype=np.float64).reshape(-1, 16))


def collect(pof):
    """world-space triangle soup of detail level 0 and its children"""
    subs = pof["subs"]
    root = pof["detail0"]
    def world_off(i):
        o = np.zeros(3)
        while i >= 0 and i in subs:
            o = o + subs[i]["off"]; i = subs[i]["parent"]
        return o
    def under(i):
        while i >= 0 and i in subs:
            if i == root:
                return True
            i = subs[i]["parent"]
        return False
    P, N, UV, TM, FN = [], [], [], [], []
    for i, sm in subs.items():
        if not under(i) or sm["verts"] is None or not len(sm["tris"]):
            continue
        t = sm["tris"]
        vi = t[:, 0:3].astype(int); ni = t[:, 3:6].astype(int)
        o = world_off(i)
        P.append(sm["verts"][vi] + o)
        nn = sm["norms"][np.clip(ni, 0, len(sm["norms"]) - 1)] if sm["norms"] is not None else np.zeros((len(t), 3, 3))
        N.append(nn)
        UV.append(t[:, 6:12].reshape(-1, 3, 2)); TM.append(t[:, 12].astype(int)); FN.append(t[:, 13:16])
    return (np.concatenate(P), np.concatenate(N), np.concatenate(UV), np.concatenate(TM), np.concatenate(FN))


# ------------------------------------------------------------------------------------------------------ rendering
def find_texture(name, dirs):
    for d in dirs:
        for ext in (".dds", ".png", ".jpg", ".tga", ".DDS", ".PNG"):
            f = os.path.join(d, name + ext)
            if os.path.exists(f):
                return f
    return None


def load_tex(name, dirs, cap=2048):
    f = find_texture(name, dirs) if name else None
    if not f:
        return None
    im = Image.open(f).convert("RGB")
    if max(im.size) > cap:
        im = im.resize((cap, cap * im.height // im.width) if im.width >= im.height else (cap * im.width // im.height, cap), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255.0


def camera(center, radius, yaw, pitch, dist_f, W, H, fov=40.0):
    yaw, pitch = math.radians(yaw), math.radians(pitch)
    f = np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])   # from target to eye
    eye = center + f * radius * dist_f
    z = center - eye; z /= np.linalg.norm(z)
    x = np.cross([0, 1, 0], z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    focal = (W / 2) / math.tan(math.radians(fov) / 2)
    return eye, x, y, z, focal


def render(model, tex, glow_tex, view, W, H, light, bg_seed=1, ss=2):
    P, N, UV, TM, FN = model
    center = (P.reshape(-1, 3).min(0) + P.reshape(-1, 3).max(0)) / 2
    radius = float(np.linalg.norm(P.reshape(-1, 3) - center, axis=1).max())
    W2, H2 = W * ss, H * ss
    eye, ax, ay, az, focal = camera(center, radius, view[0], view[1], view[2], W2, H2)
    rel = P - eye
    cx, cy, cz = rel @ ax, rel @ ay, rel @ az
    z = cz                                                       # (F,3)
    ok = (z > 1.0).all(1)
    sx = cx / np.maximum(z, 1e-3) * focal + W2 / 2
    sy = H2 / 2 - cy / np.maximum(z, 1e-3) * focal
    # back-face cull with the stored polygon normal
    ctr = P.mean(1)
    facing = ((eye - ctr) * FN).sum(1) > 0
    ok &= facing
    ok &= (sx.max(1) > 0) & (sx.min(1) < W2) & (sy.max(1) > 0) & (sy.min(1) < H2)
    idx = np.nonzero(ok)[0]
    area = np.abs((sx[idx, 1] - sx[idx, 0]) * (sy[idx, 2] - sy[idx, 0]) - (sx[idx, 2] - sx[idx, 0]) * (sy[idx, 1] - sy[idx, 0])) / 2
    nsamp = np.clip(np.ceil(np.sqrt(area) * 1.2), 1, 14).astype(int)
    keys, depths, cols = [], [], []
    L = np.array(light, dtype=np.float64); L /= np.linalg.norm(L)
    for n in np.unique(nsamp):
        sel = idx[nsamp == n]
        g = [((i + 0.5) / n, (j + 0.5) / n) for i in range(n) for j in range(n)]
        g = [(u, v) if u + v <= 1 else (1 - u, 1 - v) for u, v in g]
        bary = np.array([(1 - u - v, u, v) for u, v in g])           # (K,3)
        for s in range(0, len(sel), 60000):
            ss_ = sel[s:s + 60000]
            w = 1.0 / z[ss_]                                          # (m,3) perspective weights
            bw = bary[None, :, :] * w[:, None, :]                      # (m,K,3)
            bw = bw / bw.sum(-1, keepdims=True)
            X = (bary[None] * sx[ss_][:, None, :]).sum(-1); Y = (bary[None] * sy[ss_][:, None, :]).sum(-1)
            Z = 1.0 / (bary[None] * w[:, None, :]).sum(-1)
            uv = (bw[..., None] * UV[ss_][:, None, :, :]).sum(2)       # (m,K,2)
            nm = (bw[..., None] * N[ss_][:, None, :, :]).sum(2)
            nl = np.linalg.norm(nm, axis=-1, keepdims=True)
            fn = FN[ss_][:, None, :]
            nm = np.where(nl > 1e-6, nm / np.maximum(nl, 1e-6), fn)
            lam = np.clip((nm * L).sum(-1), 0, 1)
            if tex is not None:
                th, tw = tex.shape[:2]
                tx = (np.mod(uv[..., 0], 1.0) * tw).astype(int) % tw
                ty = (np.mod(uv[..., 1], 1.0) * th).astype(int) % th
                albedo = tex[ty, tx]
            else:
                albedo = np.full(uv.shape[:2] + (3,), 0.55, np.float32)
            shade = 0.22 + 0.95 * lam
            col = albedo * shade[..., None]
            px = np.floor(X).astype(int); py = np.floor(Y).astype(int)
            m = (px >= 0) & (px < W2) & (py >= 0) & (py < H2)
            keys.append((py * W2 + px)[m]); depths.append(Z[m]); cols.append(col[m])
    img = np.zeros((H2, W2, 3), np.float32)
    zbuf = np.full(H2 * W2, np.inf, np.float32)
    if keys:
        k = np.concatenate(keys); dz = np.concatenate(depths).astype(np.float32); c = np.concatenate(cols)
        o = np.lexsort((dz, k)); k, dz, c = k[o], dz[o], c[o]
        first = np.r_[True, k[1:] != k[:-1]]
        k, dz, c = k[first], dz[first], c[first]
        zbuf[k] = dz
        img.reshape(-1, 3)[k] = c
        # fill single-pixel holes from the nearest covered neighbours
        cov = np.isfinite(zbuf).reshape(H2, W2)
        for _ in range(2):
            pad = np.pad(img, ((1, 1), (1, 1), (0, 0)))
            cpad = np.pad(cov, 1)
            acc = np.zeros_like(img); cnt = np.zeros((H2, W2), np.float32)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    acc += pad[1 + dy:1 + dy + H2, 1 + dx:1 + dx + W2] * cpad[1 + dy:1 + dy + H2, 1 + dx:1 + dx + W2][..., None]
                    cnt += cpad[1 + dy:1 + dy + H2, 1 + dx:1 + dx + W2]
            fill = (~cov) & (cnt >= 3)
            img[fill] = acc[fill] / cnt[fill][..., None]
            zb = zbuf.reshape(H2, W2); zb[fill] = np.inf * 0 + np.nanmean(dz)
            cov = cov | fill
    # background: dark space with a few stars
    rng = np.random.default_rng(bg_seed)
    bg = np.zeros((H2, W2, 3), np.float32) + np.array([0.012, 0.014, 0.022], np.float32)
    for _ in range(int(W2 * H2 / 4000)):
        bg[rng.integers(0, H2), rng.integers(0, W2)] = rng.uniform(0.3, 1.0)
    covered = np.isfinite(zbuf).reshape(H2, W2) | (img.sum(-1) > 0)
    out = np.where(covered[..., None], img, bg)
    return out, (eye, ax, ay, az, focal), zbuf.reshape(H2, W2), (W2, H2)


def add_glow(out, cam, zbuf, dims, glow, glow_tex, ss):
    eye, ax, ay, az, focal = cam
    W2, H2 = dims
    layer = np.zeros_like(out)
    for bank in glow:
        for pt in bank["pts"]:
            rel = pt[:3] - eye
            cz = float(rel @ az)
            if cz < 1:
                continue
            sx = float(rel @ ax) / cz * focal + W2 / 2
            sy = H2 / 2 - float(rel @ ay) / cz * focal
            # visible if nothing nearer covers the point's pixel (a little tolerance for the nozzle itself) and it faces us
            facing = float((eye - pt[:3]) @ pt[3:6]) > 0 if np.linalg.norm(pt[3:6]) > 0 else True
            px, py = int(sx), int(sy)
            if not (0 <= px < W2 and 0 <= py < H2):
                continue
            if zbuf[py, px] < cz - max(pt[6] * 0.8, 3.0):
                continue
            r = max(pt[6] * 2 * focal / cz, 3.0)
            fade = 1.0 if facing else 0.35
            n = int(r)
            ys, xs = np.mgrid[-n:n + 1, -n:n + 1]
            rr = np.hypot(xs, ys) / max(r / 2, 1)
            spr = np.clip(1 - rr, 0, 1) ** 1.6
            col = np.array([1.0, 0.72, 0.42], np.float32)
            if glow_tex is not None:
                gi = np.asarray(Image.fromarray((glow_tex * 255).astype(np.uint8)).resize((2 * n + 1, 2 * n + 1), Image.BILINEAR), dtype=np.float32) / 255.0
                patch = gi * 1.3 * fade
            else:
                patch = spr[..., None] * col * 1.3 * fade
            y0, y1, x0, x1 = py - n, py + n + 1, px - n, px + n + 1
            cy0, cx0 = max(0, -y0), max(0, -x0)
            y0c, x0c = max(0, y0), max(0, x0)
            y1c, x1c = min(H2, y1), min(W2, x1)
            layer[y0c:y1c, x0c:x1c] += patch[cy0:cy0 + (y1c - y0c), cx0:cx0 + (x1c - x0c)]
    # bloom: a blurred copy of the glow layer
    bl = Image.fromarray(np.clip(layer * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6 * ss))
    return np.clip(out + layer + np.asarray(bl, dtype=np.float32) / 255.0 * 0.9, 0, 1)


VIEWS = {  # yaw (0 = camera behind the model looking +z), pitch, distance factor
    "rear": (180, 12, 2.4), "front": (0, 12, 2.4), "side": (90, 8, 2.2), "top": (150, 70, 2.2), "3q": (215, 20, 2.1),
    "rear-low": (200, -25, 2.4), "closerear": (160, 8, 0.9),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pof"); ap.add_argument("out")
    ap.add_argument("--maps", action="append", default=[])
    ap.add_argument("--views", default="3q,rear,side,top")
    ap.add_argument("--size", default="960x480")
    ap.add_argument("--light", default="-0.5,0.7,-0.45")
    a = ap.parse_args()
    W, H = [int(v) for v in a.size.split("x")]
    pof = read_pof(a.pof)
    model = collect(pof)
    print("%s: %d triangles, %d submodels, %d glow banks, textures %s" % (os.path.basename(a.pof), len(model[0]), len(pof["subs"]), len(pof["glow"]), pof["textures"]))
    dirs = a.maps or [os.path.dirname(a.pof)]
    tex = load_tex(pof["textures"][0] if pof["textures"] else None, dirs)
    print("texture:", None if tex is None else tex.shape)
    gname = pof["glow"][0]["tex"] if pof["glow"] else None
    gt = load_tex(gname, dirs, 256) if gname else None
    light = [float(v) for v in a.light.split(",")]
    ss = 2
    tiles = []
    for v in a.views.split(","):
        out, cam, zb, dims = render(model, tex, gt, VIEWS.get(v) or tuple(float(x) for x in v.split(":")), W, H, light, ss=ss)
        if pof["glow"]:
            out = add_glow(out, cam, zb, dims, pof["glow"], gt, ss)
        im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
        tiles.append(im)
        print("view", v)
    cols = 2 if len(tiles) > 1 else 1
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * W, (i // cols) * H))
    sheet.save(a.out)
    print("wrote", a.out, sheet.size)


if __name__ == "__main__":
    main()
