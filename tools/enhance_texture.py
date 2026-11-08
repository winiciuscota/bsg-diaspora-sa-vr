#!/usr/bin/env python3
"""Cheap texture rescue for generated ship textures: match the colour statistics of a reference picture (the image the model
was generated from) and upscale 2x with a mild sharpen. CPU only. The GPU route (Real-ESRGAN, tools/upscale_fast.py) is better
when the GPU is free.
usage: enhance_texture.py texture.jpg reference.png out.png [--contrast 1.4] [--scale 2]"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("texture"); ap.add_argument("reference"); ap.add_argument("out")
ap.add_argument("--contrast", type=float, default=1.1, help="multiplier for the texture's own detail around its mean")
ap.add_argument("--scale", type=int, default=2)
a = ap.parse_args()

tex = np.asarray(Image.open(a.texture).convert("RGB"), dtype=np.float64)
ref_im = Image.open(a.reference).convert("RGBA")
ref = np.asarray(ref_im, dtype=np.float64)
mask = (ref[..., 3] > 200) & (ref[..., :3].min(-1) < 235) & (ref[..., :3].max(-1) > 30)   # the ship, not the white or black background
rp = ref[mask][:, :3]
t_mean, t_std = tex.reshape(-1, 3).mean(0), tex.reshape(-1, 3).std(0)
r_mean, r_std = rp.mean(0), rp.std(0)
print("texture mean/std", t_mean.round(), t_std.round(), "| reference", r_mean.round(), r_std.round())
# luminance detail of the texture keeps its structure; colour comes from the reference
lum = tex.mean(-1, keepdims=True)
detail = (lum - lum.mean()) * a.contrast
out = r_mean + (tex - t_mean) / np.maximum(t_std, 1e-6) * np.minimum(r_std, 45.0) * 0.5 + detail
out = np.clip(out, 0, 255).astype(np.uint8)
im = Image.fromarray(out)
if a.scale > 1:
    im = im.resize((im.width * a.scale, im.height * a.scale), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.5, percent=110, threshold=2))
im.save(a.out)
print("wrote", a.out, im.size)
