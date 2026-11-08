#!/usr/bin/env python3
"""The chosen comms effect ("C1 half blend"): B8 chain (distortion -> tone EQ -> 12 kHz alias -> 60 Hz frequency-shift mix -> telephone band ->
7 ms echo -> distortion) mixed 50/50 with the clean voice. The tone EQ is derived once from the pooled recordings of the voice (against original
Diaspora lines) so every line of a voice gets the same correction.
usage: radio_final.py --voice flask --out OUTDIR [--speed 1.0] JOBS_DIR ...   (each dir holds jobs.json + the clean <id>.wav lines)"""
import argparse, glob, json, os, subprocess, tempfile, numpy as np
from scipy.signal import hilbert
from scipy.io import wavfile
ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--voice", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--speed", type=float, default=1.0); ap.add_argument("--ref", default="/tmp/wk/vo/ex/data/voice"); ap.add_argument("--match-max", type=float, default=10.0)
ap.add_argument("--dry-match", action="store_true", help="also apply the tone EQ to the clean half of the blend (for boomy / muffled source voices)")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); SR = 44100

def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def avg_spec(x, N=4096):
    n = len(x) // N * N; P = np.abs(np.fft.rfft(x[:n].reshape(-1, N) * np.hanning(N), axis=1)) ** 2
    return P[P.sum(1) > np.percentile(P.sum(1), 40)].mean(0)
CENT = [100, 160, 250, 400, 630, 1000, 1600, 2500, 4000, 6300, 9000]
def bands(P):
    fr = np.fft.rfftfreq((len(P) - 1) * 2, 1 / SR)
    return np.array([10 * np.log10(P[(fr >= c / 2 ** (1 / 3)) & (fr < c * 2 ** (1 / 3))].mean() + 1e-12) for c in CENT])
def pooled(files, cap):
    P = np.zeros(2049); k = 0
    for p in files[:cap]:
        x = load(p)
        if len(x) > 8192: P += avg_spec(x); k += 1
    return P / k
lines = []
for d in a.dirs:
    for l in json.load(open(os.path.join(d, "jobs.json")))["lines"]:
        if l.get("voice") == a.voice and os.path.exists(os.path.join(d, l["id"] + ".wav")): lines.append((l["id"], os.path.join(d, l["id"] + ".wav")))
t = bands(pooled(sorted(glob.glob(a.ref + "/**/*.ogg", recursive=True)), 120)); c = bands(pooled([p for _, p in lines], 200))
d = np.clip((t - t[5]) - (c - c[5]), -a.match_max, a.match_max)
print(len(lines), "lines; EQ dB at", CENT, np.round(d, 1))
MATCH = "firequalizer=gain_entry='%s':accuracy=5" % ";".join("entry(%d,%.1f)" % (f, g) for f, g in zip(CENT, d))
def drive(x): return "volume=%.2f,asoftclip=type=tanh,volume=%.3f" % (1 + x, 1 / (1 + x * 0.5))
def run(args): subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)
def alias(x, sr_out):
    n = len(x); m = int(n * sr_out / SR); tt = np.arange(m) * SR / sr_out
    s = x[np.minimum(np.round(tt).astype(int), n - 1)]; u = np.arange(n) * sr_out / SR
    return s[np.minimum(np.floor(u).astype(int), m - 1)]
for lid, src in lines:
    with tempfile.TemporaryDirectory() as w:
        run(["-i", src, "-af", "aresample=44100,aformat=channel_layouts=mono,highpass=f=300," + MATCH + "," + drive(2.0), "-c:a", "pcm_f32le", w + "/a.wav"])
        sr, x = wavfile.read(w + "/a.wav"); x = np.concatenate([x.astype(np.float64), np.zeros(int(0.05 * sr))])
        x = alias(x, 12000)
        y = 0.55 * x + 0.45 * np.real(hilbert(x) * np.exp(2j * np.pi * 60 * np.arange(len(x)) / sr))
        wavfile.write(w + "/b.wav", sr, y.astype(np.float32))
        post = "highpass=f=300,lowpass=f=3400,highpass=f=300,acompressor=threshold=-22dB:ratio=3:attack=4:release=80,aecho=0.9:0.6:7:0.35," + drive(0.8) + \
               ",loudnorm=I=-17:TP=-1.5:LRA=7,aresample=44100,aformat=channel_layouts=stereo,apad=pad_dur=0.1"
        run(["-i", w + "/b.wav", "-af", post, "-c:a", "pcm_f32le", w + "/wet.wav"])
        run(["-i", src, "-af", (("aresample=44100,highpass=f=120," + MATCH + ",") if a.dry_match else "") + "aresample=44100,loudnorm=I=-17:TP=-1.5:LRA=7,aresample=44100,aformat=channel_layouts=stereo,apad=pad_dur=0.1", "-c:a", "pcm_f32le", w + "/dry.wav"])
        tempo = ",atempo=%.3f" % a.speed if a.speed != 1.0 else ""
        run(["-i", w + "/wet.wav", "-i", w + "/dry.wav", "-filter_complex",
             "[0:a][1:a]amix=inputs=2:weights='1 1':normalize=0,loudnorm=I=-17:TP=-1.5:LRA=7,aresample=44100,alimiter=limit=0.89:level=disabled,aformat=channel_layouts=stereo" + tempo,
             "-c:a", "libvorbis", "-q:a", "5", os.path.join(a.out, lid + ".ogg")])
print("wrote", len(lines), "files to", a.out)
