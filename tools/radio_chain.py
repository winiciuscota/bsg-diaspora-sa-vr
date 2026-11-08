#!/usr/bin/env python3
"""BSG-style comms chain variants: light distortion -> telephone EQ -> ring modulation -> fast tremolo -> light distortion.
usage: radio_chain.py CLEAN.ogg OUTDIR   (tone-match EQ against original Diaspora lines as in radio_lab.py, then the chain)"""
import argparse, glob, os, subprocess, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("clean"); ap.add_argument("outdir"); ap.add_argument("--ref", default="/tmp/wk/vo/ex/data/voice")
ap.add_argument("--match-max", type=float, default=10.0)
a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True); SR = 44100

def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def avg_spec(x, N=4096):
    n = len(x) // N * N; P = np.abs(np.fft.rfft(x[:n].reshape(-1, N) * np.hanning(N), axis=1)) ** 2
    return P[P.sum(1) > np.percentile(P.sum(1), 40)].mean(0)
CENT = [100, 160, 250, 400, 630, 1000, 1600, 2500, 4000, 6300, 9000]
def bands(P):
    fr = np.fft.rfftfreq((len(P) - 1) * 2, 1 / SR)
    return np.array([10 * np.log10(P[(fr >= c / 2 ** (1 / 3)) & (fr < c * 2 ** (1 / 3))].mean() + 1e-12) for c in CENT])
ref = np.zeros(2049); k = 0
for p in sorted(glob.glob(a.ref + "/**/*.ogg", recursive=True))[:120]:
    x = load(p)
    if len(x) > 8192: ref += avg_spec(x); k += 1
t, c = bands(ref / k), bands(avg_spec(load(a.clean)))
d = np.clip((t - t[5]) - (c - c[5]), -a.match_max, a.match_max)
MATCH = "firequalizer=gain_entry='%s':accuracy=5" % ";".join("entry(%d,%.1f)" % (f, g) for f, g in zip(CENT, d))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.clean], capture_output=True, text=True).stdout)
D = dur + 1.0

# drive1 / drive2: tanh soft clip amount; hp/lp: telephone band; ring: carrier Hz and wet share; trem: rate Hz and depth
R = {
    "A1_gentle":        dict(d1=1.0, hp=300, lp=3400, ring=50,  wet=0.25, tf=14, td=0.25, d2=0.8, extra=None),
    "A2_metallic_90":   dict(d1=1.2, hp=300, lp=3400, ring=90,  wet=0.30, tf=18, td=0.30, d2=1.0, extra=None),
    "A3_phasey_30":     dict(d1=1.2, hp=320, lp=3300, ring=30,  wet=0.35, tf=10, td=0.35, d2=1.0, extra=None),
    "A4_robot_120":     dict(d1=1.0, hp=300, lp=3500, ring=120, wet=0.25, tf=20, td=0.20, d2=0.8, extra=None),
    "A5_strong":        dict(d1=1.8, hp=350, lp=3200, ring=60,  wet=0.40, tf=16, td=0.40, d2=1.5, extra=None),
    "A6_with_static":   dict(d1=1.2, hp=300, lp=3400, ring=90,  wet=0.30, tf=18, td=0.30, d2=1.0, extra="static"),
    "A7_tight_slowtrem": dict(d1=1.5, hp=400, lp=2800, ring=70, wet=0.30, tf=8,  td=0.30, d2=1.2, extra=None),
    "A8_fast_flutter":  dict(d1=1.2, hp=300, lp=3400, ring=80,  wet=0.30, tf=28, td=0.35, d2=1.0, extra=None),
}
def drive(x): return "volume=%.2f,asoftclip=type=tanh,volume=%.3f" % (1 + x, 1 / (1 + x * 0.5)) if x else "anull"
for name, r in R.items():
    chain = ["[0:a]aresample=44100,aformat=channel_layouts=mono", drive(r["d1"]), "highpass=f=%d" % r["hp"], MATCH, "lowpass=f=%d" % r["lp"],
             "highpass=f=%d" % r["hp"], "acompressor=threshold=-22dB:ratio=3:attack=4:release=80,aresample=44100"]
    g = [",".join(chain) + ",asplit=2[dry][wetin]",
         "sine=f=%d:r=44100:d=%.2f[car]" % (r["ring"], D),
         "[wetin][car]amultiply,volume=2.0[rm]",
         "[dry][rm]amix=inputs=2:weights='%.2f %.2f':normalize=0[mix]" % (1 - r["wet"], r["wet"] * 1.6),
         "[mix]tremolo=f=%d:d=%.2f,%s,loudnorm=I=-17:TP=-1.5:LRA=7,aresample=44100,aformat=channel_layouts=mono,apad=pad_dur=0.1[v]" % (r["tf"], r["td"], drive(r["d2"]))]
    inputs = ["-i", a.clean]
    if r["extra"] == "static":
        click = "anoisesrc=d=0.045:c=white:a=0.05:r=44100,highpass=f=1500,lowpass=f=5000,afade=t=out:d=0.045"
        inputs += ["-f", "lavfi", "-i", "anoisesrc=d=%.2f:c=pink:a=0.012:r=44100" % D, "-f", "lavfi", "-i", click, "-f", "lavfi", "-i", click]
        g.append("[1:a]highpass=f=250,lowpass=f=4200[nz]"); g.append("[v][nz]amix=inputs=2:duration=first:normalize=0[m]")
        g.append("[2:a][m][3:a]concat=n=3:v=0:a=1[o]")
    else:
        g.append("[v]anull[o]")
    g.append("[o]aformat=channel_layouts=stereo[out]")
    dst = os.path.join(a.outdir, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(g), "-map", "[out]", "-c:a", "libvorbis", "-q:a", "5", dst], check=True)
    print("wrote", name)
