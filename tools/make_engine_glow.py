#!/usr/bin/env python3
"""Soft round engine glow sprite (additive: black = nothing) for POF glow point banks.
usage: make_engine_glow.py out.dds [r,g,b core colour 0-255, default 110,165,255 (the blue-white of the Colonial engines); orange is 255,190,110]"""
import subprocess, sys, tempfile, os
import numpy as np
from PIL import Image

N = 128
col = np.array([float(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "110,165,255").split(",")])
y, x = np.mgrid[0:N, 0:N]
r = np.hypot(x - (N - 1) / 2, y - (N - 1) / 2) / (N / 2)
core = np.clip(1 - r, 0, 1) ** 1.6
halo = np.clip(1 - r, 0, 1) ** 3.5
white_hot = (col + 255) / 2          # the centre burns towards white, the rim keeps the colour
img = np.clip(core[..., None] * col * 0.8 + halo[..., None] * white_hot * 0.7, 0, 255).astype(np.uint8)
with tempfile.TemporaryDirectory() as w:
    p = os.path.join(w, "g.png")
    Image.fromarray(img).save(p)
    subprocess.run(["magick", p, "-define", "dds:compression=dxt1", "-define", "dds:mipmaps=7", sys.argv[1]], check=True)
print("wrote", sys.argv[1])
