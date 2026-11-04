#!/usr/bin/env python3
"""Adds a textured glb (from the assetgen queue) to the mod as a static ship class: model (glb2pof.py), DXT1 texture with mips,
and a modular ship table <pof>-shp.tbm.
usage: add_glb_ship.py in.glb --class "Tylium Refinery" --short Tyl_Refinery --pof tyl_refinery --length 1100 [--axes x,z,y]"""
import argparse, math, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "overlay", "diaspora_fixes", "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_wrecks import TBM_HEAD, TBM_SHIP

ap = argparse.ArgumentParser()
ap.add_argument("glb")
ap.add_argument("--class", dest="cls", required=True)
ap.add_argument("--short", required=True)
ap.add_argument("--pof", required=True)
ap.add_argument("--length", type=float, required=True)
ap.add_argument("--axes", default="auto")
ap.add_argument("--flip-front", action="store_true")
a = ap.parse_args()

tex = a.pof + "_hull"
os.makedirs(os.path.join(DATA, "models"), exist_ok=True)
os.makedirs(os.path.join(DATA, "maps"), exist_ok=True)
with tempfile.TemporaryDirectory() as w:
    img = os.path.join(w, tex + ".jpg")
    cmd = [sys.executable, os.path.join(ROOT, "tools", "glb2pof.py"), a.glb, os.path.join(DATA, "models", a.pof + ".pof"),
           "--texture", tex, "--length", str(a.length), "--axes", a.axes, "--image", img, "--faces-per-part", "8000"]
    if a.flip_front:
        cmd.append("--flip-front")
    subprocess.run(cmd, check=True)
    from PIL import Image
    wd, ht = Image.open(img).size
    subprocess.run(["magick", img, "-define", "dds:compression=dxt1", "-define", "dds:mipmaps=%d" % int(math.log2(max(wd, ht))),
                    os.path.join(DATA, "maps", tex + ".dds")], check=True)
rad = a.length / 2
tbm = TBM_HEAD + TBM_SHIP.format(cls=a.cls, short=a.short, pof=a.pof + ".pof", rad=rad * 0.5, rad2=rad, hp=2000000,
                                 close=a.length * 1.6) + "#End\n"
open(os.path.join(DATA, "tables", a.pof + "-shp.tbm"), "w").write(tbm)
print("added", a.cls, "->", a.pof + ".pof,", tex + ".dds,", a.pof + "-shp.tbm")
