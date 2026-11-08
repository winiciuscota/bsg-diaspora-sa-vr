#!/usr/bin/env python3
"""(radio_alias.py) B8 chain + aliasing: the voice is sampled at a low rate WITHOUT an anti-alias filter, so everything above half the rate folds back
into the audio band as inharmonic tones.  Chain: distortion -> wide tone EQ -> alias -> frequency shift mix -> telephone band -> short echo -> distortion.
usage: radio_alias.py CLEAN.ogg OUTDIR

Original docstring: BSG-style comms variants built on a real frequency shifter (mistuned single sideband): distortion -> telephone EQ (tone matched to original
lines) -> Hilbert frequency shift (every frequency moves by the same Hz: metallic, inharmonic) -> very short reverb / phaser -> light tremolo ->
distortion -> optional static + squelch.   usage: radio_ssb.py CLEAN.ogg OUTDIR"""
import argparse, glob, os, subprocess, tempfile, numpy as np
from scipy.signal import hilbert
from scipy.io import wavfile
ap = argparse.ArgumentParser(); ap.add_argument("clean"); ap.add_argument("outdir"); ap.add_argument("--ref", default="/tmp/wk/vo/ex/data/voice")
ap.add_argument("--match-max", type=float, default=10.0); ap.add_argument("--no-match", action="store_true"); ap.add_argument("--only", default="", help="comma separated recipe name prefixes")
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
def drive(x): return "volume=%.2f,asoftclip=type=tanh,volume=%.3f" % (1 + x, 1 / (1 + x * 0.5)) if x else "anull"

# alias: sample rate in Hz (None = off), interp "hold" (sample and hold DAC) or "lin"; pre = distortion before the alias stage (makes the high band that folds back)
R = {
    "C1_b8_alias12k":   dict(d1=2.0, hp=300, lp=3400, alias=12000, interp="hold", shift=60, wet=0.45, echo="7", d2=0.8),
    "H1_c1_half_params": dict(d1=1.0, hp=300, lp=3400, alias=12000, interp="hold", shift=60, wet=0.225, echo="7", d2=0.4, awet=0.5, edecay=0.175),
    "C2_b8_alias8k":    dict(d1=2.0, hp=300, lp=3400, alias=8000,  interp="hold", shift=60, wet=0.45, echo="7", d2=0.8),
    "C3_b8_alias16k":   dict(d1=2.0, hp=300, lp=3400, alias=16000, interp="hold", shift=60, wet=0.45, echo="7", d2=0.8),
    "C4_alias10k_only": dict(d1=2.0, hp=300, lp=3400, alias=10000, interp="hold", shift=0,  wet=0.0,  echo=None, d2=0.8),
    "C5_alias10k_shift": dict(d1=2.5, hp=300, lp=3400, alias=10000, interp="hold", shift=45, wet=0.5, echo="7", d2=1.0),
    "C6_alias6k_strong": dict(d1=2.5, hp=300, lp=3400, alias=6000, interp="hold", shift=60, wet=0.45, echo="7", d2=1.0),
    "C7_alias12k_hot":  dict(d1=4.0, hp=300, lp=3400, alias=12000, interp="hold", shift=60, wet=0.45, echo="7", d2=1.0),
    "C8_alias14k_lin":  dict(d1=3.0, hp=300, lp=3400, alias=14000, interp="lin",  shift=60, wet=0.45, echo="7", d2=0.8),
}
def alias(x, sr_out, interp, sr=44100):
    n = len(x); m = int(n * sr_out / sr); t = np.arange(m) * sr / sr_out
    s = x[np.minimum(np.round(t).astype(int), n - 1)]               # point sampling, no anti-alias filter
    u = np.arange(n) * sr_out / sr
    return s[np.minimum(np.floor(u).astype(int), m - 1)] if interp == "hold" else np.interp(u, np.arange(m), s)
if a.no_match: MATCH = "anull"
R = {k: v for k, v in R.items() if not a.only or any(k.startswith(p) for p in a.only.split(","))}
def run(args): subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)
for name, r in R.items():
    with tempfile.TemporaryDirectory() as w:
        pre = ",".join(["aresample=44100,aformat=channel_layouts=mono", "highpass=f=%d" % r["hp"], MATCH, drive(r["d1"])])
        run(["-i", a.clean, "-af", pre, "-ar", "44100", "-c:a", "pcm_f32le", w + "/a.wav"])
        sr, x = wavfile.read(w + "/a.wav"); x = x.astype(np.float64)
        x = np.concatenate([x, np.zeros(int(0.05 * sr))])
        aw = r.get("awet", 1.0); x = (1 - aw) * x + aw * alias(x, r["alias"], r["interp"])
        sh = np.real(hilbert(x) * np.exp(2j * np.pi * r["shift"] * np.arange(len(x)) / sr))
        y = (1 - r["wet"]) * x + r["wet"] * sh
        wavfile.write(w + "/b.wav", sr, y.astype(np.float32))
        post = ["highpass=f=%d" % r["hp"], "lowpass=f=%d" % r["lp"], "highpass=f=%d" % r["hp"], "acompressor=threshold=-22dB:ratio=3:attack=4:release=80"]
        if r["echo"]:
            ds = r["echo"].split("|"); post.append("aecho=0.9:0.6:%s:%s" % (r["echo"], "|".join([str(r.get("edecay", 0.35)), str(r.get("edecay", 0.35) * 0.7)][:len(ds)])))
        post += [drive(r["d2"]), "loudnorm=I=-17:TP=-1.5:LRA=7,aresample=44100,aformat=channel_layouts=mono,apad=pad_dur=0.1"]
        dst = os.path.join(a.outdir, name + ".ogg")
        if False:
            click = "anoisesrc=d=0.045:c=white:a=0.05:r=44100,highpass=f=1500,lowpass=f=5000,afade=t=out:d=0.045"
            g = "[0:a]%s[v];[1:a]highpass=f=250,lowpass=f=4200[nz];[v][nz]amix=inputs=2:duration=first:normalize=0[m];[2:a][m][3:a]concat=n=3:v=0:a=1,aformat=channel_layouts=stereo[out]" % ",".join(post)
            run(["-i", w + "/b.wav", "-f", "lavfi", "-i", "anoisesrc=d=12:c=pink:a=0.012:r=44100", "-f", "lavfi", "-i", click, "-f", "lavfi", "-i", click,
                 "-filter_complex", g, "-map", "[out]", "-c:a", "libvorbis", "-q:a", "5", dst])
        else:
            run(["-i", w + "/b.wav", "-filter_complex", "[0:a]%s,aformat=channel_layouts=stereo[out]" % ",".join(post), "-map", "[out]", "-c:a", "libvorbis", "-q:a", "5", dst])
    print("wrote", name)
