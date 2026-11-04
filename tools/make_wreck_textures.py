#!/usr/bin/env python3
"""Procedural, seamlessly tiling hull texture for the wreck models: dark armour plating with panel seams, rivets, rust
streaks and scorching. Writes <out>/wreck_hull.png (diffuse) and wreck_hull-normal.png.
usage: make_wreck_textures.py OUTDIR [size]"""
import os, sys
import numpy as np
from PIL import Image

N = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
rng = np.random.default_rng(7)


def fnoise(beta=2.0, seed=None):
    """periodic 1/f^beta noise in [0, 1] (FFT-filtered white noise tiles by construction)"""
    r = np.random.default_rng(seed)
    f = np.fft.fftfreq(N)[:, None] ** 2 + np.fft.rfftfreq(N)[None, :] ** 2
    f[0, 0] = 1.0
    spec = (r.normal(size=f.shape) + 1j * r.normal(size=f.shape)) / f ** (beta / 2)
    spec[0, 0] = 0
    a = np.fft.irfft2(spec, s=(N, N))
    a -= a.min()
    return a / a.max()


yy, xx = np.mgrid[0:N, 0:N]
# panels: a jittered grid of plates, each with its own tone, dark seams between them
cell = N // 8
pid = (yy // cell) * 8 + (xx // cell)
tone = rng.uniform(0.75, 1.15, 64)[pid % 64]
ex = np.minimum(xx % cell, cell - 1 - xx % cell)
ey = np.minimum(yy % cell, cell - 1 - yy % cell)
edge = np.minimum(ex, ey)
seam = np.clip(1 - edge / 3.0, 0, 1)                      # 1 on the seam
# rivets along the plate edges
rv = ((xx % (cell // 4)) - cell // 8) ** 2 + ((yy % cell) - 9) ** 2
rivets = (rv < 9).astype(float) + (((yy % (cell // 4)) - cell // 8) ** 2 + ((xx % cell) - 9) ** 2 < 9)
rivets = np.clip(rivets, 0, 1)

base = 0.30 * tone * (0.75 + 0.35 * fnoise(2.4, 1) + 0.25 * fnoise(0.9, 9))
base = base * (1 - 0.6 * seam)
base += 0.05 * rivets
# rust streaks running down the plates, stronger near seams and in noisy patches
streak = fnoise(1.2, 2)
streak = np.clip((np.roll(streak, 7, axis=0) - 0.55) * 4, 0, 1) * (0.4 + 0.6 * fnoise(2.0, 3))
rust = np.clip((fnoise(2.2, 4) - 0.50) * 3.0, 0, 1) * 0.6 + streak * 0.5
rust = np.clip(rust, 0, 1)
scorch = np.clip((fnoise(1.7, 5) - 0.62) * 3.0, 0, 1) * 0.8

rgb = np.stack([base, base * 1.02, base * 1.08], -1)
rgb = rgb * (1 - rust[..., None] * 0.7) + rust[..., None] * np.array([0.34, 0.17, 0.08]) * (0.5 + 0.6 * fnoise(1.8, 6))[..., None]
rgb = rgb * (1 - scorch[..., None] * 0.75)
rgb = np.clip(rgb, 0, 1)

# normal map from a height field: seams cut in, rivets and rust crust raised
h = -0.8 * seam + 0.5 * rivets + 0.15 * fnoise(2.0, 8) + 0.1 * rust
gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 6
gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 6
nz = np.ones_like(h)
ln = np.sqrt(gx * gx + gy * gy + nz * nz)
nrm = np.stack([-gx / ln, gy / ln, nz / ln], -1) * 0.5 + 0.5

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
Image.fromarray((rgb * 255).astype(np.uint8)).save(os.path.join(out, "wreck_hull.png"))
Image.fromarray((nrm * 255).astype(np.uint8)).save(os.path.join(out, "wreck_hull-normal.png"))
print("wrote", out)
